# Local Trajectory Identifiability — EVO-018

## Question

Can phase-conditioned calibration separate clean and degraded seven-event
prefixes in the frozen privacy-sanitized local cohort?

## Audit

Eighteen eligible sessions produced only five unique allowed feature
observations. Two observation groups contained both clean and degraded labels,
covering seven sessions.

- deterministic accuracy upper bound: `0.88889`;
- failure-recall upper bound at zero false intervention: `0.0`;
- both degraded prefixes exactly duplicate at least one clean prefix.

No model or threshold can recover failure recall without false interventions
from these retained features. Phase calibration would only disguise an
information deficit.

## Evolution

The Agent CLI Mirror event contract now emits four privacy-safe fields for
future sessions:

- opaque session ID;
- event index;
- elapsed milliseconds;
- numeric exit code.

Commands, details, paths, prompts, payloads, and raw outputs remain denied by
the capture layer.

The identifiability audit becomes a gate before trajectory-model promotion.

## Decision

The frozen EVO-017 cohort is retired from model tuning. Fresh enriched sessions
must be collected before phase-conditioned calibration or utility evaluation.

## Non-Claim Boundary

Improved telemetry does not authorize live monitoring, payload collection,
memory writes, tool use, or autonomous authority.
