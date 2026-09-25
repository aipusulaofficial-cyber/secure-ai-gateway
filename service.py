from fastapi import FastAPI
from pydantic import BaseModel
from opentelemetry import trace
try:
 from opentelemetry.sdk.resources import Resource
 from opentelemetry.sdk.trace import TracerProvider
 from opentelemetry.sdk.trace.export import BatchSpanProcessor,ConsoleSpanExporter
 p=TracerProvider(resource=Resource.create({"service.name":"secure-ai-gateway"}));p.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()));trace.set_tracer_provider(p)
except Exception: pass
app=FastAPI(title="secure-ai-gateway",version="1.0.0");tracer=trace.get_tracer("secure-ai-gateway")
class Request(BaseModel): key:str; payload:dict={}
@app.get("/health/live")
def live():return {"status":"ok"}
@app.get("/health/ready")
def ready():return {"status":"ready"}
@app.post("/v1/gateway")
def handle(r:Request):
 with tracer.start_as_current_span("gateway") as s:s.set_attribute("request.key",r.key)
 return {"status":"accepted","key":r.key}
