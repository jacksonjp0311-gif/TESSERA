# Tessera in 90 Seconds

Tessera is a sparse compressive memory engine with RCC Nexus discipline.

It runs this loop:

```text
telemetry
-> sparse spectral field
-> compressed code
-> reconstruction / prediction
-> rate-distortion score
-> warning / block / memory gates
-> replay buffer
-> wound ledger
-> evidence package
-> transfer certificate
-> claim ceiling
```

It navigates this repository through:

```text
README
-> README_90_SECONDS
-> AGENTS
-> repository_context_index
-> rcc_nexus_index
-> route_map
-> origin_manifest
-> validators
```

## Fast local check

```powershell
cd "C:\Users\jacks\OneDrive\Desktop\Tessera"
$env:PYTHONPATH = ".\src"
python scripts/rcc/check_rcc_nexus.py
python scripts/validation/validate_architecture_contracts.py
python scripts/readme/audit_readme_nexus_discipline.py
python -m unittest discover -s tests
python -m tessera run --out outputs --steps 160 --epochs 2 --topology q4 --field-dim 16 --code-dim 8
python -m tessera validate --run outputs/runs/latest
```

## What changed in v0.1.2

- Root README now has Human / RCC Nexus / AI Agent trisection.
- README discipline has a dedicated document and validator.
- Public metrics dashboard is visible.
- Nexus route map includes README discipline surfaces.
- Push remains blocked until James authorizes it.

## Claim boundary

Tessera is a local reference engine. It does not prove real telemetry transfer until the v1.7 transfer protocol runs on declared real datasets with manifests, leakage guards, baselines, held-out replay, and transfer certificates.
