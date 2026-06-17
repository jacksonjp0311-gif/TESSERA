#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(pwd)}"
cd "$ROOT"
export PYTHONPATH="$ROOT/src"
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8
python scripts/loopbook/sync_loopbook.py
python scripts/validation/validate_loopbook_gate.py
powershell.exe -ExecutionPolicy Bypass -File "scripts/run-tessera-full-loop.ps1" -Root "$ROOT"
