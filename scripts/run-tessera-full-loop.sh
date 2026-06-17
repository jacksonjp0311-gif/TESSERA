#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(pwd)}"
cd "$ROOT"
export PYTHONPATH="$ROOT/src"
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8
echo "::group::compile"
python -m tessera loop compile --out reports/runtime_loop
echo "::endgroup::"
echo "::group::check"
python scripts/rcc/check_rcc_nexus.py
python scripts/validation/validate_architecture_contracts.py
python scripts/readme/audit_readme_nexus_discipline.py
python scripts/validation/validate_operator_shell.py
python scripts/validation/validate_runtime_loop_compiler.py
python -m unittest discover -s tests
echo "::endgroup::"
echo "::group::runtime"
python -m tessera run --out outputs --steps 80 --epochs 1 --topology q4 --field-dim 16 --code-dim 8
python -m tessera validate --run outputs/runs/latest
echo "::endgroup::"
