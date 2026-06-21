# Tessera Neural Plugin

## Specification

Host-neutral sparse-neural sidecar prototype for allowlisted agent telemetry,
local inference, memory proposals, replay certificates, and shadow repair
proposals.

## Hooks

- Inbound: typed `AgentEvent` telemetry
- Outbound: inference, memory proposal, repair proposal, replay certificate

## Artifacts

- `contracts.py`
- `trajectory.py`
- `runtime.py`
- `supervisor.py`
- `docs/schemas/plugin_manifest.schema.json`

## Invariants

- Sensitive events are rejected.
- Tool invocation, host-memory writes, prompt mutation, live codec replacement,
  topology mutation, and external API calls are denied by default.
- Repair proposals remain shadow-only.
- Replay never authorizes promotion by itself.
- Production-facing inference runs behind a supervised local subprocess.
- Crashes and hard timeouts fail closed and emit no proposals.
- Repeated failures open a circuit breaker.
- Unload clears buffered events and permanently closes that runtime instance.
- Supervised host inference disables inline neural fitting by default.
- Crossing the neural-support threshold emits a shadow-training-required
  status while the bounded fast path continues serving the host.
- Direct research-mode plugin instances may still run inline neural fitting.
- Shadow trainers emit immutable checkpoint candidates only.
- Checkpoint activation requires payload integrity and replay gates.
- Active versions change through atomic pointers with preserved rollback.
- Operational prediction may use a normal-history-selected causal expert while
  neural field loss remains separately visible for anomaly awareness.

## Claim Boundary

Containment and warm interactive latency are locally validated. Asynchronous
checkpoint lifecycle is locally validated, but real neural checkpoint utility,
host compatibility, load, signing, security review, and natural agent utility
still block production readiness.
