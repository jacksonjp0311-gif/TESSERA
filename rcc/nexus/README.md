# RCC Nexus

## S — Specification

RCC-N route shell for Tessera repository navigation, Echo Location, agent handoff, and validation-bound context reconstruction.

## H — Hooks

Inbound hooks:

- README.md
- AGENTS.md
- docs/context/repository_context_index.json
- docs/context/rcc_nexus_index.json

Outbound hooks:

- rcc/nexus/route_map.json
- rcc/nexus/task_routing_matrix.md
- rcc/nexus/agent_handoff_contract.md
- scripts/rcc/check_rcc_nexus.py

## A — Artifacts

- route_map.json
- task_routing_matrix.md
- agent_handoff_contract.md

## T — Theory / Basis

RCC-N v1.7 adoption-profile governance: declared geometry is documentation, measured geometry is evidence, enforced geometry is infrastructure, validation is the reality boundary.

## I — Invariants

- RCC tells the agent what the repository means.
- RCC-N tells the agent where it is.
- Validation tells the agent whether reality agreed.
- Route maps must not exceed validation.
- Claim ceilings must remain visible.

## E — Examples

```bash
python scripts/rcc/check_rcc_nexus.py
```

## RCC Nexus Echo Location

Sphere Position:

- Shell: center
- Meridian(s): agent, drift, documentation, safety, memory
- Sector: rcc/nexus
- Version / TTL: RCC-N-v1.7 / 180 days
- Last Verified: 2026-06-17

Local Role:

- Nexus route map and agent-orientation shell.

Claim Boundary:

- This folder improves implementation, evidence, documentation, or navigation only within its declared scope. It does not prove code correctness, empirical validation, transfer, safety, or production readiness.
