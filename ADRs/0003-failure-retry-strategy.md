# ADR-0003: Failure and retry strategy

## Decision
Use explicit timeout budgets, bounded exponential backoff, idempotency-aware retries, bounded concurrency, token-bucket rate limiting where applicable, and circuit breaking for repeated dependency failures.

## Why
Hidden or unlimited retries amplify outages and can duplicate non-idempotent side effects. Explicit budgets make failure behavior observable.

## Alternatives considered
Unlimited retries, fixed-delay retries, and blind retries for every request were rejected.

## Trade-offs
Predictable failure and bounded latency are preferred over exhausting every dependency attempt. Thresholds must be tuned from measured traffic.

## Consequences
Callers must declare retryable exceptions and only enable retries for safe/idempotent operations.

## Implementation evidence
resilience.py, tests/test_resilience.py, docs/FAILURE-MATRIX.md and docs/OPERATIONS.md.