from __future__ import annotations

import argparse
import json
from pathlib import Path

from tessera import loop_runtime


def manifest() -> dict:
    """Return the runtime loop compiler manifest."""
    return {
        "schema": "TESSERA-runtime-loop-compiler-v0.2.0",
        "loop_steps": [
            "REHYDRATE",
            "RHP",
            "NEXUS",
            "GEOMETRY",
            "LESSONS",
            "MIRROR",
            "LOOPBOOK",
            "CHECK",
            "RUN",
            "VALIDATE",
            "LEDGER",
            "PUSH",
            "ROOT",
        ],
        "compiler_version": "0.2.0",
        "targets": ["ascii", "bash", "powershell"],
    }


def ascii_text() -> str:
    """Return the ASCII runtime loop compiler chart."""
    return (
        "+------------------------------------------------------------+\n"
        "|               TESSERA RUNTIME LOOP COMPILER               |\n"
        "+------------------------------------------------------------+\n"
        "| 01 REHYDRATE       Load pointers, evidence, geometry       |\n"
        "| 02 RHP             Establish current truth                 |\n"
        "| 03 NEXUS           Resolve routes and surfaces             |\n"
        "| 04 GEOMETRY        Validate node/edge interconnection       |\n"
        "| 05 LESSONS         Require evidence-backed gates           |\n"
        "| 06 MIRROR          Sync agent CLI mirror                   |\n"
        "| 07 LOOPBOOK        Sync canonical runbook                  |\n"
        "| 08 CHECK           Run RCC/arch/README/registry/tests      |\n"
        "| 09 RUN             Execute Tessera runtime                 |\n"
        "| 10 VALIDATE        Validate evidence and certificate       |\n"
        "| 11 LEDGER          Write reports and live state            |\n"
        "| 12 PUSH            Commit and push after gates pass        |\n"
        "| 13 DISCONNECT      Close observer and worker cleanly       |\n"
        "| 14 ROOT            Return to repository root               |\n"
        "+------------------------------------------------------------+\n"
    )


def bash_text() -> str:
    """Return the Bash runtime loop compiler script."""
    return (
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "\n"
        "cd \"$(dirname \"$0\")/..\"\n"
        "\n"
        "python -m tessera loop ascii\n"
        "python -m tessera loop manifest\n"
        "python scripts/validation/validate_runtime_loop_compiler.py\n"
        "python -m tessera loop compile --out reports/runtime_loop\n"
    )


def powershell_text() -> str:
    """Return the PowerShell runtime loop compiler script."""
    return (
        "$ErrorActionPreference = 'Stop'\n"
        "Set-Location (Split-Path -Parent $PSScriptRoot)\n"
        "\n"
        "python -m tessera loop ascii\n"
        "python -m tessera loop manifest\n"
        "python scripts/validation/validate_runtime_loop_compiler.py\n"
        "python -m tessera loop compile --out reports/runtime_loop\n"
    )


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="tessera loop")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("ascii").set_defaults(func=lambda args: print(ascii_text()))
    sub.add_parser("manifest").set_defaults(func=lambda args: print(json.dumps(manifest(), indent=2)))
    c = sub.add_parser("compile")
    c.add_argument("--out", default="reports/runtime_loop")
    c.set_defaults(func=lambda args: loop_runtime.compile_launchers(loop_runtime.root_path()))
    args = p.parse_args(argv)
    args.func(args)
