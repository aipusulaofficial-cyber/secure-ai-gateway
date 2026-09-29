# GitHub Workflow Guide

This repository uses GitHub Actions as executable engineering evidence.

## Workflow model

Workflows live in `.github/workflows/`. A trigger starts a workflow, jobs execute on runners, and each job contains ordered steps.

**Evidence flow**

`Trigger → Runner → Setup → Quality Gates → Domain Evidence → Tests → Security/Build Checks → Artifacts → Result`

## What the Actions UI proves

- **Run:** which commit and trigger produced the evidence.
- **Job:** the verification unit that ran.
- **Step:** the exact action or command executed.
- **Gate:** the condition that can stop the verification path.
- **Artifact:** persistent test, coverage, benchmark, report, or build output.

## Repository-specific evidence focus

**HTTP/security behavior, policy boundaries, production tests, and supply-chain evidence.**

A successful workflow proves the configured checks passed for that commit. It is not a blanket claim about production scale or external infrastructure.

## Failure diagnosis

Inspect the first failed step. Later skipped steps are normally consequences, not additional root causes. Correct the repository, commit the fix, and verify the new commit's full workflow set.

## Reproducibility and artifacts

Keep important verification executable from the repository and preserve machine-readable outputs as workflow artifacts where they add audit value.

## Portfolio signal

This repository is one component of the AIPUSULA enterprise AI platform portfolio. Its workflow converts the domain contract into repeatable CI evidence.

See `docs/PORTFOLIO_EVIDENCE.md` for the domain proof chain.
