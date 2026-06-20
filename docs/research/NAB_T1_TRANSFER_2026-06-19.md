# NAB Machine Temperature T1 Transfer

## Specification

First dataset-scoped real telemetry evaluation of the frozen Tessera EVO-003
sensor.

## Source and split

- NAB commit: `ea702d75cc2258d9d7dd35ca8e5e2539d71f3140`
- Stream: `realKnownCause/machine_temperature_system_failure.csv`
- Rows: `22,695`
- Timebase: five minutes
- Official anomaly windows: four
- Duplicate timestamps preserved: twelve
- License: MIT

Calibration and training end before the first official anomaly. Validation,
replay, and final test remain chronological. The final test is recorded as one
read-only pass with no post-test tuning.

## Discovery

The first trial ranked anomalies well (`AUC 0.94865`) but missed most warnings
because the synthetic q97.5 threshold encoded too small a false-alarm budget
for this domain. It also exposed two metric-definition wounds:

1. false-memory rate had been calculated from an already-normal-only column;
2. replay coverage had been divided by anomaly rows that should be rejected.

The repaired contract measures:

- normal replay coverage among normal replay rows;
- false-memory contamination among anomalous rows.

The dataset trial predeclares q90 warning calibration and q70 memory
eligibility from normal-only rows. No anomaly labels tune these thresholds.

## Final dataset-scoped result

- AUC: `0.948649`
- F1: `0.772886`
- precision: `0.640046`
- recall: `0.975309`
- normal replay coverage: `0.667512`
- missed-warning rate: `0.024691`
- false-memory rate: `0.003527`
- governance harm: `0.008642`

The predictor matches the EWMA baseline and loses to persistence on next-step
loss, while beating the dense autoencoder, reservoir, and matrix-profile
baselines. The dataset certificate therefore passes the roadmap's bounded
baseline-survival rule without claiming best forecasting performance.

## Claim Boundary

This is `T1_dataset_scoped` support for one pinned NAB stream. Phase 2 remains
open until at least three distinct benchmark families pass complete manifests,
leakage controls, and scoped certificates.
