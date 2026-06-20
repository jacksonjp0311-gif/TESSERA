# Multiscale Awareness Evolution — TESSERA-EVO-003

## Specification

In Tessera, “awareness” means measured observability across independent runtime
signals. It does not mean consciousness, sentience, subjective experience, or
autonomous authority.

## Discovery path

EVO-002 exposed a scoring inversion: raw reconstruction error dominated the
rate-distortion score, while some anomalies produced lower reconstruction
error. A one-sided weighted sum therefore ranked unfamiliar states as normal.

The implemented synthesis connects:

- OmniAnomaly: learn normal multivariate temporal representations and derive
  anomaly evidence from deviations.
  <https://dl.acm.org/doi/10.1145/3292500.3330672>
- USAD: reconstruction-based evidence can be useful, but must be stable and
  operationally bounded.
  <https://www.kdd.org/kdd2020/accepted-papers/view/usad-unsupervised-anomaly-detection-on-multivariate-time-series.html>
- Page CUSUM: persistent deviations carry information beyond isolated points.
  <https://doi.org/10.1093/biomet/41.1-2.100>
- Robust statistics: median/MAD references resist contamination better than
  mean/variance references.

## Implemented sensor

```text
normal-only calibration
-> robust two-sided channel deviation
-> bounded channel influence
-> top-two corroboration
-> instant / 3-step / 7-step temporal scales
-> warning, block, and replay-safe memory proposal gates
```

Channels:

- forecast innovation;
- reconstruction deviation;
- spectral-field surprise;
- latent-code drift;
- latent rate deviation.

Each robust score is capped at `12`, preventing one drifting sensor from
dominating the system. The fused score uses the mean of the two strongest
channels and the maximum across instant, short, and medium temporal views.

## Five-seed result

- median AUC: `0.80222`
- mean replay pass rate: `0.65231`
- mean missed-warning rate: `0.07407`
- maximum false-memory rate: `0.0`
- forecast baseline parity: passed
- Phase 1 aggregate gate: passed

The combined score exceeded every individual channel in the inspected seed:
combined `0.80889`, latent drift `0.78741`, rate `0.78148`, prediction
`0.77037`, field surprise `0.66444`, reconstruction `0.50`.

## Boundary and next hypothesis

This is synthetic Phase 1 evidence only. It does not prove transfer, safety,
production readiness, consciousness, or general anomaly superiority.

The next operation is Phase 2: freeze this synthetic reference, ingest a
versioned real telemetry dataset through `DatasetAdapter`, preserve
chronological leakage controls, and issue only dataset-scoped T1 evidence.
