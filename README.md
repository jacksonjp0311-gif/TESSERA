<div align="center">

# Tessera

### Sparse compressive memory engine with replay-certified memory and RCC Nexus discipline.

**Declare the graph. Compress the stream. Replay every memory. Wound every failure. Repair only in shadow. Validate before mutation. Claim only what transfers.**

![Tessera Engine](https://img.shields.io/badge/Tessera%20Engine-v0.3.2-blue)
![RCC-N](https://img.shields.io/badge/RCC--N-Full-brightgreen)
![README Discipline](https://img.shields.io/badge/README%20discipline-passing-brightgreen)
![Alignment](https://img.shields.io/badge/alignment-geometry--guarded-brightgreen)
![Claim Ceiling](https://img.shields.io/badge/claim%20ceiling-diagnostic--baseline--limited-orange)
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
| Package / CLI | `tessera` |
| Current engine | Tessera Engine v0.3.2 Operator Geometry Finalization |
| Command registry | `docs/loop/TESSERA_COMMAND_REGISTRY.md` |
| Loopbook | `docs/loop/TESSERA_LOOPBOOK.md` |
| Failure lessons chart | `docs/loop/TESSERA_FAILURE_LESSONS.md` |
| Operator loop chart | `docs/loop/TESSERA_OPERATOR_LOOP_CHART.md` |
| Alignment geometry gap | `docs/alignment/TESSERA_ALIGNMENT_GEOMETRY_GAP.md` |
| PowerShell loop | `scripts/run-tessera-full-loop.ps1` |
| Bash loop | `scripts/run-tessera-full-loop.sh` |
| Claim ceiling | diagnostic baseline-limited |
| GitHub push | push after validation passes unless `--no-push` / `-NoPush` is used |

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
