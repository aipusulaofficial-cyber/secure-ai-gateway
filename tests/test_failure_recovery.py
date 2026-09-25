from fastapi.testclient import TestClient
from service import app
def test_rate_limit_returns_429_after_budget():
 c=TestClient(app)
 for _ in range(60): assert c.post("/v1/gateway",json={"key":"rate-test","payload":{"token":"Bearer inference","scope":"inference"}}).status_code==200
 assert c.post("/v1/gateway",json={"key":"rate-test","payload":{"token":"Bearer inference","scope":"inference"}}).status_code==429