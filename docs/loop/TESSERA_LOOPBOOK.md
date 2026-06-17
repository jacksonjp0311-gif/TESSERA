# TESSERA Loopbook

## Purpose

The Loopbook is the canonical operator run record for Tessera. Every feature that changes the runtime loop, scripts, validation path, README run surface, or operator interface must update this file and `docs/loop/loopbook_manifest.json`.

```text
rehydrate -> loopbook -> launch -> observe -> worker -> check -> run -> validate -> ledger -> push -> root
```

## Canonical Command

```powershell
cd "C:\Users\jacks\OneDrive\Desktop\Tessera"
.\scripts\run-tessera-full-loop.ps1
```

Dry run without push:

```powershell
.\scripts\run-tessera-full-loop.ps1 -NoPush
```

## What Opens Every Time

```text
Observer PowerShell = read-only human interface
Worker PowerShell   = local code runner
```

## Loop Steps

1. `rehydrate`
2. `loopbook`
3. `launch`
4. `observe`
5. `worker`
6. `check`
7. `run`
8. `validate`
9. `ledger`
10. `push`
11. `root`

## Gate Rule

```text
If feature surfaces change, sync the Loopbook.
If the Loopbook manifest is stale, validation fails.
If validation fails, no commit/push promotion.
```

## Expected Result

1. Repository root is locked.
2. Loopbook sync runs.
3. Observer PowerShell opens.
4. Worker PowerShell opens.
5. Checkers run.
6. Tessera runtime runs.
7. Latest evidence validates.
8. Ledger/report files update.
9. Git commit/push runs unless `-NoPush` is used.
10. RootMirror returns to the Tessera root.

## Non-Claim Boundary

The Loopbook does not prove truth, safety, production readiness, code correctness, AGI, consciousness, or real telemetry transfer. It records and gates the operator loop.

## Current Manifest Snapshot

```json
{
  "schema": "TESSERA-loopbook-manifest-v0.2.6",
  "updated_at_utc": "2026-06-17T10:48:29.262804+00:00",
  "git_head": "4455952",
  "loop_steps": [
    "rehydrate",
    "loopbook",
    "launch",
    "observe",
    "worker",
    "check",
    "run",
    "validate",
    "ledger",
    "push",
    "root"
  ],
  "canonical_loopbook": "docs/loop/TESSERA_LOOPBOOK.md",
  "canonical_command": ".\\scripts\\run-tessera-full-loop.ps1",
  "observer": "scripts/tessera-watch.ps1",
  "worker": "scripts/tessera-worker.ps1",
  "launcher": "scripts/tessera-dual-console.ps1",
  "gate": "scripts/validation/validate_loopbook_gate.py",
  "feature_hashes": {
    "README.md": "50089cb59a6a9029f8e5ab6fcc260544dc4559deea4f2b85129665808bf0b860",
    "README_90_SECONDS.md": "bbc105d0f9f70554b32467db0f14ae736d41cbd5034ff4d24a0610f56a4a6c2d",
    "AGENTS.md": "5451a5ee4cc6559071ce987500cffd95a24c3ed15541af3bf1f27fabc2f4054b",
    "docs/loop/TESSERA_LOOPBOOK.md": null,
    "scripts/run-tessera-full-loop.ps1": "ff4f0f2e619b64f7d6c8d40f22c12e26334f8331a02d477e70f1f8286924a392",
    "scripts/tessera-dual-console.ps1": "dcd7e6e37bd6096f3c729941ff4951000efc404b7eccc239aff24777fac9669f",
    "scripts/tessera-worker.ps1": "0de9313c0da2d7acd3b823bc985588bceebbc78040359552aed428c201382000",
    "scripts/tessera-watch.ps1": "4887c4b174066c658acb549787d1c3bfdbf7a30c9604f6b8a805ab61ed6f35ab",
    "scripts/validation/validate_loopbook_gate.py": "9c0124a8269929b9eed9d4d238cea5499f50fab7ec7ff74bcdc7941a8d9bc8a7",
    "src/tessera/loop_compiler.py": "10be9ee96c8c9729352d26ccd19506fad18ccd38c9408a239dc61e13b7df8aa3",
    "src/tessera/cli.py": "e38403de5f873a1f63c59cecaa69f5b00fe9ac19867c621c7bee4d4c289fc0ff"
  },
  "claim_boundary": "Loopbook sync records operator surfaces only; it does not prove real telemetry transfer."
}
```

## Failure Lessons and Loop Chart Gate

Tessera maintains these companion Loopbook surfaces:

```text
docs/loop/TESSERA_FAILURE_LESSONS.md
docs/loop/TESSERA_OPERATOR_LOOP_CHART.md
docs/loop/TESSERA_README_FEATURE_IMPORTS.md
```

Promotion gate:

```powershell
python scripts/validation/validate_failure_lessons_chart_gate.py
```

Core law:

```text
Failure must become a lesson.
Lesson must become a chart.
Chart must become a gate.
Gate must run before promotion.
```
