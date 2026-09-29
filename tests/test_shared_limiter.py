from shared_limiter import RedisSlidingLimiter


def test_invalid_limit():
    import pytest
    with pytest.raises(ValueError):
        RedisSlidingLimiter(None, limit=0)


def test_shared_quota_across_distinct_clients():
    import os
    from concurrent.futures import ThreadPoolExecutor
    from uuid import uuid4

    import pytest
    from redis import Redis

    url = os.environ.get("REDIS_TEST_URL")
    if not url:
        pytest.skip("Redis integration service unavailable")
    first = RedisSlidingLimiter(Redis.from_url(url), limit=5)
    second = RedisSlidingLimiter(Redis.from_url(url), limit=5)
    principal = uuid4().hex
    assert first.ping() and second.ping()
    with ThreadPoolExecutor(max_workers=12) as pool:
        accepted = list(pool.map(
            lambda n: (first if n % 2 else second).allow(principal), range(40)
        ))
    assert accepted.count(True) == 5
    assert not second.allow(principal)
    assert first.allow(uuid4().hex)
