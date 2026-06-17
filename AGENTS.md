# AGENTS.md - Tessera Agent Operating Contract

## Required Read Order

1. README.md
2. README_90_SECONDS.md
3. docs/context/repository_context_index.json
4. docs/context/rcc_nexus_index.json
5. rcc/nexus/route_map.json
6. docs/alignment/origin_manifest.json
7. reports/runtime_loop/tessera_loop_manifest.json
8. docs/operator_shell/TESSERA_OPERATOR_SHELL_V0_2_2.md

## Core Loop

```text
rehydrate -> shell -> compile -> check -> run -> validate -> ledger -> push -> root
```

## Operator Shell

```powershell
.\scripts\tessera-shell.ps1
```

Commands: status, compile, check, run, validate, full, push, help, exit.

## Validation Commands

```powershell
$env:PYTHONPATH = ".\src"
python scripts/rcc/check_rcc_nexus.py
python scripts/validation/validate_architecture_contracts.py
python scripts/readme/audit_readme_nexus_discipline.py
python scripts/validation/validate_operator_shell.py
python scripts/validation/validate_runtime_loop_compiler.py
python -m unittest discover -s tests
python -m tessera validate --run outputs/runs/latest
```

## Push Rule

James has authorized push-by-default after local validation passes. Use -NoPush only for dry-run inspection.

## Non-Claim Lock

The shell is an operator surface. It does not prove transfer, safety, production readiness, correctness, AGI, consciousness, or autonomous authority.