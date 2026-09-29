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
