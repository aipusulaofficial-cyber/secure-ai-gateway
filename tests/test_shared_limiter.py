from shared_limiter import RedisSlidingLimiter


def test_invalid_limit():
    import pytest
    with pytest.raises(ValueError):
        RedisSlidingLimiter(None, limit=0)
