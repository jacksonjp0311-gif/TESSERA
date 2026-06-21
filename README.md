<div align="center">

# Tessera

### Sparse compressive memory engine with replay-certified memory and RCC Nexus discipline.

**Declare the graph. Compress the stream. Replay every memory. Wound every failure. Repair only in shadow. Validate before mutation. Claim only what transfers.**

![Operator Surface](https://img.shields.io/badge/Operator%20Surface-v0.3.9-blue)
![RCC-N](https://img.shields.io/badge/RCC--N-Full-brightgreen)
![README Discipline](https://img.shields.io/badge/README%20discipline-passing-brightgreen)
![Alignment](https://img.shields.io/badge/alignment-geometry--guarded-brightgreen)
![Claim Ceiling](https://img.shields.io/badge/claim%20ceiling-one--dataset--T1--supported-blue)
![Non-Claim](https://img.shields.io/badge/non--claim--locks-active-black)

</div>

---

## What Tessera Is

Tessera is a local-first Python reference engine for sparse compressive memory. It tests whether a sparse spectral field can compress telemetry into latent codes, reconstruct and predict the stream, gate candidate memories, replay those memories, record wounds, compare against simple baselines, and emit certificate-bound evidence packages.

Tessera is built to answer one engineering question:

```text
What is this compressed telemetry state allowed to become next?
```

## Current Health Snapshot

| Surface | Current result |
|---|---:|
| Repository | `Tessera` |
| Package / CLI | `tessera` v0.2.0 |
| Diagnostic engine | Engine v0.1 |
| Operator surface | v0.3.9 Agent CLI Mirror Graceful Stop |
| Command registry | `docs/loop/TESSERA_COMMAND_REGISTRY.md` |
| Loopbook | `docs/loop/TESSERA_LOOPBOOK.md` |
| Failure lessons chart | `docs/loop/TESSERA_FAILURE_LESSONS.md` |
| Operator loop chart | `docs/loop/TESSERA_OPERATOR_LOOP_CHART.md` |
| Alignment geometry gap | `docs/alignment/TESSERA_ALIGNMENT_GEOMETRY_GAP.md` |
| PowerShell loop | `scripts/run-tessera-full-loop.ps1` |
| Bash loop | `scripts/run-tessera-full-loop.sh` |
| Claim ceiling | two dataset-scoped T1 families supported; general transfer open |
| GitHub push | push after validation passes unless `--no-push` / `-NoPush` is used |

## What Tessera Must Not Forget

These are promoted engineering lessons. They change future behavior and are
enforced by tests, manifests, certificates, or repository gates.

| Learned truth | Permanent behavior |
|---|---|
| Tiny normal-only datasets cannot support an unconstrained neural forecaster. | Stable simple experts own the prediction floor; neural fields earn bounded residual authority. |
| A large raw error is not automatically useful anomaly evidence. | Every awareness channel receives normal-only, two-sided robust calibration and bounded influence. |
| Replay and false-memory metrics can lie through the wrong denominator. | Replay coverage is measured among normal rows; false-memory contamination is measured among anomaly rows. |
| Strong ranking does not guarantee useful warnings. | AUC, warning recall, replay coverage, false memory, and governance harm remain separate gates. |
| Synthetic success does not imply real transfer. | Every external dataset gets a pinned source, license, hashes, immutable splits, and a dataset-scoped certificate. |
| A successful real dataset does not imply cross-domain generalization. | Untouched confirmation datasets may reject a discovered hypothesis without weakening promotion thresholds. |
| Target telemetry and command/event context are different semantic types. | Contextual systems require typed or relational modeling; scalar fusion is not assumed sufficient. |
| Upstream preprocessing can invalidate an otherwise reproducible benchmark. | Inherited test-based scaling is recorded as leakage and structurally blocks clean T1 promotion. |
| Failed transfer is not discarded work. | Every failure becomes a wound, lesson, next hypothesis, and route update. |
| Expanded observability is not consciousness or autonomy. | No model output grants host-memory writes, tools, prompt mutation, live repair, or self-authorization. |
| Event governance cannot repair sensor blindness. | Quarantine may contain a detected episode, but sensor routing must first match point, subsequence, or contextual anomaly scale. |
| A router should not be forced to trust one weak sensor. | Point and subsequence evidence are calibrated independently; future routing may abstain when neither tile is trustworthy. |
| Abstention metadata alone does not change perception. | Abstention must alter score fusion under a declared coverage budget; independent memory normality remains a separate gate. |
| Routing cannot manufacture a missing sensing primitive. | Selective fusion is promoted only for confirmed sensor families; rejected morphology domains require new perception. |
| One-channel arrays still have two-dimensional contracts. | Every baseline restores `(rows, features)` output shape and is regression-tested against quadratic broadcasting. |
| One model does not need to own every cognitive function. | Forecasting, compression, anomaly sensing, and memory admission may use separately validated bounded experts. |
| Larger neural geometry is not automatically better geometry. | Supported codecs remain frozen until deeper or wider variants pass ranking, replay, memory, and prediction gates together. |
| Repair cannot win on one flattering number. | Shadow arms must pass prediction, replay, recall, and false-memory eligibility before utility ranking. |
| Explicit failures make weak agent benchmarks. | Trajectory utility must test precursors, safe-memory retention, false intervention, and latency against simple controls. |
| Precursors create a five-way utility tradeoff. | Recall, false intervention, safe-memory retention, unsafe-memory rejection, and latency remain separate agent gates. |
| Privacy-safe metadata is still a new domain. | Local operator trajectories require phase-conditioned calibration; warning on everything is a failed utility result. |
| A model cannot infer what the sensor never observed. | Trajectory identifiability is audited before calibration; label-conflicting feature collisions block promotion. |
| An adequate sensor can still be wasted by the wrong router. | Phase-semantic telemetry is handled by a separately calibrated bounded specialist before integration. |
| Shared phase names do not make workflows exchangeable. | Specialists require finite-sample normal support and a matching privacy-safe workflow profile; otherwise they abstain. |
| Several locally calibrated sensors can still over-warn together. | Calibrate the combined session decision when one host action follows multiple phase tests. |
| Low false-warning rates can hide weak sensitivity. | Preregister effect-size response tests and report the minimum detectable perturbation separately. |
| A mechanism-adjacent sensor can still be too coarse. | Require replicated tail-specific association; preserve calibration while testing higher-resolution privacy-safe execution aggregates. |
| Permission declarations are not runtime isolation. | Production-facing inference must be supervised, time-bounded, fail-closed, unloadable, and adversarially tested. |
| Learning does not belong on the interactive request path. | Fast inference remains synchronous; fitting and repair stay shadow-only until replay-gated checkpoint admission. |
| A shadow trainer must never activate its own output. | Checkpoints are immutable proposals admitted through integrity, replay, atomic activation, and rollback gates. |
| A controlled neural win is not natural agent utility. | Promote integration separately; natural chronological cohorts must beat persistence, summaries, and retrieval controls. |
| A checkpoint that beats persistence may still be unnecessary. | Stable expert ownership remains until neural utility beats every preregistered matched control. |
| Two outliers do not constitute an operating mode. | Conditional calibration requires recurring privacy-safe signatures in both discovery and later validation. |
| General resource pressure is not automatically tail attribution. | Context conditioning requires replicated association with robust tail events, not ordinary latency alone. |

Current evidence says: Tessera has two supported real-telemetry T1 families
(NAB and UCR), one rejected NASA transfer branch, and no general transfer claim.

## PowerShell All-One Loop Box

```powershell
cd "C:\Users\jacks\OneDrive\Desktop\Tessera"
.\scripts\run-tessera-full-loop.ps1
```

Dry run:

```powershell
.\scripts\run-tessera-full-loop.ps1 -NoPush
```

## Bash All-One Loop Box

```bash
cd "$HOME/OneDrive/Desktop/Tessera"
./scripts/run-tessera-full-loop.sh
```

Dry run:

```bash
./scripts/run-tessera-full-loop.sh --no-push
```

## What Opens at the Start of Every Loop

```text
Observer CLI opens first.
Worker CLI opens second.
```

The Observer is read-only. The Worker runs the Python-owned loop.

## Command Registry

Every operational command is recorded in:

```text
docs/loop/TESSERA_COMMAND_REGISTRY.md
```

Essential commands:

```powershell
python -m tessera.operator_geometry validate
python -m tessera.operator_geometry launch
python -m tessera.operator_geometry observe
python -m tessera.operator_geometry worker
python -m tessera.operator_geometry chart
python -m tessera.operator_geometry lessons
python -m tessera.operator_geometry commands
```

## Runtime Geometry

```text
rehydrate
-> RHP current truth
-> Nexus routes
-> repository geometry
-> lesson gates
-> command-registry
-> alignment-geometry
-> loopbook
-> lessons
-> launch-observer
-> launch-worker
-> check
-> run
-> validate
-> ledger
-> push
-> root
```

## RHP-Nexus Rehydration

Tessera includes a compact, dependency-free extraction of the strongest
Hermes RHP and Nexus contracts:

```powershell
$env:PYTHONPATH = ".\src"
python -m tessera.rhp rehydrate --root .
python -m tessera.rhp validate --root .
```

Canonical surfaces:

- `docs/context/rhp/latest-rhp.json` — current truth pointer
- `docs/context/nexus/surface_registry.json` — routes and mini-README profiles
- `docs/geometry/repository_geometry.json` — node, edge, and loop geometry
- `docs/lessons/lesson_chart.json` — evidence-backed lesson promotion
- `scripts/validation/validate_rhp_nexus.py` — unified promotion gate

The extraction deliberately excludes Hermes-specific CI mutation, autoheal,
provider/model authority, memory promotion, API writes, and historical
evidence accumulation.

## Evolutionary Roadmap

The evidence-gated path from the current diagnostic engine to a pluggable
neural subsystem for agent-based applications is defined in:

```text
docs/roadmap/TESSERA_EVOLUTIONARY_ROADMAP.md
```

The near-term sequence is experimental integrity, neural baseline recovery,
real telemetry transfer, replay-guided shadow repair, agent-trajectory memory,
adaptive sparse topology, and only then a host-neutral neural plugin contract.

Current executable phase prototype:

```powershell
python -m tessera benchmark --seeds 11,23,37 --steps 300 --epochs 2
python -m tessera transfer-nab --root . --epochs 10
python -m tessera plugin-demo --events 8
```

The evolved hybrid predictor combines a stable EWMA level expert with a bounded
sparse-neural innovation. Its normal-calibrated multiscale sensor passed the
five-seed synthetic Phase 1 aggregate gate: median AUC `0.80222`, mean replay
coverage `0.748`, mean missed warnings `0.04444`, and mean false-memory rate
`0.04444`. See
`docs/research/MULTISCALE_AWARENESS_EVOLUTION_2026-06-19.md`.

The first real telemetry trial is pinned to NAB's machine-temperature failure
stream. It issued dataset-scoped T1 support with AUC `0.94865`, normal replay
coverage `0.66751`, missed-warning rate `0.02469`, and false-memory rate
`0.00353`. This is one stream from one benchmark family, not Phase 2 completion
or general transfer.

NASA SMAP Telemanom channels were also evaluated diagnostically. The
cross-family transfer failed: an untouched E-2 confirmation produced AUC
`0.56896` with high false-memory contamination. In addition, the published
arrays inherit test-based scaling, which blocks clean T1 promotion. This branch
remains diagnostic while NAB and UCR hold dataset-scoped support.

The pinned UCR branch added a shape-aware subsequence discord sensor. On an
untouched confirmation series, causal event persistence raised AUC from
`0.67002` to `0.87849` and recall to `0.80769`. UCR T1 remains diagnostic:
normal replay coverage was `0.58323`, false-memory contamination `0.15385`, and
forecasting remained below baseline. This is confirmed sensing progress, not a
transfer claim.

EVO-007 tested whether event episodes and memory quarantine generalized to a
fresh UCR pair. Discovery series 176 reached AUC `0.97629`, full recall, replay
`0.74701`, and zero false memories. Untouched confirmation series 177 contained
a two-sample anomaly and rejected the window-24 shape hypothesis: AUC `0.43675`,
missed warnings `1.0`, and false memories `1.0`. The lesson is permanent:
episode governance can contain detected events, but cannot replace
scale-appropriate perception.

EVO-008 built the first normal-calibrated point/subsequence sensor router. The
point tile transferred across a fresh ECG pair: untouched confirmation AUC
`0.94731`, recall `1.0`, and false-memory rate `0.0`. The long-shape branch
confirmed only AUC `0.64806` with high contamination. Route-aware episode
duration improved point replay from `0.36262` to `0.46536`, but replay and
forecasting gates still block UCR T1. The next router must support abstention
and separate detection confidence from memory eligibility.

EVO-009 added explicit abstention and an independent joint-normality memory
gate. On untouched point and shape confirmations it reached AUC `0.92274` and
`0.96784`, with zero false memories on both. Normal replay coverage remained
below gate at `0.58078` and `0.56556`, and max fusion still trailed the best
specialist scores (`0.92903` and `0.98863`). The memory-normality branch is
confirmed; abstention-aware fusion, forecasting, and UCR T1 remain blocked.

EVO-010 made abstention operational through a normal-validation `20%`
specialist-coverage budget and consensus fusion elsewhere. Untouched ECG point
confirmation reached AUC `0.99997`, replay `0.62725`, recall `1.0`, and zero
false memories, clearing every detector and memory gate. InternalBleeding
confirmation rejected the current shape family with AUC `0.24390` and
false-memory rate `0.79518`. Forecasting remains the point branch blocker:
Tessera loss `0.42382` versus reservoir baseline `0.01401`.

EVO-011 separated forecasting from anomaly sensing. A normal-validation causal
expert bank selected ridge autoregression with lag `32` independently on a
distorted discovery stream and untouched clean confirmation. Confirmation
issued UCR dataset-scoped T1 support with AUC `0.96081`, replay `0.61215`,
recall `1.0`, zero false memories, and prediction loss `0.01888` versus the
best comparison baseline `0.02299`. Tessera now has two supported real-data
families—NAB and UCR—while general transfer and production readiness remain
unproven.

The bounded plugin runtime now uses the same modular forecasting contract.
Neural field loss remains the anomaly-awareness surface; a causal expert
selected from prior normal event history supplies operational prediction loss.
The chosen expert is exposed in inference packets and checkpoints. Host memory
writes, tools, prompt mutation, topology mutation, live codec replacement, and
external APIs remain denied.

EVO-014 re-evaluated the enhanced neural core on the pinned NAB protocol.
Depth `3`, hidden width `128` retained AUC `0.94448`, recall `0.99295`, and
zero final-test false memories, while EWMA `0.8` improved prediction loss to
`0.02488`. Replay coverage fell to `0.53473`, so the enhanced codec remains
diagnostic and the original supported NAB T1 certificate stays canonical.

EVO-015 repaired shadow-ablation promotion so wrong-target repair cannot win
without replay evidence. `targeted_shadow_repair` became the only eligible arm.
The first offline trajectory benchmark then matched recency at `1.0` decision
accuracy and failure recall, blocked all unsafe memories, retained `0.5` of
safe memories, and averaged about `159 ms` inference latency. Because explicit
error flags saturated the recency control, no superior agent-utility claim is
supported.

EVO-016 removed explicit failure and retry flags on a fresh 24-trajectory
cohort. Tessera reached `1.0` precursor recall and `0.91667` decision accuracy,
versus recency `0.0`/`0.5` and summary `0.33333`/`0.66667`, while rejecting all
unsafe memories. It also produced `0.16667` false interventions, retained only
`0.58333` of safe memories, and averaged about `98 ms` latency. This supports
synthetic offline precursor utility, not live agent utility.

EVO-017 privacy-audited the local Agent CLI ledger and excluded commands,
details, paths, prompts, and raw outputs. On 17 qualifying sessions Tessera
caught both observed failures but warned on all 15 clean sessions, yielding
accuracy `0.11765` and safe-memory recall `0`. Privacy-safe capture is
supported; local trajectory utility is rejected pending fresh data and
phase-conditioned calibration.

EVO-018 proved the frozen local cohort is not identifiable: 18 sessions reduced
to five unique allowed observations, and every degraded prefix exactly matched
a clean prefix. Failure recall at zero false intervention is therefore bounded
at `0`. Tessera now gates trajectory promotion on identifiability and emits
safe future telemetry—opaque session ID, event index, elapsed milliseconds, and
numeric exit code—without exposing commands or payloads.

EVO-019 used that safe telemetry on a controlled calibration cohort and a
separate fresh holdout cohort. The frozen phase-duration specialist reached
`1.0` failure recall, `0.25` false intervention, `0.75` safe-memory recall,
`0.0` unsafe-memory rate, and `0.875` decision accuracy across eight holdout
sessions, with approximately `0.006 ms` mean decision latency. The precursor
is visible, but four clean calibration sessions are not enough for stable
operating bounds; live agent utility remains unsupported.

EVO-020 expanded calibration to 24 new clean sessions and replaced the ad hoc
margin with a finite-sample rank gate requiring 19 observations at a declared
5% clean-warning budget. On a fresh eight-session controlled confirmation, the
specialist reached `1.0` recall, `0.0` false intervention, `1.0` safe-memory
recall, and `1.0` accuracy. Two natural full-loop sessions had a different
privacy-safe structural workflow profile, so coverage was `0` and both
decisions safely abstained. Controlled confirmation does not transfer to
natural workflows without profile-specific calibration.

EVO-021 calibrated the real validation workflow. Independent phase bounds
warned on `1/8` clean shadow sessions, exposing session-level multiple-testing
risk. A later split-conformal gate used 20 clean reference sessions and 20
independent score-calibration sessions to calibrate one maximum cross-phase
score. On eight untouched clean sessions it achieved `1.0` coverage and `0.0`
warnings. Two slow valid calibration runs made the gate highly conservative,
so natural failure sensitivity remains unmeasured and unsupported.

EVO-022 preregistered an offline delay ladder against the frozen natural
workflow specialist. Response was monotonic and zero-delay warnings remained
`0`, but full detection required `200 ms` of added REHYDRATE latency and
`250 ms` for MIRROR and GEOMETRY. No phase responded at `150 ms` or below.
This maps coarse detector sensitivity; injected delays are not natural
failures.

EVO-023 tested whether the slow clean tail justified separate operational
modes. One GEOMETRY-only tail event and one REHYDRATE-only tail event appeared
in validation, with no matching discovery recurrence. No candidate met the
required `3 + 3` chronological support, so mode separation was rejected and
calibration remained unchanged.

EVO-024 added allowlisted aggregate CPU, available-memory ratio, and process
count to 40 fresh clean validation sessions. These fields reproducibly tracked
ordinary MIRROR latency but did not explain the sparse REHYDRATE or GEOMETRY
tails. No phase/context pair passed the preregistered correlation and tail
support gates, so context-conditioned calibration was rejected.

EVO-025 measured subprocess spawn-call duration and aggregate disk byte/time
deltas across 40 fresh clean sessions. No phase/field pair passed the
chronological correlation and tail-support gates. MIRROR spawn association
weakened from `0.537` in discovery to `0.257` in validation, and aggregate disk
time was usually zero. Mechanism-conditioned calibration was rejected; the
next bounded sensor target is child CPU time and context-switch aggregates.

EVO-026 hardened the plugin boundary with a persistent supervised subprocess,
hard timeout, crash containment, circuit breaker, numeric input budgets, health
reporting, and unload behavior. All six local containment probes passed with
zero unauthorized host mutations. Persistent-worker reuse reduced warm p95
from approximately `3.65 s` to `1.13 s`, but that remains above the declared
`250 ms` production budget. Containment is promoted; production-candidate
status is not.

EVO-027 removed neural fitting from the synchronous supervised request path.
After explicit worker warmup, 20 consecutive calls achieved `3.11 ms` p95 and
`5.10 ms` maximum latency against the `250 ms` budget, while all containment
checks remained active. The interactive runtime latency gate now passes.
Production status remains blocked because asynchronous shadow training,
checkpoint admission and rollback, host adapters, sustained load, signing,
security review, and natural agent utility are still open.

EVO-028 added the asynchronous learning control plane: immutable hash-bound
checkpoint candidates, replay-gated admission, atomic activation, injected
failure preservation, and rollback. Five of five lifecycle probes passed.
The trainer still has no activation authority. The next target is a real
neural checkpoint evaluated on held-out agent-trajectory replay.

EVO-029 admitted a real serialized TESSERANet checkpoint with a
validation-selected causal prediction expert. It passed controlled held-out
replay and served 20 warm neural requests at `11.19 ms` p95 and `15.66 ms`
maximum latency. The integration path works; natural agent utility remains
unproven because the controlled trajectory strongly favored autoregression.

EVO-030 tested 120 immutable clean natural sessions chronologically. The
checkpoint improved over persistence but won only `52.63%` of replay rows,
below the `60%` admission gate, and was `24.15%` worse than
validation-selected EWMA on the untouched final 20 sessions. Admission was
rejected. The validated fast path remains intact, with stable expert prediction
ownership and neural awareness separated.

The plugin accepts allowlisted agent-event metadata, performs local sparse
neural inference, and emits memory, repair, and replay proposals. Host-memory
writes, tool invocation, prompt mutation, live codec replacement, topology
mutation, and external API calls remain denied.

## Failure Lessons Chart

Failures are recorded in:

```text
docs/loop/TESSERA_FAILURE_LESSONS.md
```

Core law:

```text
Failure must become a lesson.
Lesson must become a chart.
Chart must become a gate.
Gate must run before promotion.
```

## Alignment and Geometry Gap

The repaired geometry is recorded in:

```text
docs/alignment/TESSERA_ALIGNMENT_GEOMETRY_GAP.md
```

Core law:

```text
No command without registry.
No loop without Observer-first launch.
No feature without Loopbook/lessons/chart alignment.
No root-level engine patch notes.
No PowerShell-owned loop logic.
```

## Validation Commands

```powershell
python -m tessera.operator_geometry validate
python scripts/readme/audit_readme_nexus_discipline.py
python scripts/rcc/check_rcc_nexus.py
python scripts/validation/validate_architecture_contracts.py
python -m unittest discover -s tests
python -m tessera validate --run outputs/runs/latest
```

## Non-Claim Lock

Tessera does not prove truth, safety, production readiness, code correctness, AGI, consciousness, biological equivalence, physical manifold identity, general anomaly-detection superiority, or real telemetry transfer from synthetic runs.

```text
No manifest, no transfer claim.
No baseline, no capability claim.
No replay, no memory promotion.
No validated loop, no push.
Navigation is not validation.
Documentation is not correctness.
Synthetic success is not transfer.
Validation remains reality.
```

## Agent CLI Contract

Every operator-facing Tessera script or loop enters through the Agent CLI. The Agent CLI opens the Observer first, then opens the Worker.

```text
Observer CLI opens first.
Worker CLI opens second.
```

PowerShell All-One Loop Box:

```powershell
cd "C:\Users\jacks\OneDrive\Desktop\Tessera"
.\scripts\tessera-agent.ps1
```

Bash All-One Loop Box:

```bash
cd "$HOME/OneDrive/Desktop/Tessera"
./scripts/tessera-agent.sh
```

Direct Python:

```powershell
python -m tessera.agent_cli launch
```

Agent contract:

```text
docs/operator/TESSERA_AGENT_CLI_CONTRACT.md
```

Validation:

```powershell
python scripts/validation/validate_agent_cli_contract.py
```

<!-- TESSERA_AGENT_CLI_MIRROR_START -->
## Agent CLI Mirror — Transplantable Root Module

Tessera now includes a portable `agent_cli_mirror/` root folder. Its purpose is to turn operator-facing scripts into a hardened agent-style CLI interface: scripts as agent/API calls enter, the Observer opens before Worker, live state is emitted, failures become lessons, and the command registry remains portable.

```text
operator script
-> Agent CLI Mirror
-> Observer opens before Worker
-> Worker executes registered command capsule
-> live state / events / lessons / ledger
-> validation / push / root
```

### Intent

`agent_cli_mirror/` is designed to be copied into another repository. To transplant it:

```text
1. Copy agent_cli_mirror/
2. Copy scripts/agent-mirror.ps1 and scripts/agent-mirror.sh
3. Edit agent_cli_mirror/config/commands.json
4. Run python agent_cli_mirror/agent_mirror.py validate
5. Launch through the mirror, not raw scripts
```

### Canonical Agent Entrypoints

PowerShell:

```powershell
.\scripts\agent-mirror.ps1
```

Bash:

```bash
./scripts/agent-mirror.sh
```

Direct Python:

```powershell
python agent_cli_mirror/agent_mirror.py launch --command full
```

Dry run:

```powershell
.\scripts\agent-mirror.ps1 -NoPush -SkipRun
```

### Registry Law

```text
No operator-facing script bypasses the Agent CLI Mirror.
No script becomes public until it is represented in agent_cli_mirror/config/commands.json.
No Worker starts before Observer.
No failure disappears without a lesson entry.
No shell owns the loop; shells only launch the mirror.
```

### Portable Boundary

The Agent CLI Mirror improves operator visibility, portability, command compression, and failure learning. It does not prove safety, correctness, autonomy, production readiness, or real telemetry transfer.
<!-- TESSERA_AGENT_CLI_MIRROR_END -->

## Agent CLI Mirror Graceful Stop

The Agent CLI Mirror now treats operator interruption as a governed event instead of a raw traceback. `Ctrl+C` in the Observer closes the Observer cleanly. `Ctrl+C` in the Worker records an interrupted-command lesson and exits with a controlled stop state. Use `-SkipRun` or `-Command validate` for lightweight interface checks when heavy imports such as Torch or SciPy are not needed.
