from fastapi import FastAPI, HTTPException
from opentelemetry import trace
from pydantic import BaseModel, Field

from gateway_domain import RateLimiter, authorize
from observability import configure_observability, get_logger, PrincipalObservabilityMiddleware

configure_observability()
logger = get_logger(__name__)
rate_limiter = RateLimiter(limit=60, window_s=60.0)

app = FastAPI(title="secure-ai-gateway", version="1.0.0")
app.add_middleware(PrincipalObservabilityMiddleware)
tracer = trace.get_tracer("secure-ai-gateway")


class Request(BaseModel):
    key: str
    payload: dict = Field(default_factory=dict)


@app.get("/health/live")
def live() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/ready")
def ready() -> dict[str, str]:
    return {"status": "ready"}


@app.post("/v1/gateway")
def handle(request: Request) -> dict[str, bool | str]:
    if not rate_limiter.allow(request.key):
        raise HTTPException(status_code=429, detail="rate limit exceeded")
    with tracer.start_as_current_span("secure-ai-gateway.authorize"):
        try:
            decision = authorize(
                request.payload.get("token", ""),
                request.payload.get("scope", "inference"),
            )
            logger.info(
                "gateway_decision key=%s allowed=%s reason=%s",
                request.key,
                decision.allowed,
                decision.reason,
            )
            return {"allowed": decision.allowed, "reason": decision.reason}
        except (ValueError, KeyError, TypeError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
