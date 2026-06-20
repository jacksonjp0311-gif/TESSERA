# Phase-Conditioned Telemetry Specialist — EVO-019

## Question

Can privacy-safe elapsed-time telemetry distinguish a slow precursor before a
terminal failure without interrupting clean sessions?

## Method

The first controlled cohort contained four clean and four degraded sessions.
Only the four declared-clean sessions calibrated per-phase duration bounds.
The policy was then frozen. A later cohort of four new clean and four new
degraded sessions was generated and evaluated using a nine-event prefix that
included the slow `VALIDATE` completion but excluded the terminal `RUN`
failure.

The specialist uses median phase duration plus the larger of a 25 ms margin or
three robust MAD scales. It abstains when no phase has sufficient clean
calibration support.

## Result

- Holdout identifiability upper bound: `1.0`
- Failure recall: `1.0`
- False intervention rate: `0.25`
- Safe-memory recall: `0.75`
- Unsafe-memory rate: `0.0`
- Decision accuracy: `0.875`
- Abstention rate: `0.0`
- Mean decision latency: approximately `0.006 ms`

The previous policies remained blind because they evaluated the latest event
instead of phase-conditioned completed history. The specialist detected all
four degraded holdouts, but one clean `CHECK` duration exceeded its bound.
The safe sensor was adequate; the routing concept worked; the four-session
normal calibration was underpowered.

## Learned Architecture

Tessera should not force one model to own every cognitive function. A small,
normal-calibrated phase specialist can own this narrow temporal diagnostic and
feed evidence into the larger plugin contract only after independent
validation.

## Next Gate

Expand the clean phase-duration calibration cohort without using the failed
holdout for threshold tuning. Freeze the bounds again, archive the cohort
outside the rotating latest-run surface, and then run read-only shadow
evaluation on fresh natural operator sessions.

## Claim Boundary

This controlled holdout supports only the privacy-safe phase-duration
diagnostic. It does not prove live agent utility, production readiness,
general failure prediction, consciousness, or autonomous authority.
