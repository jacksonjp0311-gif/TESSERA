# Natural Tail Mode Audit — EVO-023

## Question

Do the slow clean sessions represent a repeatable operational mode that should
receive separate calibration?

## Method

The 40-session clean calibration cohort was split chronologically into 20
discovery and 20 validation sessions. A phase entered a tail signature when its
robust score exceeded `6`. A candidate mode required the same phase signature
at least three times in both halves.

Valid slow sessions could not be removed, relabeled, or used to lower the
existing threshold.

## Result

Two candidate signatures appeared:

| Signature | Discovery | Validation |
|---|---:|---:|
| GEOMETRY tail | 0 | 1 |
| REHYDRATE tail | 0 | 1 |

No mode met recurrence requirements. Mode separation was rejected and the
frozen calibration was not changed.

## Interpretation

The evidence supports isolated tail events, not a stable second operating
regime. Splitting modes would overfit two observations and manufacture apparent
sensitivity.

## Next Gate

Add narrowly allowlisted execution-context telemetry that can help distinguish
resource contention from phase-specific degradation without exposing commands,
paths, prompts, or raw outputs. Collect fresh sessions before attribution.

## Claim Boundary

This audit does not identify tail causes, natural failures, production
incidents, consciousness, or autonomous authority.
