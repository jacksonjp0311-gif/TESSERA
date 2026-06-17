# Tessera v0.2.2 PowerShell Operator Shell

## Purpose

Create a local Hermes-style PowerShell interface for Tessera. The shell gives the operator compressed grouped execution, status rows, explicit checkers, runtime commands, validation, commit/push, and RootMirror return.

## Commands

```text
status   - show root, git status, and shell status
compile  - compile ASCII/runbook/manifest surfaces
check    - run RCC, architecture, README, shell, loop, and unit checks
run      - run local Tessera smoke cycle
validate - validate outputs/runs/latest
full     - compile, check, run, validate, and push
push     - commit and push current validated work
help     - redraw command surface
exit     - return to root and leave shell
```

## Boundary

The shell may observe, compile, check, run, validate, ledger, and push after validation. It may not self-authorize dangerous transitions, claim real telemetry transfer, import Hermes runtime authority, import CMS write authority, or claim ASF-R safety/truth.