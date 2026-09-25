# Architecture

## Boundaries
Public contracts, domain logic, and infrastructure adapters remain separated so providers can be replaced safely.

## Reliability
Validate inputs, bound resources, make failures explicit, and keep retry policy at a layer that understands idempotency.

## Production trade-offs
The foundation favors deterministic local execution and small interfaces. Production should externalize shared state, export OpenTelemetry telemetry, and enforce SLO, security, and resource policies.
