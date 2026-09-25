import pytest

from gateway_domain import RateLimiter, authorize


def test_authorization_and_rate_limit():
    assert authorize("Bearer inference", "inference").allowed
    assert not authorize("Bearer other", "inference").allowed
    limiter = RateLimiter(1)
    assert limiter.allow("k", 0)
    assert not limiter.allow("k", 1)


def test_authorization_requires_bearer():
    assert authorize("inference", "inference").reason == "missing_credentials"


@pytest.mark.parametrize("limit,window", [(0, 60), (1, 0)])
def test_rate_limiter_rejects_invalid_configuration(limit, window):
    with pytest.raises(ValueError):
        RateLimiter(limit, window)
