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

## Authentication readiness and deployment prerequisites

Provision the `ai-gateway-auth` secret with key `jwt-secret` through the environment's approved secrets manager *before* deployment. Kubernetes and Helm reference the existing secret; neither chart nor repository creates or stores the secret value. Rotate the secret according to your key-management procedure and use a rollout so pods reload the environment variable.

`/health/live` proves the HTTP process is running. `/health/ready` returns **503** when `AI_GATEWAY_JWT_SECRET` is missing, and 200 otherwise. Readiness does **not** prove an upstream provider or future shared rate-limit backend is healthy.

**Current multi-replica limit:** `RateLimiter` is only thread-safe within one process and the public HTTP rate-limit key comes from the request. In deployments with multiple replicas, neither quota integrity across replicas nor protection from client key rotation is established. See [distributed limiter remediation](https://github.com/aipusulaofficial-cyber/secure-ai-gateway/issues/11). Do not present local quota tests as proof of fleet-wide rate limiting.
