from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "docs/loop/loopbook_manifest.json"
LOOPBOOK = ROOT / "docs/loop/TESSERA_LOOPBOOK.md"
EXPECTED_SCHEMA = "TESSERA-loopbook-manifest-v0.2.8"

REQUIRED_FILES = [
    "docs/loop/TESSERA_LOOPBOOK.md", "docs/loop/loopbook_manifest.json", "scripts/loopbook/sync_loopbook.py",
    "scripts/run-tessera-full-loop.ps1", "scripts/run-tessera-full-loop.sh",
    "scripts/agent-mirror.ps1", "scripts/agent-mirror.sh", "agent_cli_mirror/agent_mirror.py",
]
README_TOKENS = [
    "PowerShell All-One Loop Box", "scripts\\run-tessera-full-loop.ps1",
    "Observer CLI opens first", "Worker CLI opens second", "Agent CLI Mirror",
]

def sha(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    missing = [p for p in REQUIRED_FILES if not (ROOT / p).exists()]
    manifest = {}
    stale = []
    schema = None
    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        schema = manifest.get("schema")
        for rel, expected in manifest.get("feature_hashes", {}).items():
            actual = sha(ROOT / rel)
            if expected is not None and actual != expected:
                stale.append({"path": rel, "expected": expected, "actual": actual})
    else:
        missing.append("docs/loop/loopbook_manifest.json")
    readme = (ROOT / "README.md").read_text(encoding="utf-8") if (ROOT / "README.md").exists() else ""
    loopbook = LOOPBOOK.read_text(encoding="utf-8") if LOOPBOOK.exists() else ""
    missing_readme = [t for t in README_TOKENS if t not in readme]
    missing_loopbook_tokens = [t for t in ["Canonical Command", "Gate Rule", "Observer PowerShell", "Worker PowerShell", "agent-cli-mirror"] if t not in loopbook]
    passed = (not missing and not stale and not missing_readme and not missing_loopbook_tokens and schema == EXPECTED_SCHEMA)
    report = {
        "schema": "TESSERA-loopbook-gate-validation-v0.2.8", "passed": passed, "manifest_schema": schema,
        "missing_files": missing, "stale_hashes": stale, "missing_readme_tokens": missing_readme, "missing_loopbook_tokens": missing_loopbook_tokens,
        "claim_boundary": "Loopbook gate validates operator run surfaces only; it does not prove real telemetry transfer.",
    }
    out = ROOT / "reports/loopbook/latest_loopbook_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if passed else 1

if __name__ == "__main__":
    raise SystemExit(main())
