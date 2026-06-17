# TESSERA Loopbook

## Purpose

The Loopbook is the canonical operator run record for Tessera. The loop is now Python-owned. PowerShell only launches terminals.

```text
rehydrate -> python-loop-kernel -> loopbook -> launch -> observe -> worker -> check -> run -> validate -> ledger -> push -> root
```

## Canonical Python Command

```powershell
cd "C:\Users\jacks\OneDrive\Desktop\Tessera"
$env:PYTHONPATH = ".\src"
python -m tessera.loop_runtime launch
```

## Canonical PowerShell Launcher

```powershell
cd "C:\Users\jacks\OneDrive\Desktop\Tessera"
.\scripts\run-tessera-full-loop.ps1
```

## What Opens Every Time

```text
Observer PowerShell = read-only human interface
Worker PowerShell   = Python loop worker
```

## Loop Steps

1. `rehydrate`
2. `python-loop-kernel`
3. `loopbook`
4. `launch`
5. `observe`
6. `worker`
7. `check`
8. `run`
9. `validate`
10. `ledger`
11. `push`
12. `root`

## Gate Rule

```text
If feature surfaces change, sync the Loopbook.
If failures occur, update Failure Lessons.
If the chart is stale, validation fails.
If validation fails, no commit/push promotion.
```

## Non-Claim Boundary

The Loopbook does not prove truth, safety, production readiness, code correctness, AGI, consciousness, or real telemetry transfer. It records and gates the operator loop.

## Current Manifest Snapshot

```json
{
  "schema": "TESSERA-loopbook-manifest-v0.2.8",
  "updated_at_utc": "2026-06-17T11:44:35.836142+00:00",
  "git_head": "b0e236a",
  "loop_steps": [
    "rehydrate",
    "python-loop-kernel",
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
  "python_loop_kernel": "src/tessera/loop_runtime.py",
  "canonical_command": "python -m tessera.loop_runtime launch",
  "powershell_launcher": "scripts/run-tessera-full-loop.ps1",
  "claim_boundary": "Loop kernel records operator surfaces only; it does not prove real telemetry transfer.",
  "feature_hashes": {
    "README.md": "6bc6124f09fb995410789fc4bb97ff74873d1d8466210ce5770b9e860cf6de3e",
    "README_90_SECONDS.md": "ae20c88824fc21c649a46f8c9a11589cdc047740cf7618f5b31deb713617a8e8",
    "AGENTS.md": "cff09709179d0b1d27af0cf5473a99ffc5573f3e76e11e21373dc3f83f716136",
    "docs/loop/TESSERA_LOOPBOOK.md": "9833ee50b8937cd98ed21e63387fecb798ed29a283ab8d3db96ca4e450d66d36",
    "docs/loop/loopbook_manifest.json": "4e4803e611286062f48d8c7f9412c1597837fd3abe5774c484965bca3b18a9d3",
    "docs/loop/TESSERA_FAILURE_LESSONS.md": "b801f73b984c3f0a5bff278464f57e96f6a14d431929f7223819af95763daf13",
    "docs/loop/TESSERA_OPERATOR_LOOP_CHART.md": "840650a4b68c3d4e9a6828f1afd95c6d4e9b8c90dbdc9461c2c57b82dba2baca",
    "scripts/run-tessera-full-loop.ps1": "9b5db004960d3ddcaffff4c4cddf9c33184189925930746d84087d622a73b4da",
    "scripts/run-tessera-full-loop.sh": "1635d9b01a8648ee7f5f9a1eeae145153a3daefd6c8a236db10f44c4a4e41839",
    "src/tessera/loop_runtime.py": "81a36d7991becf0410e6a85ff47af1a61d587fd48c974998ad6e379e96b65806",
    "src/tessera/loop_compiler.py": "bcb45e897518499265a4b63ddf4dca1d4070d10658135610eb3a7cffa79ddd16",
    "src/tessera/cli.py": "e38403de5f873a1f63c59cecaa69f5b00fe9ac19867c621c7bee4d4c289fc0ff"
  }
}
```
