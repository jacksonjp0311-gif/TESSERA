<div align="center">

# Tessera

### Sparse compressive memory engine with replay-certified memory and RCC Nexus discipline.

**Declare the graph. Compress the stream. Replay every memory. Wound every failure. Repair only in shadow. Validate before mutation. Claim only what transfers.**

![Tessera Engine](https://img.shields.io/badge/Tessera%20Engine-v0.1.2-blue)
![RCC-N](https://img.shields.io/badge/RCC--N-Full-brightgreen)
![README Discipline](https://img.shields.io/badge/README%20discipline-passing-brightgreen)
![Alignment](https://img.shields.io/badge/alignment-origin--guarded-brightgreen)
![Claim Ceiling](https://img.shields.io/badge/claim%20ceiling-diagnostic--baseline--limited-orange)
![Non-Claim](https://img.shields.io/badge/non--claim--locks-active-black)

</div>

---

## What Tessera Is

Tessera is a local-first Python reference engine for sparse compressive memory. It tests whether a sparse spectral field can compress telemetry into latent codes, reconstruct and predict the stream, gate candidate memories, replay those memories, record wounds, compare against simple baselines, and emit certificate-bound evidence packages.

Tessera is not built to answer â€œis the model intelligent?â€ It is built to answer a narrower engineering question:

```text
What is this compressed telemetry state allowed to become next?
```

The runtime path is intentionally visible:

```text
telemetry
-> dataset manifest / split discipline
-> sparse spectral field
-> encoder / latent code
-> reconstruction + prediction
-> rate-distortion score
-> warning / block / memory gates
-> replay buffer
-> wound ledger if failed
-> evidence package
-> transfer certificate
-> claim ceiling
```

Core operating law:

```text
Rehydrate before reasoning.
Orient before action.
Validate before mutation.
Gate before promotion.
Package every wound.
Show the evidence.
Return to root.
```

Tessera is built for one disciplined purpose:

```text
No manifest, no transfer claim.
No baseline, no capability claim.
No replay, no memory promotion.
No cleared gate, no durable continuation.
No human authorization, no push.
```

---

## Current Health Snapshot

| Surface | Current result |
|---|---:|
| Repository | `Tessera` |
| Package / CLI | `tessera` |
| Current engine | Tessera Engine v0.1.2 README / Nexus Discipline Patch |
| Previous seal | Tessera Engine v0.1.1 Alignment + RCC Nexus RootMirror Guard |
| Host theory line | TESSERA v1.7 Real Telemetry Transfer Architecture |
| RCC-N selected profile | Full |
| RCC route map | `rcc/nexus/route_map.json` |
| Repository context index | `docs/context/repository_context_index.json` |
| RCC Nexus index | `docs/context/rcc_nexus_index.json` |
| Origin manifest | `docs/alignment/origin_manifest.json` |
| Non-claim locks | `docs/alignment/non_claim_locks.md` |
| Theory import manifest | `docs/theory/import_manifest.json` |
| README discipline | `docs/readme/README_DISCIPLINE.md` |
| Public metrics dashboard | `docs/benchmarks/current_public_metrics.md` |
| README audit | `reports/readme/latest_readme_nexus_discipline_audit.md` |
| RCC-N checker | `reports/rcc_nexus/latest_rcc_nexus_check.json` |
| Architecture validator | `reports/validation/latest_architecture_contract_validation.json` |
| Smoke run artifacts | `outputs/runs/latest/` when generated locally |
| Claim ceiling | `diagnostic_baseline_limited_until_real_telemetry_transfer` |
| GitHub push | blocked until James explicitly authorizes it |

Current public finding: Tessera has a local runnable engine plus repository-navigation discipline. It can emit synthetic-run evidence packages and local diagnostics. It does not yet prove real telemetry transfer, production readiness, safety, truth, AGI, consciousness, or universal anomaly-detection superiority.

---

## Human Director Box

### What this repository is

Tessera is a governed software workbench for sparse compressive memory:

```text
repository origin
-> RCC Nexus orientation
-> telemetry run
-> graph field
-> compressed code
-> replay validation
-> wound / evidence / certificate
-> claim ceiling
```

The repository is designed so a human or AI agent can locate the right surface before changing it, identify the correct validation command, preserve non-claim locks, and avoid promoting synthetic results as real-world transfer.

### What changed in v0.1.2

This patch imports README discipline from three governance patterns:

1. **ASF-R style loop visibility** â€” make the full governed loop visible, include an operator run block, and state exactly what the loop does not authorize.
2. **CMS style current-state discipline** â€” maintain a health snapshot, public metrics, version lineage, README audit, and surface-alignment rule.
3. **RCC-N style Nexus discipline** â€” preserve README trisection, route maps, Echo Location records, mini READMEs, claim boundaries, and validation before mutation.

### What this repository is not

Tessera does **not** prove:

- AGI,
- consciousness,
- safety,
- truth,
- production readiness,
- code correctness,
- patch safety,
- empirical validation,
- biological equivalence,
- physical manifold identity,
- general anomaly-detection superiority,
- real telemetry transfer from synthetic runs.

---

## Run the Whole Tessera Local Loop

Use this box to run the local governed Tessera loop. This does not push to GitHub and does not grant live repair authority.

```text
This does not grant authority.
This does not prove transfer.
This does not authorize push.
This does not replace validation.
This only runs the governed local loop and emits inspectable evidence.
```

### PowerShell

```powershell
cd "C:\Users\jacks\OneDrive\Desktop\Tessera"
$env:PYTHONPATH = ".\src"

python -m pip install -e .
python scripts/rcc/check_rcc_nexus.py
python scripts/validation/validate_architecture_contracts.py
python scripts/readme/audit_readme_nexus_discipline.py
python -m unittest discover -s tests
python -m tessera run --out outputs --steps 160 --epochs 2 --topology q4 --field-dim 16 --code-dim 8
python -m tessera validate --run outputs/runs/latest
```

### All-One Alignment / RCC Patch

```powershell
cd "C:\Users\jacks\OneDrive\Desktop\Tessera"
powershell -ExecutionPolicy Bypass -File ".\scripts\tessera_alignment_rcc_nexus_all_one_v0_1_1.ps1" -Root "C:\Users\jacks\OneDrive\Desktop\Tessera"
```

### Expected result

```text
1. Root is anchored.
2. RCC/Nexus and alignment surfaces are present.
3. README/Nexus discipline audit passes.
4. Unit tests pass.
5. Tessera emits a local run under outputs/runs/.
6. Validation emits an evidence/certificate result.
7. Claim ceiling remains diagnostic unless real telemetry transfer protocol passes.
8. RootMirror returns to C:\Users\jacks\OneDrive\Desktop\Tessera.
```

---

## Current Public Metrics

See:

```text
docs/benchmarks/current_public_metrics.md
```

Current status is intentionally conservative:

| Metric | Status |
|---|---:|
| Local package import | available |
| Synthetic telemetry generator | available |
| Sparse graph operators | available |
| TESSERANet reference model | available |
| Rate-distortion scoring | available |
| Triadic gate artifacts | available |
| Wound ledger artifacts | available |
| Baseline comparison | available |
| Evidence package | available |
| Transfer certificate schema | available |
| Real telemetry transfer | not yet validated |
| Claim ceiling | diagnostic baseline-limited |

Boundary: these metrics improve repository orientation and local evidence inspection. They do not prove code correctness, empirical validation, production readiness, or real telemetry transfer.

---

# PART I â€” Human README

## Start here

1. Read this README.
2. Read `README_90_SECONDS.md`.
3. Run the local validation stack.
4. Inspect `outputs/runs/latest/` after a run.
5. Do not push until James explicitly says to push.

## Repository spine

```text
README.md
-> README_90_SECONDS.md
-> AGENTS.md
-> docs/context/repository_context_index.json
-> docs/context/rcc_nexus_index.json
-> rcc/nexus/route_map.json
-> docs/alignment/origin_manifest.json
-> validation commands
```

---

# PART II â€” RCC Nexus README

## RCC-N operating rule

```text
RCC tells the agent what the repository means.
RCC-N tells the agent where it is.
Validation tells the agent whether reality agreed.
```

## Route map

```text
rcc/nexus/route_map.json
```

## Task routing matrix

```text
rcc/nexus/task_routing_matrix.md
```

## Agent handoff

```text
rcc/nexus/agent_handoff_contract.md
```

## Echo location

```text
Shell: center
Meridians: agent, drift, documentation, safety, telemetry, memory
Sector: repository-root
Version / TTL: RCC-N-v1.7 / 180 days
Claim boundary: navigation is not validation
```

---

# PART III â€” AI Agent README

## Required read order

```text
README.md
README_90_SECONDS.md
AGENTS.md
docs/context/repository_context_index.json
docs/context/rcc_nexus_index.json
rcc/nexus/route_map.json
docs/alignment/origin_manifest.json
```

## Before editing

```text
1. Identify route.
2. Identify touched surfaces.
3. Identify validation command.
4. Identify claim ceiling.
5. Preserve non-claim locks.
6. Preserve source attribution.
7. Avoid claim inflation.
8. Return to root.
```

## After editing

```powershell
python scripts/rcc/check_rcc_nexus.py
python scripts/validation/validate_architecture_contracts.py
python scripts/readme/audit_readme_nexus_discipline.py
python -m unittest discover -s tests
```

## Push boundary

```text
No GitHub push until James explicitly authorizes push in the active session.
```

---

## Version Discipline

| Version | Layer | Boundary |
|---|---|---|
| v0.1.0 | reference engine genesis | local runnable skeleton only |
| v0.1.1 | alignment + RCC Nexus RootMirror patch | navigation / origin / validation only |
| v0.1.2 | README / Nexus discipline patch | public surface and agent orientation only |
| v0.2 target | real telemetry adapters | dataset-scoped evidence only |

Core law:

```text
No version without a document.
No surface alignment, no release.
No README audit, no public checkpoint promotion.
No evidence package, no runtime claim.
No real telemetry manifest, no transfer claim.
```

---

## Concluding Compression

Tessera now uses a Nexus-readable repository discipline:

```text
Human orientation
-> RCC Nexus routing
-> AI agent handoff
-> origin manifest
-> validation stack
-> local evidence
-> claim ceiling
```

The public lock is:

```text
Navigation is not validation.
Documentation is not correctness.
Synthetic success is not transfer.
Validation remains reality.
```

<!-- TESSERA_RUNTIME_LOOP_COMPILER_START -->
## Tessera v0.2.0 Runtime Loop Compiler

Tessera now compresses its governed runtime loop into operator-visible CLI surfaces:

```text
rehydrate -> orient -> compile -> run -> measure -> validate -> ledger -> disconnect
```

Run:

```powershell
python -m tessera loop ascii
python -m tessera loop compile --out reports/runtime_loop
python scripts/validation/validate_runtime_loop_compiler.py
```

Hermes-Agent-Evo interlock boundary:

```text
Borrow governance geometry.
Do not borrow runtime authority.
Carry lessons forward.
Disconnect foreign authority.
```

Claim boundary: loop compilation improves operator visibility and repeatability. It does not prove code correctness, safety, production readiness, or real telemetry transfer.
<!-- TESSERA_RUNTIME_LOOP_COMPILER_END -->

<!-- TESSERA_OPERATOR_SHELL_START -->
## Tessera v0.2.2 PowerShell Operator Shell

Tessera now has a local Hermes-style PowerShell operator shell. It compresses the runtime loop into grouped sections, status rows, checkers, and run commands so the operator does not have to watch raw implementation code scroll by.

```text
rehydrate -> shell -> compile -> check -> run -> validate -> ledger -> push -> root
```

<details>
<summary><strong>Open the operator shell</strong></summary>

```powershell
cd "C:\Users\jacks\OneDrive\Desktop\Tessera"
.\scripts\tessera-shell.ps1
```

Commands inside the shell:

```text
status
compile
check
run
validate
full
push
help
exit
```

</details>

<details>
<summary><strong>Run the full compressed loop without entering the shell</strong></summary>

```powershell
cd "C:\Users\jacks\OneDrive\Desktop\Tessera"
.\scripts\run-tessera-full-loop.ps1
```

Bash:

```bash
./scripts/run-tessera-full-loop.sh
```

</details>

<details>
<summary><strong>Checkers</strong></summary>

```powershell
python scripts/rcc/check_rcc_nexus.py
python scripts/validation/validate_architecture_contracts.py
python scripts/readme/audit_readme_nexus_discipline.py
python scripts/validation/validate_operator_shell.py
python scripts/validation/validate_runtime_loop_compiler.py
python -m unittest discover -s tests
python -m tessera validate --run outputs/runs/latest
```

</details>

<details>
<summary><strong>Boundary</strong></summary>

```text
The shell may observe.
The shell may compile.
The shell may run local validation.
The shell may push after validation.
The shell may not claim real telemetry transfer.
The shell may not become autonomous authority.
The shell may not import Hermes runtime authority or ASF safety claims.
```

</details>

<!-- TESSERA_OPERATOR_SHELL_END -->

<!-- TESSERA_LOOPBOOK_GATE_START -->
## TESSERA Loopbook Gate

The Loopbook is the canonical record of the Tessera runtime loop. It updates before the full loop runs and acts as a gate: if loop surfaces change and the Loopbook manifest is stale, validation fails.

```text
rehydrate -> loopbook -> launch -> observe -> worker -> check -> run -> validate -> ledger -> push -> root
```

<details>
<summary><strong>Run the whole Tessera loop</strong></summary>

```powershell
cd "C:\Users\jacks\OneDrive\Desktop\Tessera"
.\scripts\run-tessera-full-loop.ps1
```

Dry run without push:

```powershell
.\scripts\run-tessera-full-loop.ps1 -NoPush
```

</details>

<details>
<summary><strong>What opens every time</strong></summary>

```text
Observer PowerShell = read-only human interface
Worker PowerShell   = local code runner
```

The observer may watch, illuminate, and display loop state. The worker runs local commands, checkers, runtime, validation, ledger, commit, and push.

</details>

<details>
<summary><strong>Loopbook gate checkers</strong></summary>

```powershell
python scripts/loopbook/sync_loopbook.py
python scripts/validation/validate_loopbook_gate.py
python scripts/rcc/check_rcc_nexus.py
python scripts/validation/validate_architecture_contracts.py
python scripts/readme/audit_readme_nexus_discipline.py
python -m unittest discover -s tests
python -m tessera validate --run outputs/runs/latest
```

</details>

<details>
<summary><strong>Gate law</strong></summary>

```text
If feature surfaces change, sync the Loopbook.
If the Loopbook manifest is stale, validation fails.
If validation fails, no commit/push promotion.
```

</details>

Boundary: the Loopbook improves repeatability and operator visibility. It does not prove correctness, safety, production readiness, AGI, consciousness, or real telemetry transfer.
<!-- TESSERA_LOOPBOOK_GATE_END -->

<!-- TESSERA_README_DISCIPLINE_ANCHOR_START -->

# PART I — Human README
# PART II — RCC Nexus README
# PART III — AI Agent README

<!-- TESSERA_README_DISCIPLINE_ANCHOR_END -->
