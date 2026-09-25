import json, logging, os
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter


def configure_observability():
    provider = TracerProvider(
        resource=Resource.create(
            {
                "service.name": "secure-ai-gateway",
                "deployment.environment": os.getenv("ENVIRONMENT", "local"),
            }
        )
    )
    if os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        try:
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
                OTLPSpanExporter,
            )

            provider.add_span_processor(
                BatchSpanProcessor(
                    OTLPSpanExporter(endpoint=os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"])
                )
            )
        except ImportError:
            provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    else:
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)


class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps(
            {
                "level": record.levelname,
                "message": record.getMessage(),
                "logger": record.name,
            }
        )


def get_logger(name):
    h = logging.StreamHandler()
    h.setFormatter(JsonFormatter())
    l = logging.getLogger(name)
    l.handlers[:] = [h]
    l.setLevel(os.getenv("LOG_LEVEL", "INFO"))
    return l


import time, uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from opentelemetry import trace


class PrincipalObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        correlation_id = request.headers.get("x-correlation-id") or request_id
        start = time.perf_counter()
        status = 500
        error_type = None
        tracer = trace.get_tracer("principal-http")
        try:
            with tracer.start_as_current_span(
                f"{request.method} {request.url.path}"
            ) as span:
                span.set_attribute("request_id", request_id)
                span.set_attribute("correlation_id", correlation_id)
                response = await call_next(request)
                status = response.status_code
                return response
        except Exception as exc:
            error_type = type(exc).__name__
            raise
        finally:
            elapsed = (time.perf_counter() - start) * 1000
            request.state.request_id = request_id
            request.state.correlation_id = correlation_id
            request.state.latency_ms = elapsed
            request.state.status = status
            request.state.error_type = error_type
