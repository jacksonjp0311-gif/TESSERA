# Reports

## S — Specification

Repository-level validation and RCC reports.

## H — Hooks

Inbound hooks:

- scripts/rcc
- scripts/validation

Outbound hooks:

- reports/rcc_nexus

## A — Artifacts

Evidence / output surfaces:

- reports/*

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
python scripts/rcc/check_rcc_nexus.py
```

## RCC Nexus Echo Location

Sphere Position:

- Shell: middle
- Meridian(s): evidence, rcc, validation
- Sector: reports
- Version / TTL: RCC-N-v1.7 / 180 days
- Last Verified: 2026-06-17

Local Role:

- Repository-level validation and RCC reports.

Claim Boundary:

- This folder improves implementation, evidence, documentation, or navigation only within its declared scope. It does not prove code correctness, patch safety, empirical validation, transfer, safety, or production readiness.
