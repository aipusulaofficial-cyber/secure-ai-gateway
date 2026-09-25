# ADR-0004: Security decision

## Decision
Treat external requests, prompts/documents, configuration and provider data as untrusted. Validate at boundaries, enforce least privilege, bound resources, sanitize telemetry, and fail closed for security-sensitive decisions.

## Why
AI-facing systems cross trust boundaries and can amplify malformed or adversarial inputs.

## Alternatives considered
Trusting internal callers, logging raw inputs, and fail-open authorization were rejected.

## Trade-offs
Redaction can reduce debugging detail; correlation IDs and structured error categories preserve diagnosis without exposing sensitive content.

## Consequences
Security behavior is deterministic and auditable.

## Implementation evidence
service validation, structured logging, deployment hardening and repository security/SBOM workflows.