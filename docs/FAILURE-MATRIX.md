# Failure matrix

| Failure | Detection | Action | Retry? | User impact |
|---|---|---|---|---|
| Invalid/untrusted input | contract validation | reject deterministically | No | 4xx |
| Dependency timeout | timeout budget | normalize + record dependency | Only if safe/idempotent | explicit dependency error/degradation |
| Dependency 5xx | provider adapter | bounded exponential backoff | Only if safe/idempotent | bounded latency |
| Repeated dependency failure | circuit breaker | open circuit | No while open | fast failure |
| Local overload | semaphore/token bucket | fail fast | No | 429/degraded path |
| Telemetry failure | exporter error | preserve domain result | bounded/exporter-local only | no domain corruption |

Unauthorized -> 401/403; rate limit -> 429; policy dependency timeout -> fail closed; repeated dependency failures -> circuit open; no implicit retry for non-idempotent requests.