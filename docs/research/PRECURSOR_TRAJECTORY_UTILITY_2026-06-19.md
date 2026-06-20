# Precursor-Only Trajectory Utility — EVO-016

## Hypothesis

Typed temporal modeling should detect degrading agent trajectories before an
explicit error or retry flag appears, where simple recency and robust summary
controls are weaker.

## Protocol

- Fresh deterministic seeds `100` through `123`;
- 24 trajectories, half degraded;
- 12 events per trajectory;
- no explicit final error, retry, or failed-test flags;
- policies frozen before scoring: recency, robust summary, Tessera plugin.

## Results

| Metric | Recency | Summary | Tessera |
|---|---:|---:|---:|
| failure recall | 0.00000 | 0.33333 | 1.00000 |
| false intervention | 0.00000 | 0.00000 | 0.16667 |
| safe-memory recall | 1.00000 | 1.00000 | 0.58333 |
| unsafe-memory rate | 1.00000 | 0.66667 | 0.00000 |
| decision accuracy | 0.50000 | 0.66667 | 0.91667 |
| mean latency | 0.07 ms | 0.17 ms | 98.14 ms |

## Finding

Tessera detected every synthetic degradation precursor and rejected every
unsafe memory candidate, materially outperforming the two controls on decision
accuracy. It also produced more false interventions, retained fewer safe
memories, and cost roughly two orders of magnitude more latency.

## Decision

Offline synthetic precursor utility is supported. Live agent utility is not.
The next benchmark should use privacy-reviewed captured trajectories, preserve
the same controls, and add task-success and recovery-latency outcomes.

## Non-Claim Boundary

Synthetic precursor performance does not prove live utility, safe autonomous
memory, production readiness, consciousness, or tool authority.
