# Runtime Uncertainty Integration — EVO-033

## Objective

Move the supported latent-drift trust router into the supervised plugin
runtime without changing forecasts or weakening containment.

## Host Contract

Every admitted-checkpoint packet can now include:

- `trust_route`: `trusted`, `abstain`, or `not_routed`
- `abstained`: explicit Boolean
- `uncertainty_score`: target-free latent-drift value

An abstained packet cannot become a memory candidate. The stable forecast and
selected expert remain unchanged.

## Runtime Probe

A checkpoint-calibrated event stream exercised both routes:

- trials: `14`
- trusted: `8`
- abstained: `6`
- coverage: `0.5714`
- warm p50: `55.63 ms`
- warm p95: `80.29 ms`
- warm maximum: `90.02 ms`
- budget: `250 ms`

All six runtime checks passed:

- explicit host routes
- unchanged forecast status
- memory suppression on abstention
- both routes observed
- latency gate
- fail-closed route consistency

## Decision

Promote the host-facing runtime routing contract.

Do not claim semantic transfer yet. EVO-032 calibrated session-level routing,
while EVO-033 validates event-stream runtime mechanics. A host adapter must
construct the same session-summary semantic space or receive its own
chronological calibration.

## Production Gap

Core runtime architecture is close to release-candidate quality. Remaining
production blockers are:

1. semantic host adapter for the validated session router;
2. natural failure and recovery utility;
3. two independent host integrations;
4. sustained load, restart, and soak testing;
5. package signing and dependency provenance;
6. external security review and independent reproduction.

## Claim Boundary

Runtime routing mechanics do not establish semantic transfer, natural failure
sensitivity, production readiness, consciousness, or autonomous authority.
