# UCR Sensor Router — EVO-008

## Specification

Test whether independently calibrated point and subsequence sensors can route
UCR observations into shared episode and memory governance.

## Preregistered pairs

Point scale:

- discovery: series `228`, anomaly length `21`;
- untouched confirmation: series `229`, anomaly length `11`.

Subsequence scale:

- discovery: series `192`, anomaly length `101`;
- untouched confirmation: series `193`, anomaly length `101`.

The runtime router does not inspect labels or filename anomaly duration. It
compares normal-calibrated evidence from:

- robust point level, velocity, and acceleration;
- window-24 z-normalized subsequence discord with hold `12`.

## Point-scale result

Untouched confirmation:

- routed AUC `0.947314`;
- point-only AUC `0.931024`;
- subsequence-only AUC `0.818722`;
- recall `1.0`;
- false-memory rate `0.0`.

Route-aware episode governance uses a short point hold and long subsequence
hold. It improved normal replay coverage from `0.36262` to `0.46536`, but did
not reach the `0.60` gate.

## Subsequence-scale result

Untouched confirmation:

- routed AUC `0.648056`;
- subsequence-only AUC `0.771177`;
- point-only AUC `0.532244`;
- missed warnings `0.653465`;
- false-memory rate `0.396040`.

Taking the maximum of both sensors degraded the stronger subsequence evidence.

## Learned architecture

The router requires a third action:

```text
point
subsequence
abstain
```

Detection confidence and memory confidence also require separate calibration.
A strong event detector should not automatically determine normal-memory
coverage.

## Next experiment

Build confidence-aware abstention and an independent memory normality model on
new preregistered pairs. Keep forecasting as a separate capability gate.

## Claim Boundary

The point sensor tile is confirmed. The universal router, UCR T1 transfer,
forecasting capability, memory promotion, and autonomous authority remain
unsupported.
