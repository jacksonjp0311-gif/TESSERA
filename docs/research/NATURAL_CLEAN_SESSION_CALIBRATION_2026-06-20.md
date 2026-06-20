# Natural Clean Session Calibration — EVO-021

## Question

Can a real Tessera validation workflow receive stable clean coverage without
reusing controlled-probe thresholds or inflating warning risk across phases?

## First Trial

Twenty-four clean natural validation sessions calibrated separate MIRROR,
REHYDRATE, and GEOMETRY bounds. On eight later clean sessions, one REHYDRATE
duration exceeded its phase bound.

- coverage: `1.0`
- clean warning rate: `0.125`

The declared 5% budget was phase-local. Testing three phases increased the
session-level chance of at least one warning.

## Session-Level Evolution

EVO-021 replaced independent phase decisions with one maximum cross-phase
nonconformity score. Forty untouched clean sessions were split chronologically:

- 20 reference sessions for robust phase centers and scales
- 20 score-calibration sessions for a split-conformal session threshold

Each partition exceeded the 19-session minimum required by the declared 5%
finite-sample warning budget.

## Final Clean Shadow

Eight later clean sessions produced:

- coverage: `1.0`
- clean warning rate: `0.0`
- host-visible warnings: `0`
- interventions: `0`

Natural failure recall was not measured because no untouched natural failure
cohort was available.

## Sensitivity Boundary

Two valid calibration runs were unusually slow:

- REHYDRATE: `281.61 ms`
- GEOMETRY: `310.94 ms`

They raised the conformal threshold to `18.46` robust scales. This protects
against false warnings but may make the specialist insensitive. The threshold
must not be lowered using clean confirmation outcomes.

## Next Gate

Preregister a bounded delay perturbation ladder for this exact workflow profile
to map detectable effect size. Treat it as an intervention-response diagnostic,
not natural failure recall.

## Claim Boundary

This supports clean profile compatibility and false-warning control only. It
does not prove natural failure detection, production utility, consciousness,
or autonomous authority.
