# ADR-0002: Production hardening
FastAPI defines the edge contract and OpenTelemetry traces requests. Kubernetes defines probes and bounded resources; Helm packages deployment; Terraform owns infrastructure inputs. Trivy and CycloneDX enforce security/SBOM checks; HTTP contract plus Hypothesis tests protect the API; Locust supplies load traffic.
Production trade-off: keep local execution deterministic while externalizing state, secrets, telemetry and autoscaling in real environments.
