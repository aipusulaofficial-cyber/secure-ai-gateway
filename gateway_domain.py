from dataclasses import dataclass
import time


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str


class RateLimiter:
    def __init__(self, limit: int, window_s: float = 60.0) -> None:
        if limit < 1 or window_s <= 0:
            raise ValueError("invalid rate limiter configuration")
        self.limit = limit
        self.window_s = window_s
        self._hits: dict[str, list[float]] = {}

    def allow(self, key: str, now: float | None = None) -> bool:
        if not key:
            raise ValueError("rate limit key is required")
        current = time.monotonic() if now is None else now
        hits = [
            timestamp
            for timestamp in self._hits.get(key, [])
            if current - timestamp < self.window_s
        ]
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
    scopes = {scope.strip() for scope in token[7:].split(",") if scope.strip()}
    allowed = required_scope in scopes
    return Decision(allowed, "ok" if allowed else "insufficient_scope")
