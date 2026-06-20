# UCR 2021 Anomaly Archive Capsule

## Specification

Pinned UCR anomaly archive for clean, univariate Phase 2 transfer trials.

## Hooks

- Inbound: Figshare DOI artifact under CC BY 4.0
- Outbound: UCR filename-contract adapter and dataset-scoped transfer runner

## Artifacts

- `UCR_TimeSeriesAnomalyDatasets2021.zip`
- `source_manifest.json`
- `extracted/`

## Invariants

- Filename-encoded train and anomaly boundaries are parsed, not manually copied.
- Scaling is fit only inside the normal training prefix.
- Discovery and confirmation series are declared before evaluation.
- Final-test partitions are single-pass and read-only.

## Claim Boundary

One UCR series is one dataset-scoped result, not archive-wide superiority.
