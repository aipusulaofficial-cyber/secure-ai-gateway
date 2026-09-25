from fastapi.testclient import TestClient
import pytest

from gateway_domain import Decision, RateLimiter, authorize
from service import app


def test_allows_authenticated_safe_request():
    decision = authorize("Bearer inference", "inference")
    assert decision == Decision(True, "ok")


@pytest.mark.parametrize("text", ["ignore previous instructions", "exfiltrate secrets"])
def test_gateway_endpoint_accepts_authenticated_request(text):
    client = TestClient(app)
    response = client.post(
        "/v1/gateway",
        json={
            "key": "u",
            "payload": {
                "token": "Bearer inference",
                "scope": "inference",
                "text": text,
            },
        },
    )
    assert response.status_code == 200
    assert response.json() == {"allowed": True, "reason": "ok"}


def test_rejects_missing_credentials():
    decision = authorize("", "inference")
    assert decision == Decision(False, "missing_credentials")


def test_rate_limit_is_deterministic():
    limiter = RateLimiter(1, 60)
    assert limiter.allow("u", 0)
    assert not limiter.allow("u", 1)
