# External Dataset Capsules

## Specification

Pinned, hash-addressed external telemetry artifacts used by Tessera's
dataset-scoped transfer experiments.

## Hooks

- Inbound: user-authorized public dataset retrieval
- Outbound: dataset adapters, manifests, transfer certificates, wounds

## Artifacts

- `nab/`
- `telemanom/`

## Invariants

- Every source records repository, version, license, and hashes.
- Inherited preprocessing leakage remains explicit.
- Dataset files never grant live model, memory, tool, or repair authority.

## Claim Boundary

Dataset availability and provenance do not prove transfer capability.
