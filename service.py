import os
import time

import jwt
from fastapi import FastAPI, HTTPException
from fastapi import Request as FastAPIRequest
from opentelemetry import trace
from pydantic import BaseModel, Field
from redis.exceptions import RedisError

from gateway_domain import RateLimiter, authorize
from observability import PrincipalObservabilityMiddleware, configure_observability, get_logger
from runtime_evidence import request_id_from_headers, runtime_evidence
from shared_limiter import configured_limiter

configure_observability()
logger = get_logger(__name__)
rate_limiter = RateLimiter(limit=60, window_s=60.0)
app = FastAPI(title="secure-ai-gateway", version="1.0.0")
app.add_middleware(PrincipalObservabilityMiddleware)
tracer = trace.get_tracer("secure-ai-gateway")


class Request(BaseModel):
    key: str = Field(min_length=1, max_length=128)
    payload: dict = Field(default_factory=dict, max_length=32)


@app.get("/health/live")
def live():
    return {"status": "ok"}


@app.get("/health/ready")
def ready():
    if not os.getenv("AI_GATEWAY_JWT_SECRET"):
        raise HTTPException(status_code=503, detail="authentication_not_configured")
    if os.getenv("AI_GATEWAY_REQUIRE_SHARED_LIMITER") == "1":
        url = os.getenv("AI_GATEWAY_REDIS_URL")
        if not url:
            raise HTTPException(status_code=503, detail="shared_limiter_not_configured")
        try:
            if not configured_limiter(url).ping():
                raise HTTPException(status_code=503, detail="shared_limiter_unavailable")
        except RedisError as exc:
            raise HTTPException(status_code=503, detail="shared_limiter_unavailable") from exc
    return {"status": "ready"}


def enforce_shared_quota(token: str) -> None:
    url = os.getenv("AI_GATEWAY_REDIS_URL")
    secret = os.getenv("AI_GATEWAY_JWT_SECRET")
    if not url or not secret:
        raise HTTPException(status_code=503, detail="shared_limiter_not_configured")
    claims = jwt.decode(
        token.removeprefix("Bearer ").strip(),
        secret,
        algorithms=["HS256"],
        options={"require": ["sub", "exp"]},
    )
    subject = claims.get("sub")
    if not isinstance(subject, str) or not subject.strip():
        raise HTTPException(status_code=401, detail="invalid_credentials")
    try:
        allowed = configured_limiter(url).allow(subject)
    except RedisError as exc:
        raise HTTPException(status_code=503, detail="shared_limiter_unavailable") from exc
    if not allowed:
        raise HTTPException(status_code=429, detail="shared_quota_exceeded")


@app.post("/v1/gateway")
def handle(request: Request, http_request: FastAPIRequest):
    started = time.perf_counter()
    request_id = request_id_from_headers(http_request.headers)
    if (
        os.getenv("AI_GATEWAY_REQUIRE_SHARED_LIMITER") != "1"
        and not rate_limiter.allow(request.key)
    ):
        evidence = runtime_evidence(
            request_id=request_id,
            stage="gateway.rate_limit",
            decision="DENY",
            started=started,
            error="rate limit exceeded",
        )
        raise HTTPException(
            status_code=429,
            detail={"error": "rate limit exceeded", "evidence": evidence},
        )
    with tracer.start_as_current_span("secure-ai-gateway.authorize"):
        try:
            decision = authorize(
                request.payload.get("token", ""),
                request.payload.get("scope", "inference"),
            )
            if os.getenv("AI_GATEWAY_REQUIRE_SHARED_LIMITER") == "1" and decision.allowed:
                enforce_shared_quota(request.payload.get("token", ""))
            logger.info(
                "gateway_decision key=%s allowed=%s reason=%s",
                request.key,
                decision.allowed,
                decision.reason,
            )
            return {
                "allowed": decision.allowed,
                "reason": decision.reason,
                "evidence": runtime_evidence(
                    request_id=request_id,
                    stage="gateway.authorize",
                    decision="ALLOW" if decision.allowed else "DENY",
                    started=started,
                    error=None if decision.allowed else decision.reason,
                ),
            }
        except (ValueError, KeyError, TypeError) as exc:
            evidence = runtime_evidence(
                request_id=request_id,
                stage="gateway.authorize",
                decision="DENY",
                started=started,
                error=str(exc),
            )
            raise HTTPException(
                status_code=400,
                detail={"error": str(exc), "evidence": evidence},
            ) from exc
