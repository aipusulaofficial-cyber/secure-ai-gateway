import time

from fastapi import FastAPI, HTTPException
from fastapi import Request as FastAPIRequest
from opentelemetry import trace
from pydantic import BaseModel, Field

from gateway_domain import RateLimiter, authorize
from observability import PrincipalObservabilityMiddleware, configure_observability, get_logger
from runtime_evidence import request_id_from_headers, runtime_evidence
configure_observability()
logger = get_logger(__name__)
rate_limiter = RateLimiter(limit=60, window_s=60.0)
app = FastAPI(title="secure-ai-gateway", version="1.0.0")
app.add_middleware(PrincipalObservabilityMiddleware)
tracer = trace.get_tracer("secure-ai-gateway")
