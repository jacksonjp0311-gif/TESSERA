# Tests

## S — Specification

Unit and repository validation tests.

## H — Hooks

Inbound hooks:

- README.md
- src/tessera

Outbound hooks:

- reports
- outputs

## A — Artifacts

Evidence / output surfaces:

- test reports

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
- Meridian(s): validation, runtime
- Sector: tests
- Version / TTL: RCC-N-v1.7 / 180 days
- Last Verified: 2026-06-17

Local Role:

- Unit and repository validation tests.

Claim Boundary:

- This folder improves implementation, evidence, documentation, or navigation only within its declared scope. It does not prove code correctness, patch safety, empirical validation, transfer, safety, or production readiness.
