# Neural Checkpoint Runtime — EVO-029

## Objective

Connect a real Tessera neural model to the EVO-028 checkpoint lifecycle without
reintroducing synchronous fitting or breaking the interactive latency budget.

## Checkpoint

The candidate contains:

- serialized TESSERANet state
- architecture and sparse topology parameters
- training-only normalization state
- validation-selected causal prediction expert
- train, validation, and held-out replay metrics
- immutable hash and lineage supplied by the checkpoint store

The neural field supplies awareness state. The validated causal expert owns
operational next-step prediction.

## Result

On a controlled 72-event trajectory:

- baseline replay loss: `0.00046382`
- candidate replay loss: `5.11e-12`
- replay pass rate: `1.0`
- selected expert: `ridge_ar_lag_16`
- warm neural inference p95: `11.19 ms`
- warm neural inference maximum: `15.66 ms`
- latency budget: `250 ms`

The checkpoint passed replay, was admitted, loaded during isolated-worker
readiness, and served 20 neural requests without fitting on the host path.

## Decision

Promote the neural checkpoint integration path. Do not claim natural agent
utility: the controlled trajectory is highly regular and favorable to an
autoregressive expert.

The next gate is immutable natural trajectory cohorts with chronological
train, validation, replay, and final-test separation, compared against
persistence, summaries, and non-neural retrieval controls.

## Claim Boundary

Controlled replay success does not establish general transfer, production
readiness, useful agent memory, consciousness, or autonomous authority.
