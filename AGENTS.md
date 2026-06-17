# AGENTS.md â€” Tessera Agent Operating Contract

## Required Read Order

1. `README.md`
2. `README_90_SECONDS.md`
3. `docs/context/repository_context_index.json`
4. `docs/context/rcc_nexus_index.json`
5. `rcc/nexus/route_map.json`
6. `docs/alignment/origin_manifest.json`
7. `docs/readme/README_DISCIPLINE.md`

## Before Editing

- Identify route.
- Identify touched surfaces.
- Identify validation command.
- Identify claim ceiling.
- Preserve source attribution.
- Preserve non-claim locks.
- Avoid claim inflation.
- Return to repository root.

## Validation Commands

```powershell
python scripts/rcc/check_rcc_nexus.py
python scripts/validation/validate_architecture_contracts.py
python scripts/readme/audit_readme_nexus_discipline.py
python -m unittest discover -s tests
python -m tessera validate --run outputs/runs/latest
```

## Claim Locks

- navigation_is_not_validation
- documentation_is_not_correctness
- context_reconstruction_is_not_code_quality
- synthetic_success_is_not_transfer
- dataset_win_is_not_universal_claim
- replay_is_not_safety
- repair_is_not_truth
- validation_remains_required
- human_authorization_required_for_push

## Agent Route Law

```text
RCC orients.
Tessera measures.
Evidence constrains.
Certificates bound claims.
Human authorization controls push.
```

## Push Rule

Do not push to GitHub unless James explicitly authorizes push in the active session.

## Runtime Loop Compiler

Before changing runtime, validation, README, RCC, or evidence surfaces, agents must be able to run:

```powershell
python -m tessera loop ascii
python -m tessera loop compile --out reports/runtime_loop
python scripts/validation/validate_runtime_loop_compiler.py
```

The compiler is an operator-visibility surface, not proof of correctness.
