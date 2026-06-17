import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED = [
    "docs/operator/TESSERA_AGENT_CLI_CONTRACT.md",
    "docs/loop/TESSERA_COMMAND_REGISTRY.md",
    "scripts/tessera-agent.ps1",
    "scripts/tessera-agent.sh",
    "scripts/agent-mirror.ps1",
    "scripts/agent-mirror.sh",
    "scripts/run-tessera-full-loop.ps1",
    "scripts/run-tessera-full-loop.sh",
    "src/tessera/agent_cli.py",
    "src/tessera/operator_geometry.py",
    "agent_cli_mirror/agent_mirror.py",
    "agent_cli_mirror/config/commands.json",
]

SCRIPT_TOKENS = {
    "scripts/tessera-agent.ps1": ["tessera.agent_cli", "launch", "--root", "NoPush", "SkipRun", "SkipTests"],
    "scripts/tessera-agent.sh": ["tessera.agent_cli", "launch", "--root", "--no-push", "--skip-run", "--skip-tests"],
    "scripts/agent-mirror.ps1": ["agent_mirror.py", "launch", "--command", "NoPush", "SkipRun", "SkipTests"],
    "scripts/agent-mirror.sh": ["agent_mirror.py", "launch", "--command", "--no-push", "--skip-run", "--skip-tests"],
    "scripts/run-tessera-full-loop.ps1": ["agent-mirror.ps1", "-Command", "full", "NoPush", "SkipRun", "SkipTests"],
    "scripts/run-tessera-full-loop.sh": ["agent-mirror.sh", "--command=full", "--root"],
}

README_TOKENS = [
    "Agent CLI",
    "Agent CLI Mirror",
    "Observer CLI opens first",
    "Worker CLI opens second",
    "PowerShell All-One Loop Box",
    "Bash All-One Loop Box",
]
REGISTRY_TOKENS = [
    "python -m tessera.agent_cli launch",
    ".\\scripts\\tessera-agent.ps1",
    "./scripts/tessera-agent.sh",
    ".\\scripts\\agent-mirror.ps1",
    "./scripts/agent-mirror.sh",
    "No operator-facing script bypasses the Agent CLI",
]
CONTRACT_TOKENS = [
    "No operator-facing script without Agent CLI entry",
    "No loop without Observer-first launch",
    "No internal validator may spawn another Observer",
]


def read(rel: str) -> str:
    p = ROOT / rel
    return p.read_text(encoding="utf-8") if p.exists() else ""


def main() -> int:
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    missing_script_tokens = {}
    for rel, tokens in SCRIPT_TOKENS.items():
        text = read(rel)
        miss = [t for t in tokens if t not in text]
        if miss:
            missing_script_tokens[rel] = miss
    readme = read("README.md")
    registry = read("docs/loop/TESSERA_COMMAND_REGISTRY.md")
    contract = read("docs/operator/TESSERA_AGENT_CLI_CONTRACT.md")
    missing_readme = [t for t in README_TOKENS if t not in readme]
    missing_registry = [t for t in REGISTRY_TOKENS if t not in registry]
    missing_contract = [t for t in CONTRACT_TOKENS if t not in contract]
    passed = not missing and not missing_script_tokens and not missing_readme and not missing_registry and not missing_contract
    report = {
        "schema": "TESSERA-v0.3.8-agent-cli-contract-validation",
        "passed": passed,
        "missing_files": missing,
        "missing_script_tokens": missing_script_tokens,
        "missing_readme_tokens": missing_readme,
        "missing_registry_tokens": missing_registry,
        "missing_contract_tokens": missing_contract,
        "claim_boundary": "Agent CLI contract validates operator surfaces only; it does not prove real telemetry transfer.",
    }
    out = ROOT / "reports/loopbook/latest_agent_cli_contract_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())