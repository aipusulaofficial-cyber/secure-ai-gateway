import math
import os
import time
from dataclasses import dataclass
from threading import RLock

import jwt


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str


class RateLimiter:
    def __init__(self, limit: int, window_s: float = 60.0) -> None:
        if limit < 1 or not math.isfinite(window_s) or window_s <= 0:
            raise ValueError("invalid rate limiter configuration")
        self.limit = limit
        self.window_s = window_s
        self._hits: dict[str, list[float]] = {}
        self._lock = RLock()

    def allow(self, key: str, now: float | None = None) -> bool:
        if not isinstance(key, str) or not key.strip():
            raise ValueError("rate limit key is required")
        current = time.monotonic() if now is None else now
        if not math.isfinite(current):
            raise ValueError("rate limit clock must be finite")
        with self._lock:
            previous = self._hits.get(key, [])
            if previous and current < previous[-1]:
                raise ValueError("rate limit clock must not go backwards")
            hits = [t for t in previous if current - t < self.window_s]
            if len(hits) >= self.limit:
                self._hits[key] = hits
                return False
            hits.append(current)
            self._hits[key] = hits
            return True


def authorize(token: str, required_scope: str) -> Decision:
    if not token or not token.startswith("Bearer "):
        return Decision(False, "missing_credentials")
    if not required_scope.strip():
        raise ValueError("required scope is required")
    secret = os.getenv("AI_GATEWAY_JWT_SECRET")
    if not secret:
        return Decision(False, "authentication_not_configured")
    try:
        claims = jwt.decode(
            token[7:].strip(),
            secret,
            algorithms=["HS256"],
            options={"require": ["sub", "exp"]},
        )
    except jwt.PyJWTError:
        return Decision(False, "invalid_credentials")
    subject = claims.get("sub")
    if not isinstance(subject, str) or not subject.strip():
        return Decision(False, "invalid_credentials")
    raw_scopes = claims.get("scope", "")
    if not isinstance(raw_scopes, str):
        return Decision(False, "invalid_credentials")
    scopes = set(raw_scopes.split())
    allowed = required_scope in scopes
    return Decision(allowed, "ok" if allowed else "insufficient_scope")
