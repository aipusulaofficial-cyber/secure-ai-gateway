"""Fail-closed AI admission decision."""

REQUIRED = (
    "authenticated",
    "authorized",
    "rate_limited",
    "ai_policy",
    "cost_policy",
    "data_policy",
)


def decide(context: dict[str, bool]) -> str:
    return "ALLOW" if all(context.get(k, False) for k in REQUIRED) else "DENY"
