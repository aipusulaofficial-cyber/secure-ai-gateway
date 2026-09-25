# Operational runbook

Track request rate, error rate, p50/p95/p99 latency, saturation/concurrency, dependency failures, retry count and circuit state. Every request should be diagnosable by request_id and correlation_id.

1. Confirm liveness/readiness and deployment revision.
2. Search logs/traces by request_id and correlation_id.
3. Check p95/p99 latency and error_type distribution.
4. Inspect dependency latency, retry_count and circuit state.
5. Check concurrency/rate-limit saturation and resource limits.
6. Verify degraded responses are explicit and do not fabricate data.
7. Restore dependency health, then run smoke/integration checks.

Check auth failures, policy dependency latency, rate-limit counters, circuit state, and audit trail. Revoke compromised credentials before reopening access.