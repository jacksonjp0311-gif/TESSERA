# TESSERA Failure Lessons Registry

## Purpose

This registry converts the build failures from the TESSERA v0.1.4 -> v0.2.6 loop evolution into permanent engineering lessons and validation gates.

```text
failure -> diagnosis -> lesson -> gate -> artifact -> loop promotion
```

## Failure-to-Gate Chart

| ID | Failure / Wound | Diagnosis | Permanent Lesson | Gate / Artifact |
|---:|---|---|---|---|
| F01 | `outputs/runs/latest` validation pointed at incomplete artifacts | latest pointer was published before run artifacts existed | publish latest only after certificates/evidence/metrics are written | `publish_latest_run(run_dir)` + `tessera validate --run outputs/runs/latest` |
| F02 | `PermissionError` removing `outputs/runs/latest` on Windows | Windows treats directory/symlink/file removal differently | remove latest pointer with explicit file/symlink/dir handling | `src/tessera/utils/paths.py` |
| F03 | Git remote/origin logic polluted by command output | command stdout and exit code were mixed | use explicit remote getter and root-bound Git | `git -C <Root>` only |
| F04 | Bundle folder was missing | operator had to know where extracted script lived | scripts must be runnable from anywhere or paste-safe | paste-safe installer / single-file scripts |
| F05 | top-level `param(...)` failed when pasted | pasted PowerShell does not behave like file execution | paste-safe scripts avoid top-level param blocks | v0.2.6 style operator settings |
| F06 | `$Root` collapsed to empty string | root was not validated before path use | lock root before any write, command, or Git call | `Resolve-RepoPath` + root guard |
| F07 | Git scanned `C:\Users\jacks` | script ran Git outside repo root | every Git command must use `git -C <Root>` | root-bound Git invariant |
| F08 | Unicode box drawing crashed Windows console | CP1252 console could not encode glyphs | use ASCII-safe charts by default | ASCII loop chart |
| F09 | JSON route map failed on UTF-8 BOM | validator expected strict UTF-8 | normalize JSON/Markdown to UTF-8 no BOM before validation | `Normalize-NoBom` |
| F10 | README discipline failed after feature edits | README route markers drifted | README structure is a validation surface | README discipline anchor + audit |
| F11 | too much raw code scroll | operator could not see loop state clearly | split worker from observer; compress output into phase rows | dual-console worker/observer |
| F12 | pip reinstall repeated unnecessarily | local source tree already drives execution | no pip by default; install is explicit | local `PYTHONPATH` mode |
| F13 | loop knowledge lived in scripts only | users could run commands but not understand the loop | make Loopbook canonical and validate it | `docs/loop/TESSERA_LOOPBOOK.md` |
| F14 | feature changes could bypass loop docs | loop docs could go stale after new feature surfaces | Loopbook and lessons chart must update as gates | `validate_failure_lessons_chart_gate.py` |

## Core Lesson

```text
The system learns only when failure becomes a named artifact, a validation gate, and a visible operator surface.
```

## Non-Claim Boundary

These lessons improve local engineering hygiene and operator visibility. They do not prove real telemetry transfer, production readiness, safety, truth, AGI, consciousness, or universal anomaly-detection superiority.