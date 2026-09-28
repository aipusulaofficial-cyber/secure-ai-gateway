"""Small, deterministic failure-injection checks for runtime guard behavior."""

from __future__ import annotations


def bounded_retry(attempts: int, max_attempts: int) -> str:
    if attempts < 0 or max_attempts < 1:
        raise ValueError("invalid retry configuration")
    return "RETRY" if attempts < max_attempts else "FAIL"


def admission(healthy: bool, authorized: bool, quota_ok: bool) -> str:
    return "ALLOW" if healthy and authorized and quota_ok else "DENY"


def run_failure_matrix() -> dict:
    return {
        "timeout": bounded_retry(0, 2),
        "backend_unavailable": admission(False, True, True),
        "unauthorized": admission(True, False, True),
        "quota_exhausted": admission(True, True, False),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(run_failure_matrix(), indent=2))
