# RCC

## S — Specification

Repository Context Canon and RCC-N support surface for Tessera.

## H — Hooks

Inbound hooks:

- README.md
- AGENTS.md
- README_90_SECONDS.md
- docs/context/repository_context_index.json
- docs/context/rcc_nexus_index.json

Outbound hooks:

- rcc/nexus
- reports/rcc_nexus

## A — Artifacts

- rcc/nexus/route_map.json
- rcc/nexus/README.md
- rcc/nexus/agent_handoff_contract.md
- rcc/nexus/task_routing_matrix.md

## T — Theory / Basis

Governed by RCC-N v1.7 and Tessera alignment locks.

## I — Invariants

- Navigation is not validation.
- Documentation is not correctness.
- Validation remains required.
- Do not push until James authorizes it.

## E — Examples

```bash
python scripts/rcc/check_rcc_nexus.py
```

## RCC Nexus Echo Location

Sphere Position:

- Shell: center
- Meridian(s): rcc, agent, drift, documentation, safety
- Sector: rcc
- Version / TTL: RCC-N-v1.7 / 180 days
- Last Verified: 2026-06-17

Local Role:

- RCC root shell for Nexus routing and navigation.

Claim Boundary:

- This folder improves navigation and agent orientation only. It does not prove code correctness, patch safety, empirical validation, transfer, safety, or model capability.
