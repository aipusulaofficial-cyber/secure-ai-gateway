# Production Contract

This component participates in the AIPusula platform control plane.

## Required context
- correlation/trace ID
- component version
- dependency/model version
- policy decision
- audit reference

## Non-negotiable behavior
- deterministic error contract
- bounded retries/timeouts
- explicit security and cost policy decisions
- observable execution
- reproducible tests/evidence

## Release gate
Changes must pass repository tests plus the platform's security, quality, provenance and evidence requirements.
