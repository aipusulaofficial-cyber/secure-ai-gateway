import jwt

from gateway_domain import authorize


def test_malformed_scope_claim_fails_closed(monkeypatch):
    monkeypatch.setenv("AI_GATEWAY_JWT_SECRET", "test-secret")
    token = jwt.encode(
        {"sub": "agent", "scope": 7, "exp": 4102444800}, "test-secret", algorithm="HS256"
    )
    decision = authorize(f"Bearer {token}", "model:write")
    assert not decision.allowed
    assert decision.reason == "invalid_credentials"


def test_blank_subject_fails_closed(monkeypatch):
    monkeypatch.setenv("AI_GATEWAY_JWT_SECRET", "test-secret")
    token = jwt.encode(
        {"sub": " ", "scope": "model:write", "exp": 4102444800},
        "test-secret",
        algorithm="HS256",
    )
    assert not authorize(f"Bearer {token}", "model:write").allowed


def test_header_request_id_validation():
    from uuid import UUID

    from runtime_evidence import request_id_from_headers

    assert request_id_from_headers({"x-request-id": "valid-123"}) == "valid-123"
    for value in ("", "unsafe\nvalue", "x" * 129, " space "):
        actual = request_id_from_headers({"x-request-id": value})
        assert actual != value
        UUID(actual)


def test_rate_limit_refuses_backward_and_nonfinite_clock():
    import pytest

    from gateway_domain import RateLimiter

    limiter = RateLimiter(limit=2, window_s=5.0)
    assert limiter.allow("client", now=10.0)
    with pytest.raises(ValueError):
        limiter.allow("client", now=9.0)
    with pytest.raises(ValueError):
        limiter.allow("client", now=float("nan"))
    assert limiter.allow("client", now=10.1)
    assert not limiter.allow("client", now=10.2)


def test_rate_limit_parallel_calls_are_atomic():
    from concurrent.futures import ThreadPoolExecutor

    from gateway_domain import RateLimiter

    limiter = RateLimiter(limit=5)
    with ThreadPoolExecutor(max_workers=16) as executor:
        outcomes = list(executor.map(lambda _: limiter.allow("shared"), range(100)))
    assert outcomes.count(True) == 5


def test_readiness_fails_closed_without_jwt_verification_key(monkeypatch):
    from fastapi.testclient import TestClient

    from service import app

    monkeypatch.delenv("AI_GATEWAY_JWT_SECRET", raising=False)
    client = TestClient(app)
    assert client.get("/health/live").status_code == 200
    response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json()["detail"] == "authentication_not_configured"


def test_readiness_succeeds_with_jwt_verification_key(monkeypatch):
    from fastapi.testclient import TestClient

    from service import app

    monkeypatch.setenv("AI_GATEWAY_JWT_SECRET", "test-key")
    response = TestClient(app).get("/health/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"
