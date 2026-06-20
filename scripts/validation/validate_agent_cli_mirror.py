from __future__ import annotations

import json
import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = [
    "agent_cli_mirror/README.md",
    "agent_cli_mirror/AGENT_CLI_MIRROR_CONTRACT.md",
    "agent_cli_mirror/agent_mirror.py",
    "agent_cli_mirror/config/commands.json",
    "agent_cli_mirror/docs/TRANSPLANT.md",
    "agent_cli_mirror/docs/INTERFACE.md",
    "agent_cli_mirror/LEARNED_LESSONS.md",
    "scripts/agent-mirror.ps1",
    "scripts/agent-mirror.sh",
    "scripts/run-tessera-full-loop.ps1",
    "scripts/run-tessera-full-loop.sh",
]
README_TOKENS = [
    "Agent CLI Mirror",
    "Transplantable Root Module",
    "Observer opens before Worker",
    "scripts as agent/API calls",
    "agent_cli_mirror/",
    "No operator-facing script bypasses the Agent CLI Mirror",
]


def read(rel: str) -> str:
    path = ROOT / rel
    return path.read_text(encoding="utf-8") if path.exists() else ""


def main() -> int:
    missing_files = [rel for rel in REQUIRED if not (ROOT / rel).exists()]
    readme = read("README.md")
    missing_readme = [token for token in README_TOKENS if token not in readme]
    config_path = ROOT / "agent_cli_mirror/config/commands.json"
    missing_commands = []
    schema_ok = False
    syntax_errors = []
    launcher_path = ROOT / "agent_cli_mirror/agent_mirror.py"
    if launcher_path.exists():
        try:
            py_compile.compile(str(launcher_path), doraise=True)
        except py_compile.PyCompileError as exc:
            syntax_errors.append(str(exc))
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
            schema_ok = config.get("schema") == "AGENT-CLI-MIRROR-COMMANDS-v0.3.9"
            for command in ["full", "validate", "diagnostic", "status"]:
                if command not in config.get("commands", {}):
                    missing_commands.append(command)
        except json.JSONDecodeError as exc:
            syntax_errors.append(f"commands.json: {exc}")
    else:
        missing_commands = ["full", "validate", "diagnostic", "status"]
    passed = not missing_files and not missing_readme and not missing_commands and schema_ok and not syntax_errors
    report = {
        "schema": "TESSERA-agent-cli-mirror-validation-v0.3.9",
        "passed": passed,
        "missing_files": missing_files,
        "missing_readme_tokens": missing_readme,
        "missing_commands": missing_commands,
        "command_schema_ok": schema_ok,
        "syntax_errors": syntax_errors,
        "claim_boundary": "Agent CLI Mirror validation checks operator surfaces only; it does not prove autonomy, safety, correctness, or real telemetry transfer.",
    }
    out = ROOT / "reports/agent_cli_mirror/latest_agent_cli_mirror_validation.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
