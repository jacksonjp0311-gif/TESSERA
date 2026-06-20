# NAB Enhanced Network Diagnostic — EVO-014

## Purpose

Evaluate the EVO-012/013 enhanced neural architecture on the pinned NAB
machine-temperature stream without replacing the previously supported NAB T1
certificate unless the same promotion bundle survives.

## Protocol Repair

The first EVO-014 attempt used percentage splits and did not expand NAB's
official anomaly windows, leaving zero anomalies in the final test. Those runs
are invalid and discarded.

The valid evaluation restored:

- `NabKnownCauseAdapter`;
- official `combined_windows.json` labels;
- fixed split boundaries `850 / 1700 / 6000 / 18000`;
- train-only scaling;
- normal-only anomaly calibration;
- held-out replay;
- single-pass final test.

## Results

| Metric | depth 2 / hidden 64 | depth 3 / hidden 128 |
|---|---:|---:|
| AUC | 0.46438 | 0.94448 |
| recall | 0.14462 | 0.99295 |
| replay coverage | 0.55756 | 0.53473 |
| final-test false-memory rate | 0.00000 | 0.00000 |
| neural prediction loss | 0.07703 | 0.07711 |
| selected expert | EWMA 0.8 | EWMA 0.8 |
| selected prediction loss | 0.02488 | 0.02488 |
| persistence loss | 0.02579 | 0.02579 |

The larger architecture preserved strong anomaly ranking and the selected
causal expert improved forecasting, but replay remained below the `0.60`
promotion gate. The smaller architecture also lost anomaly ranking.

## Decision

The original NAB T1 certificate remains canonical. The enhanced network is
diagnostic and must not replace the supported codec. Architectural scale is not
a monotonic capability gain.

## Additional Rehydration Finding

EVO-013 evidence recorded 74 passing tests. Rehydration observed 71 tests
before the EVO-014 protocol regression test was added. This accounting drift
does not invalidate passing tests, but future evidence must derive test counts
from the actual test runner.

## Non-Claim Boundary

Strong AUC with failed replay is not a transfer certificate, production
readiness, memory safety, or autonomous authority.
