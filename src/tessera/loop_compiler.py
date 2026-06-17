from __future__ import annotations

import argparse
import json
from pathlib import Path

VERSION = "TESSERA-runtime-loop-compiler-v0.2.6"
LOOP = [
    ("01", "REHYDRATE", "load repository truth, README, AGENTS, RCC, origin, claim locks"),
    ("02", "LOOPBOOK", "sync canonical runbook and manifest before every full loop"),
    ("03", "LAUNCH", "open dual PowerShell console surfaces"),
    ("04", "OBSERVE", "human observer watches status, events, wounds, certificate, git state"),
    ("05", "WORKER", "worker runs checkers, runtime, validation, ledger, push"),
    ("06", "CHECK", "run RCC, architecture, README, loopbook, and unit gates"),
    ("07", "RUN", "execute local Tessera diagnostic runtime without pip reinstall"),
    ("08", "VALIDATE", "validate latest evidence package and transfer certificate"),
    ("09", "LEDGER", "write reports, live state, hashes, lessons, and Loopbook state"),
    ("10", "PUSH", "commit and push after local gates pass"),
    ("11", "ROOT", "return to repository root"),
]

ASCII = "+------------------------------------------------------------------+\n| TESSERA v0.2.6 PASTE-SAFE LOOPBOOK GATE                          |\n+------------------------------------------------------------------+\n| REHYDRATE -> LOOPBOOK -> LAUNCH -> OBSERVE -> WORKER             |\n| CHECK -> RUN -> VALIDATE -> LEDGER -> PUSH -> ROOT               |\n+------------------------------------------------------------------+\n| Loopbook is the canonical record.                                |\n| Full loop opens the human observer every time.                   |\n| Worker runs code; observer is read-only.                         |\n| Loopbook sync is a required gate before promotion.               |\n+------------------------------------------------------------------+"

POWERSHELL = r'''<# TESSERA CANONICAL FULL LOOP v0.2.6 :: always opens observer/worker #>
param(
    [string]$Root = "$env:USERPROFILE\OneDrive\Desktop\Tessera",
    [switch]$NoPush,
    [switch]$SkipRun,
    [switch]$SkipTests
)
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path $Root).Path
Set-Location $Root
[System.IO.Directory]::SetCurrentDirectory($Root)
$env:PYTHONPATH = Join-Path $Root "src"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
python scripts/loopbook/sync_loopbook.py
python scripts/validation/validate_loopbook_gate.py
$ArgsList = @("-Root", $Root)
if ($NoPush) { $ArgsList += "-NoPush" }
if ($SkipRun) { $ArgsList += "-SkipRun" }
if ($SkipTests) { $ArgsList += "-SkipTests" }
& (Join-Path $Root "scripts\tessera-dual-console.ps1") @ArgsList
Set-Location $Root
[System.IO.Directory]::SetCurrentDirectory($Root)
Write-Host "[ROOT] $Root"
'''

BASH = r'''#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(pwd)}"
cd "$ROOT"
export PYTHONPATH="$ROOT/src"
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8
python scripts/loopbook/sync_loopbook.py
python scripts/validation/validate_loopbook_gate.py
powershell.exe -ExecutionPolicy Bypass -File "scripts/run-tessera-full-loop.ps1" -Root "$ROOT"
'''

def ascii_text() -> str:
    rows = "\n".join(f"{n} {name:<10} :: {desc}" for n, name, desc in LOOP)
    return ASCII + "\n\n" + rows + "\n"

def manifest() -> dict:
    return {
        "schema": VERSION,
        "loop": [{"order": n, "stage": name, "purpose": desc} for n, name, desc in LOOP],
        "canonical_loopbook": "docs/loop/TESSERA_LOOPBOOK.md",
        "canonical_launcher": "scripts/run-tessera-full-loop.ps1",
        "dual_console_launcher": "scripts/tessera-dual-console.ps1",
        "worker": "scripts/tessera-worker.ps1",
        "observer": "scripts/tessera-watch.ps1",
        "gate": "scripts/validation/validate_loopbook_gate.py",
        "claim_boundary": "Loopbook gate improves repeatability and operator visibility. It does not prove correctness, safety, production readiness, or real telemetry transfer.",
    }

def compile_outputs(out: str | Path = "reports/runtime_loop") -> Path:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "tessera_loop_ascii.txt").write_text(ascii_text(), encoding="utf-8")
    (out / "tessera_loop_manifest.json").write_text(json.dumps(manifest(), indent=2), encoding="utf-8")
    Path("scripts/run-tessera-full-loop.ps1").write_text(POWERSHELL, encoding="utf-8")
    Path("scripts/run-tessera-full-loop.sh").write_text(BASH, encoding="utf-8")
    return out

def cmd_ascii(_: argparse.Namespace) -> None:
    print(ascii_text())

def cmd_manifest(_: argparse.Namespace) -> None:
    print(json.dumps(manifest(), indent=2))

def cmd_compile(args: argparse.Namespace) -> None:
    out = compile_outputs(args.out)
    print(f"TESSERA loopbook surfaces compiled: {out}")

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tessera loop", description="Compile Tessera loopbook surfaces.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("ascii"); a.set_defaults(func=cmd_ascii)
    m = sub.add_parser("manifest"); m.set_defaults(func=cmd_manifest)
    c = sub.add_parser("compile"); c.add_argument("--out", default="reports/runtime_loop"); c.set_defaults(func=cmd_compile)
    return parser

def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    args.func(args)

if __name__ == "__main__":
    main()