# Source Root

## S — Specification

Python source root for Tessera runtime.

## H — Hooks

Inbound hooks:

- README.md
- AGENTS.md

Outbound hooks:

- src/tessera

## A — Artifacts

Evidence / output surfaces:

- src/tessera/*

## T — Theory / Basis

Governed by Tessera Engine v0.1, TESSERA V1.7, RCC-N v1.7, and repository non-claim locks.

## I — Invariants

- Preserve source attribution.
- Preserve non-claim boundaries.
- Do not treat navigation as validation.
- Do not treat documentation as correctness.
- Keep evidence and validation surfaces inspectable.

## E — Examples

Run relevant validation after changes:

```bash
python -m unittest discover -s tests
```

## RCC Nexus Echo Location

Sphere Position:

- Shell: middle
- Meridian(s): runtime, neural, memory
- Sector: src
- Version / TTL: RCC-N-v1.7 / 180 days
- Last Verified: 2026-06-17

Local Role:

- Python source root for Tessera runtime.

Claim Boundary:

- This folder improves implementation, evidence, documentation, or navigation only within its declared scope. It does not prove code correctness, patch safety, empirical validation, transfer, safety, or production readiness.
