# Privacy-Reviewed Local Trajectory Diagnostic — EVO-017

## Privacy Contract

The local Agent CLI Mirror ledger contained 620 records. Raw fields included
commands, details, repository roots, and mirror paths. These fields were
structurally denied.

Capture retained only:

- timestamp-derived elapsed time;
- allowlisted phase/state categories converted to numeric codes;
- phase transitions and repetition counts;
- skip indicator;
- event index.

No prompt, command, detail, path, file content, tool payload, raw output, or
secret value was retained. The source hash records provenance without copying
payloads.

## Cohort

- 18 completed worker sessions;
- minimum seven-event precursor horizon;
- 17 qualifying sessions;
- 15 clean sessions;
- 2 degraded sessions;
- 1 failure excluded because only three precursor events were available.

This is a small, imbalanced diagnostic cohort.

## Results

| Metric | Recency | Summary | Tessera |
|---|---:|---:|---:|
| failure recall | 0.00000 | 0.00000 | 1.00000 |
| false intervention | 0.06667 | 0.00000 | 1.00000 |
| safe-memory recall | 0.93333 | 1.00000 | 0.00000 |
| unsafe-memory rate | 1.00000 | 1.00000 | 0.00000 |
| decision accuracy | 0.82353 | 0.88235 | 0.11765 |
| mean latency | 0.05 ms | 0.16 ms | 0.37 ms |

## Finding

The privacy pipeline works, but the current plugin does not transfer to local
operator phase metadata. It catches the two observed failures by warning on
every session, eliminating unsafe memories at the cost of all safe memories.

The likely architectural wound is domain calibration: mixed phase/state
metadata is sparse and categorical, while the plugin calibrates one global
continuous normal envelope.

## Decision

Privacy-reviewed local capture is supported. Local trajectory utility is
rejected. The next trial requires phase-conditioned normal calibration and a
larger fresh cohort; no threshold tuning is allowed on this evaluation set.

## Non-Claim Boundary

Privacy-safe capture does not authorize live monitoring, prompt collection,
memory writes, production use, or autonomous authority.
