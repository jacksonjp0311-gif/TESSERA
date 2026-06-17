# Alignment Surface

## S — Specification

Origin alignment, non-claim locks, certificate discipline, and no-compounding boundaries for Tessera.

## H — Hooks

Inbound hooks:

- README.md
- AGENTS.md
- docs/context/repository_context_index.json
- rcc/nexus/route_map.json

Outbound hooks:

- outputs/runs/*/certificates
- outputs/runs/*/evidence
- reports/rcc_nexus

## A — Artifacts

- origin_manifest.json
- non_claim_locks.md
- tessera_alignment_and_rcc_nexus_integration.md

## T — Theory / Basis

Governed by TESSERA V1.7, Rehydration Protocol / RP-SA, RCC-N v1.7, and the Tessera Engine v0.1 runtime boundary.

## I — Invariants

- No origin alignment, no durable mutation.
- No certificate, no memory promotion.
- No real telemetry manifest, no transfer claim.
- No baseline comparison, no superiority claim.
- No GitHub push until James authorizes it.

## E — Examples

```bash
python scripts/rcc/check_rcc_nexus.py
python scripts/validation/validate_architecture_contracts.py
```

## RCC Nexus Echo Location

Sphere Position:

- Shell: center
- Meridian(s): alignment, memory, rcc, evidence
- Sector: docs/alignment
- Version / TTL: RCC-N-v1.7 / 180 days
- Last Verified: 2026-06-17

Local Role:

- Origin-alignment and non-claim lock surface for Tessera.

Claim Boundary:

- This folder improves alignment, evidence, and navigation only. It does not prove code correctness, safety, truth, transfer, AGI, or production readiness.
