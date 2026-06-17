$ErrorActionPreference = "Stop"
$env:PYTHONPATH = (Join-Path (Get-Location).Path "src")

python scripts/rcc/check_rcc_nexus.py
python scripts/validation/validate_architecture_contracts.py
python scripts/readme/audit_readme_nexus_discipline.py
python scripts/validation/validate_runtime_loop_compiler.py
python -m unittest discover -s tests
python -m tessera loop ascii
python -m tessera loop compile --out reports/runtime_loop
python -m tessera run --out outputs --steps 80 --epochs 1 --topology q4 --field-dim 16 --code-dim 8
python -m tessera validate --run outputs/runs/latest
