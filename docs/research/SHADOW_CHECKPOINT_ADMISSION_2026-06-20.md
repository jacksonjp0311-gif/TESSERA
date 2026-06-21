# Shadow Checkpoint Admission — EVO-028

## Purpose

EVO-027 made host inference fast by removing fitting from the request path.
EVO-028 adds the separate learning control plane without granting it live
authority.

## Implemented

- asynchronous shadow candidate generation
- write-once JSON checkpoint records
- canonical SHA-256 payload integrity
- explicit lineage and metrics
- replay loss and replay-pass admission gate
- atomic pending-to-active pointer replacement
- injected pre-activation failure preservation
- previous-version pointer and atomic rollback

The trainer can create candidates only. It cannot activate them.

## Probe

The readiness probe passed five of five lifecycle checks:

- shadow job accepted
- candidate produced without activation
- replay-gated admission
- injected failure preserved the active checkpoint
- rollback restored the previous checkpoint

The controlled candidate reduced prediction loss from `2.0` to `0.0`.
Injected activation failure caused zero active-pointer changes, and rollback
succeeded.

## Decision

Promote the checkpoint lifecycle control plane. Do not promote general neural
learning utility or full production readiness.

The next gate is to connect a real Tessera neural checkpoint to this lifecycle,
validate it on held-out agent trajectories, and prove that checkpoint loading
does not break the fast-path latency budget.

## Claim Boundary

Checkpoint integrity and rollback do not prove model utility, production
readiness, safe autonomous learning, consciousness, or host authority.
