#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/src"

python -m tessera loop ascii
python -m tessera loop compile --out reports/runtime_loop
python scripts/validation/validate_runtime_loop_compiler.py
python -m tessera run --out outputs --steps 80 --epochs 1 --topology q4 --field-dim 16 --code-dim 8
python -m tessera validate --run outputs/runs/latest
echo "RootMirror returned to: $ROOT"