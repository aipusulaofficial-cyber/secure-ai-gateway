# Contracts

authentication/authorization/policy/rate-limit/threat decision is the core domain boundary.

- API contract: versioned request/response schema and validation.
- Domain contract: invariants and deterministic state transitions.
- Provider contract: adapter interface, timeout/error taxonomy and normalized results.
- Event contract: versioned envelope where asynchronous events exist.
- Configuration contract: bounded and validated environment values.

Compatibility changes require tests before merge. Provider-specific exceptions are normalized before entering domain logic.