# Plugin Runtime Containment — EVO-026

## Production Audit

The EVO-025 plugin declared denied permissions, but declarations alone did not
protect a host from an inference crash, hang, malformed numeric input, or
unbounded lifecycle.

The highest-impact production gap was therefore execution containment rather
than another model feature.

## Implemented Boundary

EVO-026 adds a host-supervised local subprocess runtime with:

- hard inference timeout and worker termination
- crash containment with proposal suppression
- consecutive-failure circuit breaker
- finite numeric input and feature-budget validation
- explicit health reporting
- explicit unload and fail-closed behavior
- persistent worker reuse to amortize Python and neural-stack startup

No contained failure emits a warning, memory proposal, repair proposal, tool
call, or host mutation.

## Measured Result

The local readiness probe passed all six containment checks:

- normal subprocess inference
- worker crash containment
- circuit-breaker closure
- hard-timeout containment
- nonfinite telemetry rejection
- unload closure

Crash and timeout containment were `1.0`, with zero unauthorized host
mutations in the probe.

Persistent worker reuse reduced the previously observed disposable-worker warm
latency from approximately `3.65 s` to approximately `1.13 s` p95.

## Production Decision

The containment boundary is promoted. Production-candidate status is rejected.

Warm inference remains above the declared `250 ms` interactive host budget.
Additional blockers include two independent host adapters, sustained load,
cross-platform validation, package signing, natural agent-task utility, and
external security review.

## Next Gate

Separate fast inference from model fitting. Cache immutable model state in the
worker and move retraining or topology repair to an asynchronous shadow path.
Then measure latency under sustained mixed fallback/neural load.

## Claim Boundary

Local containment is not production readiness, safety certification, useful
agent memory, consciousness, or autonomous authority.
