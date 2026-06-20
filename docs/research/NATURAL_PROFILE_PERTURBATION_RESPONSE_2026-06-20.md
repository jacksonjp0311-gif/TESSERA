# Natural Profile Perturbation Response — EVO-022

## Method

Before execution, EVO-022 fixed:

- phases: MIRROR, REHYDRATE, GEOMETRY
- delay levels: `0, 25, 50, 100, 150, 200, 250 ms`
- base cohort: eight untouched clean natural-profile sessions
- calibration: frozen EVO-021 split-conformal session gate

The injection changes only completed phase duration. Phase/state structure and
workflow profile remain unchanged.

## Result

| Phase | First any detection | First full detection |
|---|---:|---:|
| MIRROR | 250 ms | 250 ms |
| REHYDRATE | 200 ms | 200 ms |
| GEOMETRY | 250 ms | 250 ms |

All phase response curves were monotonic. Zero-delay warning rate was `0`.
No phase responded at `150 ms` or below.

## Interpretation

The frozen specialist can detect severe isolated latency increases, but its
calibration tail makes it insensitive to moderate delays. The result maps
detector response; it does not measure natural incident recall.

## Next Gate

Investigate whether the slow clean calibration sessions represent repeatable
operational modes rather than one exchangeable distribution. Any mode split
must be defined from privacy-safe pre-decision structure and validated on later
clean cohorts before recalibrating sensitivity.

## Claim Boundary

Injected delay response is not natural failure prediction, causal diagnosis,
production utility, consciousness, or autonomous authority.
