import jwt
import pytest

from gateway_domain import RateLimiter, authorize

SECRET = "test-secret"


def token(scope: str = "inference") -> str:
    return jwt.encode(
        {"sub": "test-user", "exp": 4102444800, "scope": scope},
        SECRET,
        algorithm="HS256",
    )


def test_authorization_and_rate_limit(monkeypatch):
    monkeypatch.setenv("AI_GATEWAY_JWT_SECRET", SECRET)
    assert authorize(f"Bearer {token()}", "inference").allowed
    assert not authorize(f"Bearer {token('other')}", "inference").allowed
    limiter = RateLimiter(1)
    assert limiter.allow("k", 0)
    assert not limiter.allow("k", 1)


def test_authorization_requires_bearer():
    assert authorize("inference", "inference").reason == "missing_credentials"


@pytest.mark.parametrize("limit,window", [(0, 60), (1, 0)])
def test_rate_limiter_rejects_invalid_configuration(limit, window):
    with pytest.raises(ValueError):
        RateLimiter(limit, window)
