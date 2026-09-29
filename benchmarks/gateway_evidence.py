import json
import os
from pathlib import Path
import sys

import jwt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gateway_domain import RateLimiter, authorize

os.environ["AI_GATEWAY_JWT_SECRET"] = "evidence-secret"
token = jwt.encode(
    {"sub": "evidence-user", "exp": 4102444800, "scope": "inference"},
    "evidence-secret",
    algorithm="HS256",
)

authorized = authorize(f"Bearer {token}", "inference")
denied = authorize(f"Bearer {token}", "admin")
missing = authorize("not-a-bearer", "inference")

limiter = RateLimiter(2, 10)
rate_results = [limiter.allow("client", now=0), limiter.allow("client", now=1), limiter.allow("client", now=2)]

report = {
    "authorized": authorized.allowed,
    "authorized_reason": authorized.reason,
    "scope_denied": not denied.allowed,
    "scope_denied_reason": denied.reason,
    "missing_credentials": missing.reason == "missing_credentials",
    "rate_limit_sequence": rate_results,
}
if report != {
    "authorized": True,
    "authorized_reason": "ok",
    "scope_denied": True,
    "scope_denied_reason": "insufficient_scope",
    "missing_credentials": True,
    "rate_limit_sequence": [True, True, False],
}:
    raise SystemExit(report)
print(json.dumps(report, sort_keys=True))
