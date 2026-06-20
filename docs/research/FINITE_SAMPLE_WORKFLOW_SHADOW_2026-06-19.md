# Finite-Sample Workflow Shadow — EVO-020

## Question

Can Tessera stabilize the controlled phase specialist without pretending that
the resulting thresholds transfer to structurally different operator loops?

## Method

Twenty-four new clean controlled sessions were archived before confirmation.
For a declared clean false-warning budget of `0.05`, finite-sample rank
calibration requires at least 19 observations per phase. The policy uses the
appropriate upper order statistic plus a fixed 10 ms execution-jitter guard.

Calibration is also bound to a privacy-safe workflow profile: a truncated hash
of the ordered phase/state structure. Commands, details, paths, prompts, and
raw outputs are not retained.

After calibration was frozen, four clean and four degraded controlled sessions
formed an untouched confirmation cohort. Two pre-existing full-loop sessions
formed a natural read-only shadow cohort.

## Result

Controlled confirmation:

- coverage: `1.0`
- failure recall: `1.0`
- false intervention: `0.0`
- safe-memory recall: `1.0`
- unsafe-memory rate: `0.0`
- decision accuracy: `1.0`

Natural shadow:

- sessions: `2`
- coverage: `0.0`
- abstention: `1.0`
- host warnings or interventions: `0`

Both natural sessions had the same uncalibrated structural workflow profile,
so the specialist abstained rather than applying controlled probe thresholds.

## Learned Architecture

Calibration belongs to a semantic workflow domain, not merely a phase name.
Specialists must prove both sufficient normal support and workflow-profile
compatibility before producing a covered decision.

## Next Gate

Collect at least 19 clean sessions for one natural workflow profile, archive
them immutably, freeze its profile-specific bounds, and evaluate a later
natural shadow cohort without host-visible warnings.

## Claim Boundary

This confirms one controlled workflow specialist and safe abstention on an
uncalibrated natural workflow. It does not establish live agent utility,
production readiness, general failure prediction, consciousness, or autonomy.
