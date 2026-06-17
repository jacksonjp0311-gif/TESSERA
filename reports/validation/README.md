# validation

## S — Specification

Generated architecture validation reports.

## H — Hooks

Inbound hooks:

- reports/README.md
- docs/architecture/README.md

Outbound hooks:

- reports/validation/latest_architecture_contract_validation.json

## A — Artifacts

- reports/validation/latest_architecture_contract_validation.json

## T — Theory / Basis

Governed by TESSERA V1.7, Tessera Engine v0.1, RCC-N v1.7, and the repository non-claim locks.

## I — Invariants

- Preserve source attribution.
- Preserve non-claim boundaries.
- Navigation is not validation.
- Documentation is not correctness.
- Synthetic success is not real telemetry transfer.
- Validation remains required.
- Do not push to GitHub until James explicitly authorizes it.

## E — Examples

Run relevant validation after changes:

```bash
python scripts/rcc/check_rcc_nexus.py
python scripts/validation/validate_architecture_contracts.py
python -m unittest discover -s tests
```

## RCC Nexus Echo Location

Sphere Position:

- Shell: middle
- Meridian(s): tessera, rcc, alignment, evidence
- Sector: reports/validation
- Version / TTL: RCC-N-v1.7 / 180 days
- Last Verified: 2026-06-17

Local Role:

- Generated architecture validation reports.

Claim Boundary:

- This folder improves implementation, evidence, documentation, or navigation only within its declared scope.
- It does not prove code correctness, patch safety, empirical validation, safety, production readiness, model capability, or real telemetry transfer.

Non-Claim Locks:

- navigation_is_not_validation
- documentation_is_not_correctness
- compression_is_not_truth
- replay_is_not_safety
- synthetic_success_is_not_transfer
- validation_remains_required

Update Obligation:

- Update this README and RCC/Nexus records if folder purpose, hooks, evidence surfaces, validation commands, or claim boundaries change.
