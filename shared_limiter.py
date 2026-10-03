"""Atomic fleet-wide rate limiting using Redis server time."""

import hashlib
from functools import lru_cache
from uuid import uuid4

from redis import Redis

# EVAL is atomic within one Redis shard; every key uses one fixed hash tag.
_SCRIPT = """
local t = redis.call('TIME')
local now = tonumber(t[1]) * 1000 + math.floor(tonumber(t[2]) / 1000)
local window = tonumber(ARGV[1])
local limit = tonumber(ARGV[2])
redis.call('ZREMRANGEBYSCORE', KEYS[1], '-inf', now - window)
if redis.call('ZCARD', KEYS[1]) >= limit then
  redis.call('PEXPIRE', KEYS[1], window)
  return 0
end
redis.call('ZADD', KEYS[1], now, ARGV[3])
redis.call('PEXPIRE', KEYS[1], window)
return 1
"""


class RedisSlidingLimiter:
    def __init__(self, client: Redis, limit: int = 60, window_ms: int = 60000):
        if limit < 1 or window_ms < 1:
            raise ValueError("invalid shared limiter configuration")
        self.client, self.limit, self.window_ms = client, limit, window_ms

    def ping(self) -> bool:
        return bool(self.client.ping())

    def allow(self, subject: str) -> bool:
        if not subject or not subject.strip():
            raise ValueError("verified subject required")
        key = "gateway:{rate}:" + hashlib.sha256(subject.encode("utf-8")).hexdigest()
        nonce = uuid4().hex
        return bool(self.client.eval(_SCRIPT, 1, key, self.window_ms, self.limit, nonce))


@lru_cache(maxsize=4)
def configured_limiter(url: str) -> RedisSlidingLimiter:
    client = Redis.from_url(url, socket_connect_timeout=0.3, socket_timeout=0.3)
    return RedisSlidingLimiter(client)
