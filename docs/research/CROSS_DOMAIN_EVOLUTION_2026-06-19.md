# Tessera Cross-Domain Evolution Note

## Scope

This note records the engineering patterns used to evolve Tessera's synthetic
predictor. It is a design rationale, not evidence of transfer or general
superiority.

## Connected patterns

1. **Residual forecasting** — N-BEATS demonstrates that residual links are a
   strong primitive for forecasting. Tessera now predicts a bounded innovation
   over a stable level estimate instead of reconstructing the next state from
   scratch.
   Source: <https://arxiv.org/abs/1905.10437>
2. **Train/inference alignment** — scheduled sampling identifies the damage
   caused when sequence models experience different state distributions during
   training and inference. Tessera now optimizes whole chronological sequences
   with recurrent field state preserved inside each epoch.
   Source: <https://arxiv.org/abs/1506.03099>
3. **Distribution-shift normalization** — RevIN motivates explicit handling of
   changing time-series levels. Tessera does not implement RevIN in this phase;
   it adopts the narrower inference that a stable, reversible level reference
   should remain available to the predictor.
   Source: <https://openreview.net/forum?id=cGDAkQo1C0p>
4. **Reservoir readout discipline** — echo-state systems separate temporal
   dynamics from a simpler trained readout. Tessera retains its sparse spectral
   field while shrinking the learned correction around a simple EWMA expert.
   Source: <https://arxiv.org/abs/2405.06561>
5. **Shrinkage and expert selection** — a zero-correction expert is included in
   validation selection. Neural correction gains are restricted to
   `0.0`, `0.1`, or `0.25`, preventing the learned field from freely displacing
   the stable forecasting floor.

## Implemented synthesis

```text
EWMA level expert
  + sparse spectral field
  + compressed latent code
  + bounded neural innovation
  + held-out gain selection
  = guarded hybrid predictor
```

Training now uses Smooth L1 loss, sequence-level optimization, cosine learning
rate decay, gradient clipping, correction-energy regularization, and a
zero-initialized innovation head.

## Measured result

The original three-seed benchmark had mean prediction loss `289.3497` and mean
baseline gap `-178.5070`.

The five-seed, 300-step confirmation benchmark produced:

- mean prediction loss: `93.5105`
- mean baseline gap: `-0.00134`
- relative baseline gap: approximately `-0.00143%`
- baseline parity tolerance: `0.1%`
- baseline parity: passed
- median AUC: `0.4415`
- replay pass rate: `0.0`

Therefore only the baseline-parity sub-gate is cleared. Phase 1 remains blocked
by anomaly discrimination, replay utility, and missed-warning performance.

## Next hypothesis

Prediction error alone is not separating anomaly families. The next bounded
experiment should create a multiscale anomaly score combining forecast
innovation, reconstruction residual, field surprise, and latent drift, then
calibrate it on normal-only windows. No memory or repair promotion should occur
until that score improves AUC and replay metrics across seeds.
