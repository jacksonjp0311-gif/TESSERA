# Theory and Reference Imports

## S — Specification

This folder stores Tessera theory lineage and imported governance/reference documents used to align the repository before GitHub promotion.

## H — Hooks

Inbound hooks:

- README.md
- docs/context/repository_context_index.json
- rcc/nexus/route_map.json

Outbound hooks:

- docs/theory/import_manifest.json
- docs/alignment
- docs/architecture

## A — Artifacts

- `imports/` — uploaded external/reference theory files.
- `tessera_lineage/` — TESSERA v1.3-v1.7 source lineage, when available.
- `import_manifest.json` — machine-readable import inventory.

## T — Theory / Basis

TESSERA v1.7, RP-SA, RCC-N v1.7, LFTE-SA format lessons, OMN README/RCC pattern, and ASF-R evidence-gated continuation pattern.

## I — Invariants

- Theory is source context, not proof.
- Imported docs must preserve attribution.
- Runtime claims require evidence packages.
- Navigation is not validation.
- Validation remains required.

## E — Examples

```bash
python scripts/validation/validate_architecture_contracts.py
```

## RCC Nexus Echo Location

Sphere Position:

- Shell: middle
- Meridian(s): theory, alignment, rcc, evidence
- Sector: docs/theory
- Version / TTL: RCC-N-v1.7 / 180 days
- Last Verified: 2026-06-17

Local Role:

- Theory lineage and imported source/reference surface.

Claim Boundary:

- This folder preserves source context. It does not prove implementation correctness, transfer, safety, or model capability.
