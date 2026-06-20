# NASA Telemanom Source Capsule

## Specification

Pinned spacecraft telemetry benchmark artifacts for Tessera Phase 2.

## Hooks

- Inbound: Telemanom repository, Kaggle mirror referenced by upstream README
- Outbound: SMAP channel adapter, diagnostic transfer runner, leakage evidence

## Artifacts

- `data.zip`
- `labeled_anomalies.csv`
- `LICENSE.txt`
- `source_manifest.json`
- `extracted/`

## Invariants

- Source hashes are immutable.
- Official train/test arrays and anomaly indices remain unchanged.
- Inherited preprocessing leakage must remain visible in every certificate.

## Claim Boundary

The published arrays were scaled using test-set extrema. Results are benchmark
diagnostics and cannot satisfy Tessera's clean T1 leakage gate.
