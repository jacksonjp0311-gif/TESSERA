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
- `docs/schemas/plugin_manifest.schema.json`

## Invariants

- Sensitive events are rejected.
- Tool invocation, host-memory writes, prompt mutation, live codec replacement,
  topology mutation, and external API calls are denied by default.
- Repair proposals remain shadow-only.
- Replay never authorizes promotion by itself.
- Operational prediction may use a normal-history-selected causal expert while
  neural field loss remains separately visible for anomaly awareness.

## Claim Boundary

This is a local prototype. It is not validated agent capability, production
readiness, autonomous authority, or a replacement language model.
