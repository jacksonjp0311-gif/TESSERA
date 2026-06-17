#!/usr/bin/env bash
set -euo pipefail
ROOT="${TESSERA_ROOT:-$(pwd)}"
exec ./scripts/agent-mirror.sh --root="$ROOT" --command=full "$@"