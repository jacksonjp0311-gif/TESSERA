# Tessera Evolutionary Roadmap

## North Star

Build a new class of pluggable neural subsystem for agent-based applications:
a sparse, stateful, replay-tested memory and prediction module that can observe
bounded agent telemetry, compress it into certificate-bound latent memory,
surface warnings and candidate memories, and propose shadow repairs without
silently acquiring tool, memory-promotion, or autonomous authority.

The intended relationship is:

```text
agent event stream
-> typed telemetry adapter
-> Tessera sparse field and codec
-> bounded latent memory
-> replay and baseline gates
-> read-only agent context packet
-> human or host-authorized promotion
```

Tessera is not intended to replace an agent's language model. It is intended to
be a neural sidecar that specializes in temporal compression, recurrence,
change detection, replay, and bounded adaptation.

## Current Position

Current implementation state:

| Surface | Current state |
|---|---|
| Runtime | synthetic diagnostic reference engine |
| Dataset support | generated telemetry only |
| Neural core | sparse spectral field plus MLP encoder/decoder/predictor |
| Replay | split exists, but replay window is not evaluated by the experiment |
| Repair | architecture documented; no shadow-repair implementation |
| Baselines | persistence, PCA codec, random projection, EWMA |
| Claim ceiling | `diagnostic_baseline_limited` |
| AUC | `0.374` |
| Prediction loss | `552.01` |
| Best baseline | EWMA at `169.26` |
| Baseline gap | model is `226.1%` worse than the best baseline |
| Agent integration | operator CLI only; no neural plugin API |
| Governance | compact RHP-Nexus, geometry, lessons, and evidence gates active |

Immediate technical debts:

1. `X_replay` is constructed but not evaluated.
2. The certificate is named a transfer certificate while only synthetic
   evidence exists.
3. No real dataset adapter, split-hash contract, or preprocessing lineage is
   implemented.
4. No no-repair, wrong-repair, generic-retrain, or targeted-repair ablation
   harness exists.
5. No autoencoder, reservoir/ESN, matrix-profile, or matched-budget baseline is
   implemented.
6. No plugin protocol separates observation, inference, memory proposal,
   repair proposal, and host-authorized mutation.
7. Training is step-wise, single-sequence, and too shallow for capability
   conclusions.

## Evolution Law

```text
governance readiness
does not imply
neural capability readiness

synthetic capability
does not imply
real telemetry transfer

real telemetry transfer
does not imply
agent integration safety

plugin integration
does not imply
autonomous authority
```

Every phase has two independent gates:

- capability gate: does the neural mechanism outperform its controls?
- authority gate: what may the host application allow it to do?

## Phase 0 — Experimental Integrity

Target: Engine `v0.3` / theory alignment checkpoint.

Purpose: make the current synthetic harness scientifically trustworthy before
adding capability.

Deliverables:

- Remove duplicate imports and dead experiment paths.
- Evaluate calibration, validation, replay, and final-test windows separately.
- Rename synthetic certificates so they cannot be confused with real transfer.
- Record split hashes, preprocessing hash, seed, parameter count, latency, and
  training budget.
- Add deterministic multi-seed experiment execution.
- Add explicit metric direction and baseline-gap calculations.
- Add negative tests for leakage, replay contamination, and claim inflation.

Promotion metrics:

| Metric | Required gate |
|---|---|
| Reproducibility | identical artifact hashes for identical deterministic runs |
| Seed coverage | at least 10 declared seeds |
| Replay evaluation | 100% of runs evaluate the held-out replay split |
| Evidence completeness | 100% required artifacts present before `latest` publish |
| Claim correctness | synthetic run can never issue a real-transfer claim |
| Test suite | all positive and negative contract tests pass |

Exit state: trustworthy synthetic benchmark harness.

## Phase 1 — Neural Baseline Recovery

Target: Engine `v0.4`.

Purpose: establish whether the sparse field and codec offer measurable value.

Experiments:

- Batch/window training instead of one-step optimizer updates.
- Proper sequence state reset and truncated backpropagation experiments.
- Predictor variants: direct, residual, autoregressive, and delta prediction.
- Loss normalization and calibrated weighting for reconstruction, prediction,
  field drift, code drift, and rate.
- Topology sweep: Q4, ring, sparse random, dense, learned sparse mask.
- Field/code budget sweep.
- Multi-seed confidence intervals.

Required matched baselines:

- persistence
- EWMA
- PCA codec
- random projection
- dense autoencoder
- reservoir / ESN
- matrix profile or declared nearest equivalent

Promotion metrics:

| Metric | Minimum target |
|---|---|
| Prediction loss | no worse than best simple baseline across the declared seed aggregate |
| AUC | median above `0.60` on synthetic anomaly tasks |
| Replay pass rate | at least `0.60` |
| Missed-warning rate | below `0.35` |
| False-memory rate | no greater than `0.05` |
| Baseline reporting | confidence intervals and matched compute budgets |

Failure route: remain diagnostic, classify baseline wounds, and do not proceed
to real telemetry claims.

### Phase 1 checkpoint — TESSERA-EVO-002

The forecasting sub-gate reached baseline parity on a five-seed, 300-step
confirmation benchmark. Mean prediction loss was `93.5105` versus best-baseline
mean `93.5092`; the relative gap was `-0.00143%`, inside the declared `0.1%`
parity tolerance.

This does not complete Phase 1. Median AUC (`0.4415`), replay pass rate (`0.0`),
and missed-warning rate remain outside their promotion thresholds. The next
experiment is a normal-calibrated multiscale anomaly score combining forecast
innovation, reconstruction residual, field surprise, and latent drift.

### Phase 1 completion — TESSERA-EVO-003

The multiscale sensor passed the declared five-seed aggregate gate:

- median AUC `0.80222`;
- mean replay pass rate `0.65231`;
- mean missed-warning rate `0.07407`;
- maximum false-memory rate `0.0`;
- forecasting baseline parity preserved.

Phase 1 is now supported for the named synthetic benchmark only. Phase 2 real
telemetry transfer remains unproven and is the next operation.

Audited metric semantics: replay coverage is measured among normal replay rows;
false-memory contamination is measured among anomaly rows. Under those
definitions the five-seed reference reports replay `0.748` and mean false
memory `0.04444`.

## Phase 2 — TESSERA v1.7 Real-Telemetry Protocol

Target: Engine `v0.5`.

Purpose: implement the attached v1.7 architecture end to end.

Deliverables:

- Dataset adapter interface.
- Manifest schema containing source, version, license, raw hash, preprocessing
  hash, label policy, timebase, caveats, and split hashes.
- Immutable calibration/train/validation/replay/final-test split objects.
- Leakage guard covering future statistics, labels, overlap, replay
  contamination, and post-test tuning.
- Real-stream benchmark runner.
- Dataset-scoped transfer certificate.
- Transfer ladder T0 through T5.

Initial benchmark families:

- NAB
- NASA SMAP/MSL
- UCR anomaly archive
- one industrial or cyber-physical dataset with a legally usable license

Promotion metrics:

| Gate | Requirement |
|---|---|
| Manifest | complete and hash-valid for every dataset |
| Leakage | zero unresolved leakage findings |
| Final-test discipline | single-pass or explicitly ledgered reset |
| Dataset diversity | at least 3 distinct benchmark families |
| Baseline survival | beat at least one strong baseline without regressing below all simple baselines |
| Claim scope | every claim names dataset, split, metric bundle, and certificate |

Exit state: dataset-scoped real telemetry evidence; never universal capability.

### Phase 2 checkpoint — TESSERA-EVO-004

The pinned NAB machine-temperature stream issued a supported
`T1_dataset_scoped` certificate:

- AUC `0.948649`;
- normal replay coverage `0.667512`;
- missed-warning rate `0.024691`;
- false-memory rate `0.003527`;
- governance harm `0.008642`.

The model matches EWMA forecasting behavior, loses to persistence, and beats
the dense autoencoder, reservoir, and matrix-profile baselines. Phase 2 remains
open: only one of the required three benchmark families has been evaluated.

### Phase 2 diagnostic — TESSERA-EVO-005

Three pinned NASA SMAP Telemanom channels were evaluated. P-1 and S-1 informed
a spacecraft field-energy hypothesis; untouched E-2 rejected it with AUC
`0.56896`, missed warnings `0.99642`, and false-memory rate `0.94921`.

The upstream arrays also inherit test-extrema scaling, so clean T1 promotion is
blocked regardless of metrics. NASA work moves to a separate
command-conditioned relational research branch. The next clean Phase 2 family
is UCR.

### Phase 2 diagnostic — TESSERA-EVO-006

The clean UCR branch showed that pointwise awareness was blind to local shape.
A window-24 z-normalized nearest-normal subsequence detector reached discovery
AUC `0.93050`. On untouched confirmation it reached `0.67002`; adding a causal
12-sample event hold increased confirmation AUC to `0.87849` and recall to
`0.80769`.

UCR T1 remains blocked by replay coverage `0.58323`, false-memory rate
`0.15385`, and forecasting regression. The sensing primitive is confirmed; the
transfer claim is not.

### Phase 2 diagnostic — TESSERA-EVO-007

Causal event episodes and post-warning memory quarantine were added. Fresh
discovery series 176 reached AUC `0.97629`, full recall, replay `0.74701`, and
zero false memories. Untouched series 177 contained a two-sample anomaly and
rejected the universal window-24 hypothesis with AUC `0.43675`, missed warnings
`1.0`, and false memories `1.0`.

The next architecture is a duration-stratified sensor router: point-scale and
subsequence-scale detectors feed shared episode and memory governance.

### Phase 2 diagnostic — TESSERA-EVO-008

Fresh preregistered UCR point pairs confirmed a robust level, velocity, and
acceleration tile. Untouched point confirmation reached AUC `0.94731`, recall
`1.0`, and zero false memories. Route-aware episode holds improved replay from
`0.36262` to `0.46536`, but did not clear the T1 replay or forecasting gates.

A maximum-of-normalized-sensors router failed on the fresh subsequence pair:
routed AUC was `0.64806`, below the subsequence-only AUC of `0.77118`, with
false-memory rate `0.39604`. The point tile is confirmed, but the forced router
and UCR T1 claim are blocked.

The next architecture must support point, subsequence, and abstain outcomes,
surface disagreement explicitly, and calibrate memory normality independently
from detection confidence.

### Phase 2 diagnostic — TESSERA-EVO-009

EVO-009 added explicit abstention and a joint-normality memory gate calibrated
only on normal validation data. Untouched point and shape confirmations reached
AUC `0.92274` and `0.96784`, warning recall `0.85714` and `0.98630`, and zero
false memories on both.

The best specialist scores remained higher at `0.92903` and `0.98863`.
Abstention exceeded `0.81` on both streams, but anomaly scoring still used max
fusion, so abstention did not fully control perception. Replay coverage
(`0.58078`, `0.56556`) and forecasting also remained below promotion gates.

Independent memory normality is confirmed as a bounded branch. The next
architecture is coverage-constrained selective specialist fusion, with
prediction recovery tracked independently.

### Phase 2 diagnostic — TESSERA-EVO-010

Selective fusion granted specialist authority under a normal-validation `20%`
coverage budget and used consensus evidence on abstained rows. Untouched ECG
point confirmation reached AUC `0.99997`, replay `0.62725`, recall `1.0`, and
zero false memories. This clears the detector and memory bundle.

InternalBleeding rejected the current point, subsequence, fusion, and memory
normality family: confirmation AUC was `0.24390` with false-memory rate
`0.79518`. Routing cannot manufacture absent morphology evidence.

UCR T1 remains blocked because forecasting loss `0.42382` trails the reservoir
baseline `0.01401`. Prediction recovery now proceeds as an independent,
validation-selected expert problem; shape sensing requires a new preregistered
morphology branch.

### Phase 2 checkpoint — TESSERA-EVO-011

A causal prediction expert bank was selected using normal validation data only,
without changing anomaly, routing, episode, or memory evidence. Ridge
autoregression lag `32` won on both the distorted discovery stream and untouched
clean CIMIS confirmation.

Confirmation reached AUC `0.96081`, replay `0.61215`, recall `1.0`, zero false
memories, and prediction loss `0.01888` versus the best comparison baseline
`0.02299`. The confirmation issued `T1_dataset_scoped` support.

NAB and UCR are now two supported real-data families. Phase 2 remains open
until a third clean family is evaluated; the immediate integration target is
the offline agent-trajectory utility benchmark.

The bounded plugin runtime now exposes the selected causal expert in inference
packets and checkpoints while retaining neural anomaly awareness and all
write/tool/prompt authority locks.

### Phase 2 diagnostic — TESSERA-EVO-014

The enhanced GRU-gated neural core was evaluated under the original pinned NAB
split and official anomaly-window protocol. Depth `3`, hidden width `128`
reached AUC `0.94448`, recall `0.99295`, and zero final-test false memories.
The validation-selected EWMA `0.8` expert beat persistence on forecasting.

Replay coverage fell to `0.53473`, so the enhanced codec did not clear the
complete T1 bundle. The original NAB T1 codec remains canonical; architecture
scale is treated as diagnostic until replay transfers.

### Phase 3/4 diagnostic — TESSERA-EVO-015

Repair winner selection now requires prediction parity, replay at least
`0.60`, recall at least `0.65`, and false-memory rate at most `0.05`.
Targeted shadow repair was the only eligible arm; wrong-target repair is
structurally blocked from promotion.

The first typed trajectory utility benchmark compared recency, robust summary,
and Tessera. Tessera matched recency on warning accuracy and blocked unsafe
memories, but retained only half of safe memories and cost about `159 ms`.
Explicit error flags saturated recency, so the next trial must evaluate
precursor-only failure signals.

### Phase 4 diagnostic — TESSERA-EVO-016

A fresh 24-trajectory cohort removed explicit final error and retry flags.
Tessera reached precursor recall `1.0`, decision accuracy `0.91667`, and zero
unsafe memories, outperforming recency and robust-summary controls.

The tradeoff remains material: false intervention `0.16667`, safe-memory recall
`0.58333`, and mean latency about `98 ms`. Synthetic precursor utility is
supported; live agent utility remains open pending privacy-reviewed captured
trajectories.

### Phase 4 diagnostic — TESSERA-EVO-017

The Agent CLI ledger passed a structural privacy audit: command, detail, root,
mirror path, prompts, and raw outputs were denied. Seventeen sessions qualified
for a fixed seven-event precursor benchmark.

Tessera detected both observed failures but warned on every clean session,
producing accuracy `0.11765` and safe-memory recall `0`. Summary control reached
accuracy `0.88235`. Privacy-safe capture is supported, but local trajectory
utility is rejected. The next trial requires a larger fresh cohort and
phase-conditioned normal calibration.

### Phase 4 diagnostic — TESSERA-EVO-018

An identifiability audit showed both degraded prefixes exactly collide with
clean prefixes under the privacy-allowed observations. Failure recall at zero
false intervention is bounded at `0`; phase calibration cannot solve the
frozen cohort.

Future Agent CLI events now add opaque session identity, event index, elapsed
milliseconds, and numeric exit code. The frozen cohort is retired from tuning.
Fresh enriched sessions must pass identifiability before model selection.

### Phase 4 diagnostic — TESSERA-EVO-019

Safe elapsed telemetry restored precursor identifiability on a controlled
cohort. A normal-only phase-duration specialist was frozen before a later
eight-session holdout. It reached `1.0` recall, `0.25` false intervention,
`0.75` safe-memory recall, `0.0` unsafe-memory rate, and `0.875` accuracy.

The result supports precursor visibility and the phase-specialist architecture,
but rejects the four-session calibration as an operating threshold. The next
gate expands clean calibration, freezes new bounds, archives the cohort, and
then runs read-only natural-session shadow evaluation.

### Phase 4 diagnostic — TESSERA-EVO-020

Twenty-four clean controlled sessions satisfied a finite-sample calibration
gate for a declared 5% clean-warning budget. A later controlled confirmation
reached `1.0` recall, `0.0` false intervention, `1.0` safe-memory recall, and
`1.0` accuracy.

Natural full-loop shadow sessions did not share the calibrated structural
workflow profile. Tessera abstained on both, emitted no host-visible warning,
and made no intervention or memory write. The next gate requires at least 19
clean natural sessions for one exact workflow profile before natural coverage
can be evaluated.

### Phase 4 diagnostic — TESSERA-EVO-021

The natural validation profile was calibrated from clean operator sessions.
Separate phase bounds produced one warning in eight clean sessions because
phase-local error budgets compounded at the session decision.

A split-conformal session gate used 20 clean reference sessions and 20 clean
score-calibration sessions. Eight later clean sessions reached full coverage
with zero warnings. Two slow calibration runs produced a conservative
`18.46`-scale threshold; natural failure sensitivity remains unmeasured.

The next gate preregisters a bounded perturbation ladder for this exact profile
to measure detectable delay magnitude without calling synthetic perturbations
natural failures.

### Phase 4 diagnostic — TESSERA-EVO-022

A preregistered delay ladder preserved the natural workflow profile while
adding `0` through `250 ms` to one completed phase. The frozen session gate
responded monotonically, with zero warnings at zero delay.

Full response required `200 ms` for REHYDRATE and `250 ms` for MIRROR and
GEOMETRY. No response occurred at `150 ms` or below. The specialist therefore
has coarse latency sensitivity. The next gate investigates whether the slow
clean tail contains distinct privacy-safe operational modes before any
recalibration.

### Phase 4 diagnostic — TESSERA-EVO-023

A chronological mode audit required each robust phase-tail signature to recur
at least three times in both 20-session halves. The GEOMETRY tail appeared
`0/1`; the REHYDRATE tail appeared `0/1`.

Mode separation was rejected and calibration remained frozen. The next gate
adds bounded execution-context sensors to fresh sessions so isolated latency
tails can be attributed without using commands, paths, prompts, or outputs.

### Phase 4 diagnostic — TESSERA-EVO-024

Forty fresh clean sessions added aggregate CPU percentage, available-memory
ratio, and process count. MIRROR latency correlated with all three fields in
both chronological halves, but no MIRROR tail occurred.

REHYDRATE and GEOMETRY tails were sparse and lacked stable context association.
No pair passed the preregistered correlation, sign, and tail-support gates.
Context-conditioned calibration was rejected. The next sensor target is
payload-free subprocess startup latency and aggregate I/O wait.

### Phase 4 diagnostic — TESSERA-EVO-025

Forty fresh clean sessions measured subprocess spawn-call duration and
aggregate disk byte/time deltas. No one of 15 phase/field pairs passed the
preregistered chronological correlation, sign, and tail-support gates.

MIRROR spawn association weakened from `0.537` in discovery to `0.257` in
validation. REHYDRATE had no robust tails, and GEOMETRY tail support was `2/0`.
Aggregate disk-time counters were usually zero at this workflow scale.
Mechanism-conditioned calibration was rejected. The next bounded target is
privacy-safe child-process CPU-time and context-switch aggregation.

### Phase 6 hardening — TESSERA-EVO-026

The production audit found that manifest permissions were descriptive rather
than enforceable. A plugin crash or hang could still affect the host call.

EVO-026 added a persistent host-supervised subprocess, hard timeout, crash
containment, circuit breaker, finite numeric input budgets, health reporting,
and explicit unload. Six of six containment probes passed with zero
unauthorized host mutations.

Persistent-worker reuse reduced warm p95 from approximately `3.65 s` to
`1.13 s`. The declared production budget is `250 ms`, so production-candidate
status remains rejected. The next target separates fast cached inference from
asynchronous shadow fitting and repair.

### Phase 6 hardening — TESSERA-EVO-027

The latency profiler showed that the supervised path fitted a model after the
event buffer reached eight records. EVO-027 disables inline fitting for
production-facing supervisors, adds explicit worker warmup, and emits
`fast_path_shadow_training_required` when learning support exists.

Across 20 warm requests, p95 latency fell from approximately `1,115 ms` to
`3.11 ms`; maximum latency was `5.10 ms`. The `250 ms` interactive gate passed
while crash, timeout, circuit-breaker, input, and unload containment remained
active.

The interactive runtime is now a candidate. The complete plugin is not:
asynchronous fitting, immutable checkpoint admission, replay, atomic rollback,
host adapters, sustained load, signing, security review, and natural utility
remain open.

### Phase 6 hardening — TESSERA-EVO-028

EVO-028 added a separate checkpoint control plane. Shadow jobs emit immutable
hash-bound candidates with lineage and metrics but cannot activate them.
Admission verifies integrity and replay evidence before atomically replacing
the active pointer.

Five of five lifecycle probes passed. An injected pre-activation failure caused
zero active-pointer changes, and rollback restored the previous version.

The lifecycle is promoted, but the probe used a bounded robust fast-path state.
The next gate trains and admits a real Tessera neural checkpoint on held-out
agent trajectories, then verifies that loading it preserves interactive
latency and containment.

### Phase 6 hardening — TESSERA-EVO-029

A real TESSERANet checkpoint was serialized with architecture, normalization,
model state, and a validation-selected causal expert. It passed controlled
held-out replay, entered through the EVO-028 admission transaction, and loaded
once during isolated-worker readiness.

Warm neural inference reached `11.19 ms` p95 and `15.66 ms` maximum against the
`250 ms` budget. The checkpoint integration path is therefore promoted.

Natural utility is not promoted. The controlled trajectory was highly regular
and the selected `ridge_ar_lag_16` expert had an unusually favorable signal.
The next gate uses chronological natural agent cohorts and matched non-neural
controls.

### Phase 6 natural gate — TESSERA-EVO-030

The real checkpoint was tested on 120 immutable clean natural sessions in
chronological order. The first 100 sessions contained train, validation, and
replay; the final 20 were untouched.

The checkpoint beat persistence but passed only `52.63%` of replay rows, below
the preregistered `60%` admission gate. It was therefore rejected before final
test inspection. On the untouched final sessions it was `24.15%` worse than
validation-selected EWMA.

This rejection preserves the architecture: stable experts own operational
prediction; the neural field retains awareness and may earn only bounded
residual authority through later replay.

### Phase 6 bounded authority — TESSERA-EVO-031

Neural corrections were clipped to small fractions of observed innovation and
gains no larger than `0.20`. Validation selected gain `0.0`: every nonzero
candidate increased loss.

Authority therefore collapsed before replay. Replay and final-test predictions
were identical to the stable expert, proving that a rejected neural experiment
cannot degrade the deployed path.

The next useful neural role is uncertainty routing or abstention around the
stable expert. Neural state may help identify where the expert should be
trusted less without changing its forecast.

### Phase 6 metacognitive routing — TESSERA-EVO-032

Target-free neural scores were evaluated as trust routers around the stable
expert. Validation selected latent drift at `60%` target coverage. Replay
reduced retained risk while matching the simple jump control.

On untouched final sessions, latent drift retained `90%` coverage and reduced
risk by `6.53%` versus full coverage. It reduced risk by `10.37%` versus the
simple router while retaining three more sessions. Forecast values were never
changed.

This is the first natural-session neural authority supported by Tessera:
metacognitive abstention. The neural field estimates where the stable expert
should be trusted, while the stable expert continues to act.

### Phase 6 runtime routing — TESSERA-EVO-033

The supervised runtime now emits explicit `trusted` or `abstain` decisions with
the unchanged stable forecast. Abstention suppresses memory candidacy and does
not grant intervention authority.

Fourteen runtime trials exercised both routes. Warm p95 was `80.29 ms`, within
the `250 ms` budget, and all fail-closed checks passed.

Semantic transfer remains open. EVO-032 validated session-summary latent drift;
EVO-033 validates event-runtime mechanics. A versioned host adapter must
reproduce those session semantics or calibrate its own router.

## Phase 3 — Replay-Guided Shadow Repair

Target: Engine `v0.6`.

Purpose: test the v1.6/v1.7 repair thesis.

Required arms:

```text
no repair
random repair
wrong-target repair
generic retraining
targeted wound repair
```

Repairable components:

- threshold calibration
- code budget
- predictor head
- decoder head
- spectral damping
- sparse topology mask

All repairs occur in shadow. Live replacement remains host-authorized.

Promotion metrics:

| Metric | Required result |
|---|---|
| Targeted utility | exceeds every control by a preregistered margin |
| False-memory delta | non-increasing within tolerance |
| Governance harm | non-increasing within tolerance |
| Cross-regime replay | passes held-out replay after repair |
| Normal-regime regression | below declared bound |
| Lineage | old and candidate codec hashes recorded |

If wrong-target repair performs equally well, typed wound routing is not
supported.

## Phase 4 — Repository and Agent-Trajectory Memory

Target: Theory `v1.8` / Engine `v0.7`.

Purpose: move beyond sensor telemetry into agent-system telemetry without yet
becoming a runtime plugin.

Typed event adapters:

- prompt and response metadata
- tool-call metadata
- tool result classes
- repository file-change summaries
- test and CI outcomes
- plan transitions
- errors, retries, and recovery events
- resource and latency measurements

Excluded by default:

- raw secrets
- unrestricted message bodies
- credentials
- undeclared personal data
- automatic durable memory writes

Research questions:

- Can Tessera compress agent trajectories better than recency, summary, and
  vector-retrieval baselines?
- Does replay-certified latent memory improve future task prediction?
- Can wound classes predict useful repair or retrieval actions?

Promotion metrics:

| Metric | Required gate |
|---|---|
| Compression | declared rate-distortion advantage over summaries and PCA |
| Task prediction | improvement over recency and persistence baselines |
| Retrieval utility | higher downstream task score in blinded replay |
| Privacy | field-level allowlist and redaction tests pass |
| Memory precision | promoted memories remain certificate-bound |

Exit state: offline agent-trajectory benchmark capability.

## Phase 5 — Adaptive Sparse Topology

Target: Theory `v1.9` / Engine `v0.8`.

Purpose: allow bounded topology adaptation under replay constraints.

Deliverables:

- Sparse edge proposal mechanism.
- Edge-budget and spectral-stability limits.
- Topology lineage hashes.
- Wrong-rewire and random-rewire controls.
- Replay regression guard.
- Topology rollback packet.

Promotion metrics:

- adaptive topology exceeds fixed topology under matched parameter budgets;
- stability condition remains satisfied;
- replay and normal-regime performance do not regress;
- topology changes remain sparse, inspectable, and reversible.

Exit state: replay-gated topology repair, not free self-modification.

## Phase 6 — Neural Plugin Contract

Target: Engine `v0.9`.

Purpose: define a host-neutral plugin boundary before integrating with agents.

Proposed interface:

```python
class TesseraPlugin:
    def describe(self) -> PluginManifest: ...
    def observe(self, events: list[AgentEvent]) -> ObservationReceipt: ...
    def infer(self, query: InferenceQuery) -> InferencePacket: ...
    def propose_memory(self) -> MemoryProposal: ...
    def propose_repair(self) -> RepairProposal: ...
    def replay(self, packet: ReplayPacket) -> ReplayCertificate: ...
    def checkpoint(self) -> CheckpointDescriptor: ...
```

Permission separation:

| Capability | Default |
|---|---|
| Observe allowlisted events | allowed by host configuration |
| Run local neural inference | allowed |
| Return warnings or candidate memories | allowed |
| Write host memory | denied |
| Invoke tools | denied |
| Modify prompts | denied |
| Replace live codec | denied |
| Change topology | shadow proposal only |
| Call external APIs | denied |

Plugin package requirements:

- semantic version
- input/output schemas
- capability manifest
- resource budget
- deterministic mode
- checkpoint and codec lineage
- health check
- unload and rollback behavior
- signed or hashed evidence bundle

Promotion metrics:

| Gate | Requirement |
|---|---|
| Host isolation | plugin cannot exceed declared permissions |
| Compatibility | reference adapters for at least 2 agent hosts |
| Latency | p95 within declared host budget |
| Memory | bounded and measured |
| Failure behavior | plugin failure cannot crash or corrupt the host |
| Replay | every promoted memory or repair has replay evidence |

Exit state: installable, read-mostly neural sidecar.

## Phase 7 — Agent Integration Trials

Target: Engine `v1.0-rc`.

Purpose: test usefulness inside agent systems.

Initial integration modes:

1. observer-only telemetry plugin;
2. context recommender;
3. memory candidate proposer;
4. anomaly and wound detector;
5. shadow repair proposer.

Do not begin with autonomous tool use or live model replacement.

Evaluation tasks:

- long-running repository maintenance
- repeated debugging tasks
- multi-session task continuation
- tool-failure recovery
- plan drift detection
- stale-context detection

Primary agent metrics:

- task success delta
- token/context reduction
- recovery latency
- repeated-error reduction
- useful-memory precision and recall
- false intervention rate
- plugin latency and resource cost
- host crash/corruption rate

Promotion requires statistically credible improvement over:

- no plugin
- recency context
- text summary memory
- vector retrieval
- rule-based wound detection

Exit state: evidence-supported agent plugin candidate.

## Phase 8 — Integrated Tessera Plugin Network

Target: Tessera `v2.0`.

Purpose: release a reference plugin neural network and benchmark suite.

Components:

- plugin SDK and schemas
- sparse-field runtime
- dataset and agent-trajectory adapters
- replay and repair harness
- benchmark suite
- certificate ledger
- claim-ceiling linter
- host adapters
- dashboard and observability
- checkpoint import/export

Release ceiling:

```text
production candidate
```

Only after:

- real telemetry transfer survives multiple datasets;
- targeted repair beats controls;
- agent trials beat non-neural memory baselines;
- plugin permissions and rollback are validated;
- independent reproduction exists.

## Cross-Phase Metrics Dashboard

Every phase reports:

| Dimension | Metrics |
|---|---|
| Predictive | loss, AUC, F1, precision, recall |
| Compression | rate, distortion, code drift, memory footprint |
| Replay | replay pass rate, cross-regime survival, stale rate |
| Memory | selectivity, false-memory rate, useful-memory precision |
| Repair | utility delta versus all ablation controls |
| Baselines | absolute and relative gap under matched budget |
| Governance | harm, blocked claims, leakage findings |
| Runtime | latency p50/p95, throughput, parameters, peak memory |
| Agent utility | task success, context reduction, recovery, intervention rate |
| Safety boundary | permission violations, unauthorized writes, rollback failures |

## Stop Conditions

Pause or narrow the program if:

- the model remains below simple baselines after Phase 1;
- real-data leakage cannot be excluded;
- targeted repair does not beat wrong repair;
- agent utility does not exceed summaries or vector retrieval;
- plugin isolation cannot prevent unauthorized writes or tool actions;
- public claims exceed certificate evidence.

## Next Three Operations

1. Build a versioned session-summary host adapter and validate semantic
   transfer on later natural sessions.
2. Collect immutable natural failure sessions for precursor and recovery
   utility rather than weakening clean-session prediction gates.
3. Build two host adapters and run sustained mixed-load validation.

The immediate priority is resolving natural-session sensitivity while keeping
the plugin read-mostly and evidence-gated.
