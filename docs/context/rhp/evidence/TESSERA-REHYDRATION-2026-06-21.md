# Tessera Rehydration Report — 2026-06-21
## Source: https://github.com/jacksonjp0311-gif/TESSERA

---

## 1. Current State Summary

| Field | Value |
|---|---|
| **Latest Operation** | EVO-038 |
| **State** | EFFECTIVE_RANK_REPAIRED_HOST_OBSERVABILITY_GATED |
| **Version** | tessera v0.3.4 |
| **Tests** | **124 passing** |
| **Geometry** | 36+ nodes, 66+ edges |
| **Lessons** | 84 promoted (F001–F084) |
| **Real T1 Families** | 2 (NAB, UCR) |
| **Claim Ceiling** | two_dataset_families_T1_supported_general_transfer_open |
| **Integration Closed** | true |
| **Authority OK** | true |

---

## 2. What Tessera Is (EVO-038)

Tessera is a **local-first neural trust layer for agent systems**. It watches an agent's privacy-safe operational trajectory, compresses it into sparse neural state, and answers a deliberately narrow question: **should the host trust this session—or abstain?**

It runs as a **supervised local sidecar**. Stable experts retain forecast ownership; the sparse neural field measures latent drift and earns only selective trust-routing authority. An abstention cannot write memory, call tools, mutate prompts, replace models, or overrule the host.

### Key Architectural Components (EVO-038)

| Component | File | Purpose |
|---|---|---|
| **TESSERANet** | `src/tessera/model/network.py` | GRU-gated sparse spectral compressive memory (depth/configurable) |
| **Training** | `src/tessera/model/train.py` | AdamW + weight decay + cosine annealing + depth/hidden_dim |
| **Prediction Experts** | `src/tessera/model/prediction_experts.py` | Causal expert bank (persistence, EWMA, ridge AR) with normal validation |
| **TesseraPlugin** | `src/tessera/plugin/runtime.py` | Stateful plugin with checkpoint loading, uncertainty routing, multi-scale anomaly |
| **PluginSupervisor** | `src/tessera/plugin/supervisor.py` | Fail-closed subprocess boundary with circuit breaker, hard timeout, unload |
| **Neural Checkpoints** | `src/tessera/plugin/neural_checkpoints.py` | Serialize/deserialize TESSERANet + expert for replay admission |
| **Host Adapters** | `src/tessera/plugin/host_adapters.py` | AgentEvent + JSON session adapters with effective-rank feature selection |
| **Trajectory Adapters** | `src/tessera/plugin/trajectory.py` | 10 typed event adapters, unified 28-dim feature space |
| **Incident Governor** | `src/tessera/plugin/incident_governor.py` | Abstain latch, memory suppression, clean terminal recovery |
| **Privacy Capture** | `src/tessera/plugin/privacy_capture.py` | Privacy-safe local ledger (no commands/prompts/payloads) |
| **Shadow Training** | `src/tessera/plugin/shadow_training.py` | Async checkpoint training outside request path |
| **RHP Core** | `src/tessera/rhp/core.py` | Validation kernel for repository, lineage, geometry, authority |
| **Graph Topologies** | `src/tessera/graph/topologies.py` | Ring, dense, random_sparse, q4 spectral operators |
| **Adaptive Topology** | `src/tessera/graph/adaptive.py` | Shadow topology proposals with stability guarantees |
| **Multi-scale Anomaly** | `src/tessera/metrics/anomaly.py` | MAD-based multi-channel anomaly scoring |
| **Rate-Distortion** | `src/tessera/metrics/rate_distortion.py` | J_RD governance metric |
| **Triadic Gates** | `src/tessera/memory/gates.py` | Warn/block/memory with independent normality |
| **Repair Ablation** | `src/tessera/experiments/repair_ablation.py` | 5-arm shadow repair with eligibility + utility ranking |
| **Neural Uncertainty Router** | `src/tessera/experiments/neural_uncertainty_router.py` | Latent drift routing for abstention |
| **Bounded Neural Residual** | `src/tessera/experiments/bounded_neural_residual.py` | Clipped neural gain — found 0.0 is optimal |
| **Trajectory Benchmark** | `src/tessera/experiments/trajectory_benchmark.py` | Offline trajectory utility benchmark |
| **Host Integrations** | `src/tessera/plugin/host_integrations.py` | Agent CLI Mirror + Hermes adapter |

---

## 3. Verified Metrics (from GitHub README + evidence)

### Synthetic Benchmarks
| Metric | Value |
|---|---|
| Median AUC | 0.80222 |
| Mean replay coverage | 0.748 |
| Mean missed-warning rate | 0.04444 |
| Mean false-memory rate | 0.04444 |

### NAB Real Telemetry
| Metric | Value |
|---|---|
| **AUC** | **0.94865** |
| Normal replay coverage | 0.66751 |
| False-memory rate | 0.0353 |
| Missed-warning rate | 0.02469 |

### UCR Real Telemetry
| Metric | Value |
|---|---|
| **Confirmation AUC** | **0.96081** (CIMIS44AirTemperature3) |
| Recall | 1.0 |
| False-memory rate | 0.0 |
| Replay coverage | 0.61215 |
| Prediction loss | 0.01888 vs baseline 0.02299 |

### EVO-034 Production Candidate
| Metric | Value |
|---|---|
| Semantic route parity | 20/20 untouched final sessions |
| Trusted/abstain | 18/2 |
| Warm p95 latency | 95.19 ms |
| Soak p99 latency | 126.79 ms |
| Soak failures | 0/100 |

### EVO-038 Effective Rank
| Metric | Value |
|---|---|
| Ambient dimension | 84 |
| Legacy declared | 5 |
| **Effective rank** | **2** |
| Phantom dimensions removed | 3 |
| Final coverage | 0.90 |
| Risk reduction vs full | 6.53% |
| Risk reduction vs simple | 10.37% |

---

## 4. Evolutionary History (EVO-001 through EVO-038)

### Phase 1: Foundation (EVO-001–EVO-005)
Synthetic telemetry, encoder/decoder/predictor, anomaly detection, memory gates, first evidence packages.

### Phase 2: Real Telemetry (EVO-006–EVO-011)
NAB T1 (AUC 0.94865), UCR T1 (AUC 0.96081), NASA SMAP rejected. Plugin prediction expert integrated. Ridge AR lag 32 selected by normal validation.

### Phase 3: Neural Enhancement (EVO-012–EVO-014)
GRU gating, deeper encoder/decoder, multi-scale predictions, AdamW. Enhanced codec evaluated on NAB (AUC 0.94448 — diagnostic, not promoted).

### Phase 4: Shadow Repair (EVO-015)
5-arm ablation: no repair, random, wrong-target, generic retrain, targeted shadow. Targeted shadow wins as only eligible arm.

### Phase 5: Agent Trajectory (EVO-016–EVO-025)
Offline trajectory benchmarks, privacy-safe capture, identifiability audit, finite-sample calibration, phase-duration specialist, context-conditioned calibration rejected, mechanism-conditioned rejected.

### Phase 6: Production Hardening (EVO-026–EVO-034)
Plugin supervisor with subprocess isolation, circuit breaker, hard timeout, crash containment. Neural fitting removed from request path. Async learning control plane. Checkpoint admission with replay gate. Latency gate passes (95.19ms p95). Semantic route parity (20/20).

### Phase 7: Effective Rank (EVO-035–EVO-038)
Release verification (9/9). Two-host integration gate. Effective rank audit (84→2). Phantom constant dimensions removed. Host observability coverage (Agent CLI 1.0, Hermes 1.0). Privacy payload leaks: 0.

---

## 5. Honest Assessment

### What's Genuinely Strong

1. **Governance is real** — 84 promoted lessons, RHP-Nexus-Geometry-Lessons-Evidence chain validates correctly. Non-claim lock is active and honest.

2. **NAB T1 is solid** — AUC 0.94865, false-memory rate 0.0353, missed-warning 0.02469. This is a real result on real machine-temperature telemetry.

3. **UCR T1 is confirmed** — AUC 0.96081, perfect recall, zero false memories. Second independent family.

4. **Neural uncertainty routing works** — EVO-032: latent drift routes abstention without changing forecasts. 90% coverage, 6.53% risk reduction vs full, 10.37% vs simple router. This is the first supported natural-session neural authority.

5. **Production candidate** — EVO-034: 20/20 semantic parity, 95.19ms p95, 0/100 soak failures. The supervised runtime is structurally sound.

6. **Effective rank honesty** — EVO-038 found that 3 of 5 declared coordinates were float32 noise. Recalibrated to 2-dim (mean duration, duration dispersion). This is scientific integrity.

7. **Privacy-safe** — Commands, prompts, paths, payloads excluded from local ledger. Identifiability audited. Non-identifiable frozen cohort.

8. **Test discipline** — 124 tests, 100% pass rate, 38 evolutions without regression.

### What's Still Limited

1. **Only 2 dataset families** — NAB and UCR. Phase 2 requires 3. NASA SMAP was rejected.

2. **No live agent utility** — All trajectory results are offline/synthetic. The README explicitly states: "synthetic precursor utility supported; live utility open."

3. **External launch gates open** — 4 more failure/recovery incidents, 2 independent host integrations, security review, cross-platform certification.

4. **Neural prediction is below baseline** — UCR EVO-010: neural loss 0.42382 vs reservoir 0.01401. Stable experts own the prediction floor.

5. **Replay coverage is low** — 0.53–0.67 across all datasets. The 60% gate blocks promotion.

6. **No independently operated hosts** — EVO-037: 0 independently operated production hosts.

### What Was Rejected (Important)
- NASA SMAP cross-family transfer (AUC 0.56896, high contamination)
- Universal shape window (UCR EVO-007 confirmation AUC 0.43675)
- Context-conditioned calibration (no correlation + tail support)
- Mechanism-conditioned calibration (spawn association weakened)
- Neural forecast authority (reservoir beats neural 30x)
- Mode separation for slow clean tails (no recurrence)

---

## 8. Bottom Line

**Tessera at EVO-038 is a well-governed, honestly-reported research engine that has:**
- Achieved T1 support on two independent real-telemetry families (NAB, UCR)
- Built a complete production-candidate runtime with subprocess isolation, circuit breakers, and checkpoint admission
- Discovered and validated neural uncertainty routing (not prediction) as the first natural-session neural authority
- Maintained scientific integrity through effective-rank audits and explicit non-claims
- 124 tests, 100% pass rate, 38 evolutions

**It is not:**
- Production-ready (external launch gates open)
- A general transfer system (2 of 3 families)
- A neural predictor (stable experts own the forecast floor)
- A live agent utility (offline-only validation)

**The path forward is clear:**
1. Third dataset family for Phase 2 completion
2. Independent host trials with effective-rank monitoring
3. Natural failure sensitivity measurement
4. Security review and cross-platform certification
