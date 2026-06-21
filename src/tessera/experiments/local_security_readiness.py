from __future__ import annotations

import ast
import re
import subprocess
from pathlib import Path

from tessera.plugin.contracts import PluginPermissions


SECRET_PATTERNS = {
    "openai_key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "private_key": re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY"),
}


def _tracked_files(root: Path) -> list[Path]:
    result = subprocess.run(
        [
            "git", "ls-files", "--cached", "--others", "--exclude-standard",
            "--", "src", "scripts", "tests", "configs",
            "pyproject.toml", "README.md", "AGENTS.md",
        ],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    return [
        root / line.strip()
        for line in result.stdout.splitlines()
        if line.strip()
    ]


def _python_findings(path: Path) -> list[dict]:
    findings = []
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = ""
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            if (
                isinstance(node.func, ast.Name)
                and name in {"eval", "exec"}
            ):
                findings.append({
                    "file": str(path),
                    "line": node.lineno,
                    "kind": f"dynamic_execution:{name}",
                })
            if name in {"run", "Popen", "call", "check_call", "check_output"}:
                if any(
                    keyword.arg == "shell"
                    and isinstance(keyword.value, ast.Constant)
                    and keyword.value.value is True
                    for keyword in node.keywords
                ):
                    findings.append({
                        "file": str(path),
                        "line": node.lineno,
                        "kind": "subprocess_shell_true",
                    })
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            modules = (
                [alias.name for alias in node.names]
                if isinstance(node, ast.Import)
                else [node.module or ""]
            )
            if "src/tessera/plugin" in path.as_posix() and any(
                module.split(".")[0]
                in {"requests", "httpx", "urllib3", "socket"}
                for module in modules
            ):
                findings.append({
                    "file": str(path),
                    "line": node.lineno,
                    "kind": "plugin_network_import",
                })
    return findings


def run_local_security_readiness(root: str | Path = ".") -> dict:
    root = Path(root).resolve()
    tracked = _tracked_files(root)
    python_findings = []
    secret_findings = []
    for path in tracked:
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if path.suffix == ".py" and relative.startswith(("src/", "scripts/")):
            python_findings.extend(_python_findings(path))
        if path.suffix.lower() not in {
            ".py", ".json", ".toml", ".yaml", ".yml", ".md", ".ps1", ".sh"
        }:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                secret_findings.append({
                    "file": relative,
                    "kind": name,
                })

    permissions = PluginPermissions()
    denied_authorities = {
        "host_memory_write": permissions.host_memory_write,
        "tool_invocation": permissions.tool_invocation,
        "prompt_mutation": permissions.prompt_mutation,
        "live_codec_replacement": permissions.live_codec_replacement,
        "topology_mutation": permissions.topology_mutation,
        "external_api_calls": permissions.external_api_calls,
    }
    checkpoint_source = (
        root / "src/tessera/plugin/neural_checkpoints.py"
    ).read_text(encoding="utf-8")
    supervisor_source = (
        root / "src/tessera/plugin/supervisor.py"
    ).read_text(encoding="utf-8")
    checks = {
        "tracked_secret_scan_clean": not secret_findings,
        "no_dynamic_execution_or_shell_true": not python_findings,
        "plugin_network_authority_denied": (
            not permissions.external_api_calls
        ),
        "mutation_authorities_denied": not any(denied_authorities.values()),
        "checkpoint_deserialization_uses_weights_only": (
            "weights_only=True" in checkpoint_source
        ),
        "supervisor_uses_spawned_process_boundary": (
            'mp.get_context("spawn")' in supervisor_source
        ),
        "hard_timeout_and_circuit_breaker_present": (
            "hard_timeout" in supervisor_source
            and "_circuit_open" in supervisor_source
        ),
    }
    return {
        "schema": "TESSERA-EVO-036-LOCAL-SECURITY-v0.1",
        "passed": all(checks.values()),
        "checks": checks,
        "metrics": {
            "release_files_scanned": len(tracked),
            "python_findings": len(python_findings),
            "secret_findings": len(secret_findings),
            "denied_authorities": len(denied_authorities),
        },
        "findings": {
            "python": python_findings,
            "secrets": secret_findings,
        },
        "external_security_review_complete": False,
        "claim_boundary": (
            "Local static checks reduce obvious release risk but are not an "
            "independent vulnerability assessment, penetration test, or "
            "security certification."
        ),
    }
