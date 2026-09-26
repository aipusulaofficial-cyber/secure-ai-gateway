# Secure AI Gateway

A security boundary for AI services providing authentication, authorization, rate limiting, policy enforcement, threat-aware request handling and auditability.

## Request flow
```text
client -> authentication -> authorization -> rate limit -> policy -> upstream AI service
                                                |
                                             audit
```

## Security contracts
- Authentication and authorization are separate decisions.
- Rate limiting bounds resource consumption at the edge.
- Policy enforcement happens before upstream execution.
- Audit context captures decision-relevant metadata without exposing secrets.
- Denied requests are explicit failures, not degraded successes.

## Reliability
The gateway is designed to protect upstream services from malformed, unauthorized and excessive traffic. Timeouts, retries and dependency failures are represented explicitly.

## Runtime & deployment
The repository includes Kubernetes/Helm deployment, Terraform, production tests, load tests, observability code and deployment verification documentation.

## Evidence
- Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- Contracts: [docs/CONTRACTS.md](docs/CONTRACTS.md)
- Failure matrix: [docs/FAILURE-MATRIX.md](docs/FAILURE-MATRIX.md)
- Operations: [docs/OPERATIONS.md](docs/OPERATIONS.md)
- SLO: [docs/SLO.md](docs/SLO.md)
- ADRs: [ADRs](ADRs/)

CI, production tests and security/SBOM checks are executable release gates.