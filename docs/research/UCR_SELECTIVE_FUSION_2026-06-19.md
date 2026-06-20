# UCR Coverage-Constrained Selective Fusion — EVO-010

## Hypothesis

Abstention should change anomaly evidence. A router may grant specialist
authority on a bounded fraction of normal-validation rows and use consensus
fusion elsewhere.

## Frozen Protocol

- target specialist coverage: `0.20`;
- point, subsequence, or abstain route;
- specialist score on decisive rows;
- geometric consensus for inactive abstention;
- mean consensus for ambiguous active sensors;
- independent joint-normality memory gate;
- no final-test tuning.

## Confirmation Results

| Metric | ECG point | InternalBleeding shape |
|---|---:|---:|
| Selective AUC | 0.99997 | 0.24390 |
| Replay coverage | 0.62725 | 0.59066 |
| Warning recall | 1.00000 | 0.02410 |
| False-memory rate | 0.00000 | 0.79518 |
| Specialist coverage | 0.21782 | 0.16545 |
| Prediction loss | 0.42382 | 0.05713 |
| Best baseline loss | 0.01401 | 0.00044 |

Point discovery also improved from max-fusion AUC `0.73543` to selective AUC
`0.77948`. The point confirmation cleared the detector and memory gates.

InternalBleeding rejected point evidence, subsequence evidence, selective
fusion, and memory normality together. This is a sensing-family failure rather
than a routing-threshold failure.

## Engineering Finding

The long ECG confirmation exposed single-channel output-shape bugs in PCA and
random-projection baselines. Both could broadcast `(n,)` predictions against
`(n, 1)` targets and allocate quadratic matrices. Baseline outputs now preserve
the declared feature dimension, and matrix-profile lookup uses nearest-neighbor
batching.

## Decision

Coverage-constrained selective fusion is confirmed only for the point branch.
UCR T1 remains blocked by forecasting, and the current shape sensor family is
rejected for InternalBleeding.

## Next Operation

Build validation-selected prediction experts independently from anomaly
sensing, and investigate a morphology-aware shape branch without weakening
existing gates.

## Non-Claim Boundary

One promotion-quality point confirmation is not archive-wide transfer,
production readiness, memory safety, consciousness, or autonomous authority.
