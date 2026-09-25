# Deployment verification

1. Build the container from the pinned source revision.
2. Verify non-root execution and declared CPU/memory limits.
3. Apply Kubernetes/Helm manifests and confirm readiness probes.
4. Confirm HPA/PDB/resource bounds where configured.
5. Verify API health and representative domain smoke test.
6. Verify request_id/correlation_id propagation and telemetry export configuration.
7. Confirm security/SBOM workflow passed for the same revision.
8. Record the deployment revision and rollback target.

A deployment is not considered verified from manifest presence alone; the checks above must execute in the target environment.