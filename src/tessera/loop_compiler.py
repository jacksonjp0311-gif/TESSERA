from __future__ import annotations

import argparse
import json
from pathlib import Path
from textwrap import dedent

VERSION = "TESSERA-runtime-loop-compiler-v0.2.2"
LOOP = [
    ("01", "REHYDRATE", "load README, AGENTS, route map, origin manifest, metrics, claim locks"),
    ("02", "SHELL", "enter compressed PowerShell operator surface"),
    ("03", "COMPILE", "render ASCII, Bash, PowerShell, manifest, and README dropdowns"),
    ("04", "CHECK", "run RCC, architecture, README, operator shell, loop, and unit checkers"),
    ("05", "RUN", "execute local Tessera runtime without pip reinstall"),
    ("06", "VALIDATE", "validate latest evidence, certificate, wounds, metrics, and claim ceiling"),
    ("07", "LEDGER", "write reports/runtime_loop and lessons learned"),
    ("08", "PUSH", "commit and push after local evidence passes"),
    ("09", "ROOT", "return to repository root"),
]

ASCII = """+------------------------------------------------------------------+
| TESSERA v0.2.2 POWERSHELL OPERATOR SHELL                         |
+------------------------------------------------------------------+
| 01 REHYDRATE  README / AGENTS / RCC / origin / claim locks        |
| 02 SHELL      compressed local command surface                    |
| 03 COMPILE    ASCII / Bash / PowerShell / manifest / README       |
| 04 CHECK      RCC / architecture / README / shell / loop / tests  |
| 05 RUN        local runtime, no pip reinstall by default          |
| 06 VALIDATE   latest evidence / certificate / wounds / metrics    |
| 07 LEDGER     report / lesson / hash / git state                  |
| 08 PUSH       commit + push after evidence passes                 |
| 09 ROOT       return to root                                      |
+------------------------------------------------------------------+"""

POWERSHELL = r'''$ErrorActionPreference = "Stop"
$Root = if ($args.Count -gt 0) { $args[0] } else { (Get-Location).Path }
Set-Location $Root
[System.IO.Directory]::SetCurrentDirectory($Root)
$env:PYTHONPATH = (Join-Path $Root "src")
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
Write-Host "::group::compile"
python -m tessera loop compile --out reports/runtime_loop
Write-Host "::endgroup::"
Write-Host "::group::check"
python scripts/rcc/check_rcc_nexus.py
python scripts/validation/validate_architecture_contracts.py
python scripts/readme/audit_readme_nexus_discipline.py
python scripts/validation/validate_operator_shell.py
python scripts/validation/validate_runtime_loop_compiler.py
python -m unittest discover -s tests
Write-Host "::endgroup::"
Write-Host "::group::runtime"
python -m tessera run --out outputs --steps 80 --epochs 1 --topology q4 --field-dim 16 --code-dim 8
python -m tessera validate --run outputs/runs/latest
Write-Host "::endgroup::"
'''

BASH = r'''#!/usr/bin/env bash
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
'''

LESSONS = [
    "PowerShell can act as the local operator shell without becoming autonomous authority.",
    "Compressed groups and status rows are better than raw code visibility for repeated loops.",
    "Use local PYTHONPATH by default; pip install is an explicit operator action.",
    "Normalize JSON and markdown without BOM before validation.",
    "Use ASCII output to avoid Windows console encoding failures.",
    "Borrow Hermes governance separation; do not borrow Hermes runtime authority.",
    "Borrow ASF whole-loop visibility; do not claim ASF safety or truth.",
]


def ascii_text() -> str:
    rows = "\n".join(f"{n} {name:<10} :: {desc}" for n, name, desc in LOOP)
    return ASCII + "\n\n" + rows + "\n"


def manifest() -> dict:
    return {
        "schema": VERSION,
        "loop": [{"order": n, "stage": name, "purpose": desc} for n, name, desc in LOOP],
        "operator_shell": "scripts/tessera-shell.ps1",
        "commands": ["status", "compile", "check", "run", "validate", "full", "push", "help", "exit"],
        "outputs": {
            "ascii": "reports/runtime_loop/tessera_loop_ascii.txt",
            "manifest": "reports/runtime_loop/tessera_loop_manifest.json",
            "readme_section": "reports/runtime_loop/tessera_readme_operator_shell_section.md",
            "lessons": "reports/lessons/tessera_v0_2_2_operator_shell_lessons.md",
        },
        "claim_boundary": "Operator shell improves local visibility and repeatability. It does not prove correctness, safety, production readiness, or real telemetry transfer.",
    }


def readme_section() -> str:
    return dedent("""
    <!-- TESSERA_OPERATOR_SHELL_START -->
    ## Tessera v0.2.2 PowerShell Operator Shell

    Tessera now has a local Hermes-style PowerShell operator shell. It compresses the runtime loop into grouped sections, status rows, checkers, and run commands so the operator does not have to watch raw implementation code scroll by.

    ```text
    rehydrate -> shell -> compile -> check -> run -> validate -> ledger -> push -> root
    ```

    <details>
    <summary><strong>Open the operator shell</strong></summary>

    ```powershell
    cd "C:\\Users\\jacks\\OneDrive\\Desktop\\Tessera"
    .\\scripts\\tessera-shell.ps1
    ```

    Commands inside the shell:

    ```text
    status
    compile
    check
    run
    validate
    full
    push
    help
    exit
    ```

    </details>

    <details>
    <summary><strong>Run the full compressed loop without entering the shell</strong></summary>

    ```powershell
    cd "C:\\Users\\jacks\\OneDrive\\Desktop\\Tessera"
    .\\scripts\\run-tessera-full-loop.ps1
    ```

    Bash:

    ```bash
    ./scripts/run-tessera-full-loop.sh
    ```

    </details>

    <details>
    <summary><strong>Checkers</strong></summary>

    ```powershell
    python scripts/rcc/check_rcc_nexus.py
    python scripts/validation/validate_architecture_contracts.py
    python scripts/readme/audit_readme_nexus_discipline.py
    python scripts/validation/validate_operator_shell.py
    python scripts/validation/validate_runtime_loop_compiler.py
    python -m unittest discover -s tests
    python -m tessera validate --run outputs/runs/latest
    ```

    </details>

    <details>
    <summary><strong>Boundary</strong></summary>

    ```text
    The shell may observe.
    The shell may compile.
    The shell may run local validation.
    The shell may push after validation.
    The shell may not claim real telemetry transfer.
    The shell may not become autonomous authority.
    The shell may not import Hermes runtime authority or ASF safety claims.
    ```

    </details>

    <!-- TESSERA_OPERATOR_SHELL_END -->
    """).strip()


def compile_outputs(out: str | Path = "reports/runtime_loop") -> Path:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "tessera_loop_ascii.txt").write_text(ascii_text(), encoding="utf-8")
    (out / "tessera_loop_manifest.json").write_text(json.dumps(manifest(), indent=2), encoding="utf-8")
    (out / "tessera_readme_operator_shell_section.md").write_text(readme_section(), encoding="utf-8")
    Path("scripts").mkdir(exist_ok=True)
    Path("scripts/run-tessera-full-loop.ps1").write_text(POWERSHELL, encoding="utf-8")
    Path("scripts/run-tessera-full-loop.sh").write_text(BASH, encoding="utf-8")
    Path("reports/lessons").mkdir(parents=True, exist_ok=True)
    Path("reports/lessons/tessera_v0_2_2_operator_shell_lessons.md").write_text(
        "# Tessera v0.2.2 Operator Shell Lessons\n\n" + "\n".join(f"- {x}" for x in LESSONS) + "\n",
        encoding="utf-8",
    )
    return out


def cmd_ascii(_: argparse.Namespace) -> None:
    print(ascii_text())


def cmd_bash(_: argparse.Namespace) -> None:
    print(BASH)


def cmd_powershell(_: argparse.Namespace) -> None:
    print(POWERSHELL)


def cmd_manifest(_: argparse.Namespace) -> None:
    print(json.dumps(manifest(), indent=2))


def cmd_compile(args: argparse.Namespace) -> None:
    out = compile_outputs(args.out)
    print(f"TESSERA operator loop surfaces compiled: {out}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tessera loop", description="Compile Tessera operator shell loop surfaces.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name, fn in [("ascii", cmd_ascii), ("bash", cmd_bash), ("powershell", cmd_powershell), ("manifest", cmd_manifest)]:
        p = sub.add_parser(name)
        p.set_defaults(func=fn)
    c = sub.add_parser("compile")
    c.add_argument("--out", default="reports/runtime_loop")
    c.set_defaults(func=cmd_compile)
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()