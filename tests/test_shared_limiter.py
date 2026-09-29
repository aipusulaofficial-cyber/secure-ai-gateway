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

def test_strict_gateway_quota_uses_verified_jwt_subject(monkeypatch):
    import jwt
    from fastapi.testclient import TestClient
    from service import app

    subjects = []

    class StubLimiter:
        def allow(self, subject):
            subjects.append(subject)
            return len(subjects) <= 1

    monkeypatch.setenv("AI_GATEWAY_JWT_SECRET", "integration-secret")
    monkeypatch.setenv("AI_GATEWAY_REQUIRE_SHARED_LIMITER", "1")
    monkeypatch.setenv("AI_GATEWAY_REDIS_URL", "redis://unused")
    monkeypatch.setattr("service.configured_limiter", lambda url: StubLimiter())
    token = jwt.encode(
        {"sub": "verified-principal", "scope": "inference", "exp": 4102444800},
        "integration-secret", algorithm="HS256",
    )
    client = TestClient(app)
    payload = {"token": f"Bearer {token}", "scope": "inference"}
    assert client.post("/v1/gateway", json={"key": "spoof-a", "payload": payload}).status_code == 200
    assert client.post("/v1/gateway", json={"key": "spoof-b", "payload": payload}).status_code == 429
    assert subjects == ["verified-principal", "verified-principal"]
