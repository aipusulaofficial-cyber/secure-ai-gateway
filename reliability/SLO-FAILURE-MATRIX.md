# SLO & Failure Injection Matrix

| Failure | Expected control | Evidence |
|---|---|---|
| Upstream timeout | bounded timeout + retry/fallback | test/log |
| Backend unavailable | health-aware isolation | test/log |
| Dependency failure | fail closed or degraded mode | test/log |
| Invalid input | contract validation | test |
| Quota exhausted | policy DENY | test |
| Model/tool failure | bounded retry + audit | test/log |

For each scenario capture detection, decision, recovery time, and user-visible outcome.

Example SLO dimensions:
- availability
- latency p95/p99
- error rate
- recovery time

SLO values should be set from measured service requirements rather than copied as arbitrary targets.