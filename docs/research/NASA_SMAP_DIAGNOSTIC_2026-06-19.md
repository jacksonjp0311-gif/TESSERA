# NASA SMAP Telemanom Diagnostic — EVO-005

## Specification

Cross-family evaluation of Tessera on pinned NASA SMAP spacecraft telemetry.
This is diagnostic evidence, not a supported T1 transfer.

## Provenance boundary

The Telemanom repository is pinned at
`2e6c5b6c3558e7835601519b7bdef37c649bdbdc` under Apache 2.0. The upstream
README describes the arrays as pre-scaled using test-set minima and maxima.
Tessera records `upstream_preprocessing_independent_of_test=false`; therefore
the clean leakage gate is structurally blocked.

## Discovery sequence

1. **P-1 baseline sensor:** combined AUC `0.481`.
2. **P-1 target-aware prediction:** next-step loss improved from `0.715` to
   `0.599`, but combined AUC fell to `0.460`.
3. **S-1 point anomaly:** field and rate channels reached `0.655` and `0.662`,
   while the fused score reached only `0.567`.
4. **Field-energy hypothesis:** instant mean of field surprise and latent rate
   reached about `0.606` on explored P-1 and `0.652` on explored S-1.
5. **Untouched E-2 confirmation:** the hypothesis failed with AUC `0.569`,
   missed-warning rate `0.996`, and false-memory rate `0.949`.

## What was learned

- NAB success did not generalize to contextual spacecraft telemetry.
- Telemanom's first column is a telemetry target; remaining columns are sparse
  command/event context and should not be treated as equivalent outputs.
- Sparse-field energy notices regime activity but does not yet represent
  anomaly meaning consistently across channels.
- Scalar sensor fusion is insufficient for command-conditioned contextual
  anomalies.
- Source-level preprocessing lineage can block promotion even before model
  metrics are considered.

## Next architecture hypothesis

NASA contextual telemetry should use a relational context model:

```text
target telemetry dynamics
+ command/event transition encoder
+ conditional expected-state model
+ event-level anomaly scoring
```

This branch remains diagnostic. The next clean Phase 2 family is UCR, while
NASA work proceeds as a separate context-conditioned research track.

## Claim Boundary

No NASA T1 support, clean transfer, safety, production readiness, memory
promotion, consciousness, or autonomous authority is claimed.
