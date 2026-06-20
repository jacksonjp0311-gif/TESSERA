# Tessera RHP

## Specification

Compact read-only rehydration and evidence-lineage substrate.

## Hooks

- Inbound: `README.md`, `AGENTS.md`, Agent CLI Mirror
- Outbound: Nexus registry, geometry graph, lesson chart, validation report

## Artifacts

- `latest-rhp.json`
- `origin_manifest.json`
- `evidence/`
- `RHP_ZERO_CONTEXT_REBUILD.md`

## Invariants

- Current truth comes from the pointer and named evidence.
- Authority locks remain false.
- Historical Hermes evidence is not copied into Tessera.
- Rehydration is not validation or authority.

## Claim Boundary

RHP reconstructs bounded repository state only. It does not prove model
capability, safety, correctness, production readiness, or transfer.
