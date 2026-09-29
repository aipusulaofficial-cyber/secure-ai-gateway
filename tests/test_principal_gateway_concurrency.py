from concurrent.futures import ThreadPoolExecutor

import jwt
import pytest

from gateway_domain import RateLimiter, authorize


def test_concurrent_requests_cannot_exceed_limit():
    limiter = RateLimiter(limit=10, window_s=60)
    with ThreadPoolExecutor(max_workers=32) as pool:
        results = list(pool.map(lambda _: limiter.allow("tenant-a", now=100.0), range(200)))
    assert sum(results) == 10
    assert not limiter.allow("tenant-a", now=100.0)
    assert limiter.allow("tenant-a", now=161.0)


@pytest.mark.parametrize("clock", [float("nan"), float("inf")])
def test_invalid_clock_rejected(clock):
    with pytest.raises(ValueError):
        RateLimiter(1).allow("tenant-a", now=clock)


def test_malformed_scope_claim_fails_closed(monkeypatch):
    monkeypatch.setenv("AI_GATEWAY_JWT_SECRET", "unit-test-secret")
    token = jwt.encode(
        {"sub": "user", "exp": 4102444800, "scope": 123},
        "unit-test-secret",
        algorithm="HS256",
    )
    decision = authorize("Bearer " + token, "read")
    assert not decision.allowed
    assert decision.reason == "invalid_credentials"
