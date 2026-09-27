# Supply Chain, Benchmark & Reliability Evidence

This repository follows a production-oriented evidence chain.

## Supply-chain controls
Required release controls:
- dependency vulnerability scanning
- secret scanning
- static analysis (SAST)
- IaC/container scanning where applicable
- SBOM generation for releasable artifacts
- build provenance and artifact verification
- immutable/versioned release evidence

## Benchmark evidence
Performance claims must be measured, not invented. Record:
- workload and dataset/model version
- environment and configuration
- throughput
- p50/p95/p99 latency
- error rate
- CPU/memory where relevant
- baseline vs post-change
- command and commit SHA used for reproduction

## Reliability evidence
Exercise controlled failures such as:
- upstream timeout
- backend unavailable
- dependency failure
- malformed input
- rate-limit/quota exhaustion
- model/tool failure

Record detection, containment, retry/fallback behavior, recovery time, and whether the SLO was preserved.

## Release rule
A release is evidence-backed only when tests, policy gates, security controls, and relevant benchmark/reliability evidence are available.