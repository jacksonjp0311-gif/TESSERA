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
- Persistent workers bind PyTorch compute to one CPU thread by default so
  concurrent host workloads do not create unbounded inference contention.
- Identical admitted-checkpoint queries reuse an exact packet keyed by the
  normalized matrix shape and bytes; any event change invalidates the key.
- Byte-identical historical prefixes reuse recurrent field, level, previous
  code, last observation, and metric-row state. Any historical mismatch
  forces full replay.
- Restart capsules integrity-bind the checkpoint, contracts, normalized
  prefix, recurrent state, metric rows, and packet before restoration.
- Crossing the neural-support threshold emits a shadow-training-required
  status while the bounded fast path continues serving the host.
- Direct research-mode plugin instances may still run inline neural fitting.
- Shadow trainers emit immutable checkpoint candidates only.
- Checkpoint activation requires payload integrity and replay gates.
- Active versions change through atomic pointers with preserved rollback.
- Admitted checkpoints may contain a serialized TESSERANet and causal expert.
- The persistent worker loads admitted neural state once during readiness.
- Operational prediction may use a normal-history-selected causal expert while
  neural field loss remains separately visible for anomaly awareness.
- Versioned session adapters preserve the calibrated mean/std/latest semantic
  space across native AgentEvent and JSON host records.
- A deterministic host-owned incident governor latches abstention after an
  observed failure and requires clean terminal recovery before release.
- Agent CLI Mirror and Hermes stream integrations map distinct host contracts
  into the shared session schema while discarding commands, text, arguments,
  previews, paths, and user identifiers.
- Effective-rank selection removes constant coordinates introduced by numeric
  variance noise; host trust requires full support of the resulting manifold.
- A fingerprinted manifold contract monitors support, intrinsic rank,
  principal angle, robust location, and scale across completed-session
  windows; drift forces abstention and suppresses memory candidacy.
- A fingerprinted sequential contract accumulates clipped orthogonal
  nonconformity. Persistent evidence latches abstention while one isolated
  impulse is prevented from acquiring unlimited influence.
- Release verification builds and integrity-checks the wheel, installs it into
  an isolated environment, and executes packaged inference and CLI smoke tests.

## Claim Boundary

Containment, semantic route parity, warm latency, sustained load, restart,
rollback, wheel integrity, isolated package installation, and packaged smoke
execution are locally validated. Untouched natural failure/recovery evidence,
independent hosts, independent package reproduction, cross-platform
certification, and external security review remain open.
