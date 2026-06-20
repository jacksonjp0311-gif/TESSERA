# NAB Machine Temperature Source Capsule

## Specification

Pinned source material for the first Tessera dataset-scoped real telemetry
trial.

## Source

- Repository: <https://github.com/numenta/NAB>
- Commit: `ea702d75cc2258d9d7dd35ca8e5e2539d71f3140`
- Stream: `data/realKnownCause/machine_temperature_system_failure.csv`
- Labels: `labels/combined_windows.json`
- License: MIT

## Hooks

- Inbound: pinned NAB stream, official combined anomaly windows, MIT license
- Outbound: `NabKnownCauseAdapter`, T1 transfer runner, dataset certificate

## Artifacts

- `machine_temperature_system_failure.csv`
- `combined_windows.json`
- `LICENSE.txt`
- `source_manifest.json`

## Hashes

- stream: `92bf5b87fc7f9bba8ca0b7ec63ccaac8cb4a1371a258e8c29a10ae9c018d82a4`
- labels: `1e1fbc4601321aad8d0f8b3784c8134299379f68f6c1f7777565f8ffd57ab6b1`
- license: `0a0b4d0b10cb1f7ed9ab2993ef93defc03447e6eba9daca1315dd32dae4877e3`

## Known Caveats

- The upstream stream contains 12 duplicate timestamps.
- NAB anomaly windows are benchmark windows, not instantaneous failure labels.
- This is one univariate stream from one benchmark family.

## Invariants

- Raw rows and duplicate timestamps remain unchanged.
- Labels are evaluation-only.
- Hash drift blocks dataset-scoped comparison.

## Claim Boundary

Evaluation on this capsule supports only dataset-scoped evidence. It does not
prove general real-telemetry transfer.
