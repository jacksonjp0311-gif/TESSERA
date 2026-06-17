#!/usr/bin/env bash
set -euo pipefail
ROOT="${TESSERA_ROOT:-$(pwd)}"
COMMAND="full"
NO_PUSH=""
SKIP_RUN=""
SKIP_TESTS=""
for arg in "$@"; do
  case "$arg" in
    --root=*) ROOT="${arg#--root=}" ;;
    --command=*) COMMAND="${arg#--command=}" ;;
    --no-push) NO_PUSH="--no-push" ;;
    --skip-run) SKIP_RUN="--skip-run" ;;
    --skip-tests) SKIP_TESTS="--skip-tests" ;;
    *) ROOT="$arg" ;;
  esac
done
cd "$ROOT"
export PYTHONPATH="$ROOT/src"
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8
python agent_cli_mirror/agent_mirror.py launch --root "$ROOT" --command "$COMMAND" $NO_PUSH $SKIP_RUN $SKIP_TESTS