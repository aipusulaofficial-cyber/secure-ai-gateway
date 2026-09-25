"""Secure AI gateway policy core: authentication, quotas and content controls."""
from dataclasses import dataclass
import time


class GatewayDenied(Exception):
    """Raised when a request violates an enforced gateway policy."""


@dataclass(frozen=True)
class Request:
    principal: str
    text: str
    request_id: str


class Policy:
    def __init__(self, blocked=None, max_chars=4000):
        self.blocked = blocked or ["ignore previous instructions", "exfiltrate"]
        self.max_chars = max_chars

    def check(self, request: Request):
        if not request.principal:
            raise GatewayDenied("unauthenticated")
        if len(request.text) > self.max_chars:
            raise GatewayDenied("payload too large")
        if any(term in request.text.lower() for term in self.blocked):
            raise GatewayDenied("policy blocked")
        return True


class RateLimiter:
    def __init__(self, limit=10, window=60):
        self.limit = limit
        self.window = window
        self.hits = {}

    def allow(self, key, now=None):
        now = time.monotonic() if now is None else now
        queue = [t for t in self.hits.get(key, []) if now - t < self.window]
        if len(queue) >= self.limit:
            return False
        queue.append(now)
        self.hits[key] = queue
        return True


class Gateway:
    def __init__(self, policy=None, limiter=None):
        self.policy = policy or Policy()
        self.limiter = limiter or RateLimiter()

    def authorize(self, request: Request, now=None):
        self.policy.check(request)
        if not self.limiter.allow(request.principal, now):
            raise GatewayDenied("rate limit exceeded")
        return {"request_id": request.request_id, "decision": "allow"}


if __name__ == "__main__":
    print(Gateway().authorize(Request("demo", "hello", "r1")))
