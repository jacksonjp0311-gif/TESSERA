# AGENTS.md - Tessera Agent Operating Contract

## Required Read Order

1. README.md
2. README_90_SECONDS.md
3. docs/loop/TESSERA_LOOPBOOK.md
4. docs/loop/loopbook_manifest.json
5. docs/context/repository_context_index.json
6. docs/context/rcc_nexus_index.json
7. rcc/nexus/route_map.json
8. docs/alignment/origin_manifest.json

## Canonical Loop

```text
rehydrate -> loopbook -> launch -> observe -> worker -> check -> run -> validate -> ledger -> push -> root
```

## Canonical Command

```powershell
.\scripts\run-tessera-full-loop.ps1
```

## Before Any Feature Promotion

```powershell
python scripts/loopbook/sync_loopbook.py
python scripts/validation/validate_loopbook_gate.py
```

## Push Rule

James has authorized push-by-default after local validation passes. Use `-NoPush` only for dry-run inspection.

## Non-Claim Lock

The Loopbook and observer console are operator surfaces. They do not prove transfer, safety, production readiness, correctness, AGI, consciousness, or autonomous authority.

## Failure Lessons Gate

Before promoting any feature that changes loop behavior, update and validate:

```powershell
python scripts/validation/validate_failure_lessons_chart_gate.py
```

Required surfaces:

```text
docs/loop/TESSERA_FAILURE_LESSONS.md
docs/loop/TESSERA_OPERATOR_LOOP_CHART.md
docs/loop/TESSERA_README_FEATURE_IMPORTS.md
```
