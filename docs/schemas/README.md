# Tessera Schemas

## Specification

Versioned contracts for datasets and the host-neutral neural plugin.

## Hooks

- `src/tessera/data/adapters.py`
- `src/tessera/plugin/contracts.py`

## Artifacts

- `dataset_manifest.schema.json`
- `plugin_manifest.schema.json`

## Invariants

- Schemas do not grant runtime authority.
- Plugin permissions default to read-mostly local behavior.
- Final-test and replay boundaries remain explicit.

## Claim Boundary

Schema conformance is not capability, security, or production-readiness proof.
