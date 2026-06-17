from __future__ import annotations

import argparse
import json
from pathlib import Path
from textwrap import dedent

LOOP_STEPS = [
    ("01", "REHYDRATE", "Load origin manifest, route map, context indexes, and claim locks."),
    ("02", "ORIENT", "Resolve RCC Nexus route, local surface, claim ceiling, and validation path."),
    ("03", "COMPILE", "Compress the runtime loop into ASCII, Bash, PowerShell, and evidence runbooks."),
    ("04", "RUN", "Execute the Tessera smoke/runtime cycle under declared graph and thresholds."),
    ("05", "MEASURE", "Emit rate-distortion, gates, wounds, baseline summary, and certificate artifacts."),
    ("06", "VALIDATE", "Run RCC, README, architecture, unit, and latest-run evidence checks."),
    ("07", "LEDGER", "Record run identity, Git state, lessons, and non-claim boundaries."),
    ("08", "DISCONNECT", "Extract lessons learned without importing Hermes runtime authority."),
]

ASCII_BOX = r"""
╔════════════════════════════════════════════════════════════════════╗
║                    TESSERA RUNTIME LOOP COMPILER                  ║
╠════════════════════════════════════════════════════════════════════╣
║ 01 REHYDRATE  -> origin/context/route/non-claim locks             ║
║ 02 ORIENT     -> RCC Nexus geometry + route map                   ║
║ 03 COMPILE    -> ASCII + Bash + PowerShell runtime runbooks       ║
║ 04 RUN        -> sparse field / codec / gates / replay            ║
║ 05 MEASURE    -> RD metrics / wounds / baselines / certificate    ║
║ 06 VALIDATE   -> RCC + README + architecture + tests + evidence   ║
║ 07 LEDGER     -> reports / lessons / Git state                    ║
║ 08 DISCONNECT -> carry lessons, not foreign runtime authority     ║
╚════════════════════════════════════════════════════════════════════╝
"""

BASH_RUNBOOK = """#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="${PYTHONPATH:-$(pwd)/src}"

python scripts/rcc/check_rcc_nexus.py
python scripts/validation/validate_architecture_contracts.py
python scripts/readme/audit_readme_nexus_discipline.py
python scripts/validation/validate_runtime_loop_compiler.py
python -m unittest discover -s tests
python -m tessera loop ascii
python -m tessera loop compile --out reports/runtime_loop
python -m tessera run --out outputs --steps 80 --epochs 1 --topology q4 --field-dim 16 --code-dim 8
python -m tessera validate --run outputs/runs/latest
"""

POWERSHELL_RUNBOOK = r"""$ErrorActionPreference = "Stop"
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
"""

LESSONS = [
    "Hermes pattern extracted: actor/runtime is separate from governance geometry.",
    "Tessera pattern added: compile the loop before every run so the operator can see the runtime contract.",
    "Latest-run bug lesson: publish latest after artifacts exist, not before.",
    "Push lesson: validation can pass while push remains blocked if commit/push flags are absent.",
    "Interlock rule: borrow geometry, not authority.",
    "Disconnect rule: preserve lessons locally, do not create dependency on Hermes runtime folders.",
]


def ascii_text() -> str:
    rows = "\n".join(f"{n}. {name:<10} :: {desc}" for n, name, desc in LOOP_STEPS)
    return ASCII_BOX.strip() + "\n\n" + rows + "\n"


def bash_text() -> str:
    return BASH_RUNBOOK


def powershell_text() -> str:
    return POWERSHELL_RUNBOOK


def manifest() -> dict:
    return {
        "schema": "TESSERA-runtime-loop-compiler-v0.2.0",
        "loop_steps": [
            {"order": order, "name": name, "description": desc}
            for order, name, desc in LOOP_STEPS
        ],
        "outputs": {
            "ascii": "reports/runtime_loop/tessera_runtime_loop_ascii.txt",
            "bash": "reports/runtime_loop/tessera_runtime_loop.sh",
            "powershell": "reports/runtime_loop/tessera_runtime_loop.ps1",
            "manifest": "reports/runtime_loop/tessera_runtime_loop_manifest.json",
        },
        "hermes_interlock": {
            "source": "hermes-agent-evo",
            "borrowed_pattern": [
                "observe",
                "propose",
                "classify",
                "dry_run",
                "evidence",
                "authorize",
                "limited_apply",
                "validate",
                "ledger",
            ],
            "blocked_transfer": [
                "Hermes runtime authority",
                "CMS write authority",
                "API authority",
                "self-authorization",
                "automatic rollback",
                "provider/model/tool authority",
            ],
        },
        "claim_boundary": "Loop compilation improves operator visibility and repeatability; it does not prove code correctness, safety, production readiness, or real telemetry transfer.",
    }


def compile_outputs(out: str | Path) -> Path:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "tessera_runtime_loop_ascii.txt").write_text(ascii_text(), encoding="utf-8")
    (out / "tessera_runtime_loop.sh").write_text(bash_text(), encoding="utf-8")
    (out / "tessera_runtime_loop.ps1").write_text(powershell_text(), encoding="utf-8")
    (out / "tessera_runtime_loop_manifest.json").write_text(
        json.dumps(manifest(), indent=2), encoding="utf-8"
    )
    (out / "tessera_runtime_loop_lessons.md").write_text(
        "# Tessera v0.2.0 Runtime Loop Lessons\n\n"
        + "\n".join(f"- {x}" for x in LESSONS)
        + "\n\n## Disconnect Boundary\n\nHermes-Agent-Evo informs the governance geometry. Tessera does not import Hermes runtime authority, CMS write authority, API authority, or self-authorization.\n",
        encoding="utf-8",
    )
    return out


def cmd_ascii(_: argparse.Namespace) -> None:
    print(ascii_text())


def cmd_bash(_: argparse.Namespace) -> None:
    print(bash_text())


def cmd_powershell(_: argparse.Namespace) -> None:
    print(powershell_text())


def cmd_manifest(_: argparse.Namespace) -> None:
    print(json.dumps(manifest(), indent=2))


def cmd_compile(args: argparse.Namespace) -> None:
    out = compile_outputs(args.out)
    print(f"TESSERA runtime loop compiled: {out}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tessera loop",
        description="Compile TESSERA runtime loop sections into ASCII/Bash/PowerShell/evidence surfaces.",
    )
    sub = parser.add_subparsers(dest="loop_cmd", required=True)

    a = sub.add_parser("ascii", help="Print the ASCII runtime loop.")
    a.set_defaults(func=cmd_ascii)

    b = sub.add_parser("bash", help="Print a Bash runtime runbook.")
    b.set_defaults(func=cmd_bash)

    p = sub.add_parser("powershell", help="Print a PowerShell runtime runbook.")
    p.set_defaults(func=cmd_powershell)

    m = sub.add_parser("manifest", help="Print the runtime loop manifest JSON.")
    m.set_defaults(func=cmd_manifest)

    c = sub.add_parser("compile", help="Write all loop compiler artifacts.")
    c.add_argument("--out", default="reports/runtime_loop")
    c.set_defaults(func=cmd_compile)
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()