from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
REQUIRED = [
    "scripts/tessera-shell.ps1",
    "scripts/run-tessera-full-loop.ps1",
    "scripts/run-tessera-full-loop.sh",
    "src/tessera/loop_compiler.py",
    "reports/runtime_loop/tessera_loop_manifest.json",
    "reports/runtime_loop/tessera_readme_operator_shell_section.md",
    "docs/operator_shell/TESSERA_OPERATOR_SHELL_V0_2_2.md",
    "docs/context/tessera_v0_2_2_operator_shell_interlock.json",
]
README_TOKENS = [
    "Tessera v0.2.2 PowerShell Operator Shell",
    "<details>",
    "scripts\\tessera-shell.ps1",
    "status",
    "compile",
    "full",
    "The shell may observe.",
]

def main() -> int:
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    readme = (ROOT / "README.md").read_text(encoding="utf-8") if (ROOT / "README.md").exists() else ""
    missing_tokens = [t for t in README_TOKENS if t not in readme]
    manifest_path = ROOT / "reports/runtime_loop/tessera_loop_manifest.json"
    manifest_schema = None
    manifest_ok = False
    if manifest_path.exists():
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_schema = data.get("schema")
        manifest_ok = manifest_schema == "TESSERA-runtime-loop-compiler-v0.2.2"
    report = {
        "schema": "TESSERA-v0.2.2-operator-shell-validation",
        "passed": not missing and not missing_tokens and manifest_ok,
        "missing_files": missing,
        "missing_readme_tokens": missing_tokens,
        "manifest_schema": manifest_schema,
        "claim_boundary": "Operator shell validation checks shell surfaces and README links only; it does not prove real telemetry transfer.",
    }
    out = ROOT / "reports/runtime_loop/latest_operator_shell_validation.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1

if __name__ == "__main__":
    raise SystemExit(main())