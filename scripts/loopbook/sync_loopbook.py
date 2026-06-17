from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
LOOP_STEPS = ["rehydrate", "loopbook", "launch", "observe", "worker", "check", "run", "validate", "ledger", "push", "root"]
FEATURE_FILES = [
    "README.md", "README_90_SECONDS.md", "AGENTS.md", "docs/loop/TESSERA_LOOPBOOK.md",
    "scripts/run-tessera-full-loop.ps1", "scripts/tessera-dual-console.ps1", "scripts/tessera-worker.ps1",
    "scripts/tessera-watch.ps1", "scripts/validation/validate_loopbook_gate.py", "src/tessera/loop_compiler.py", "src/tessera/cli.py",
]

def sha(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git_head() -> str:
    try:
        return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"

def loopbook_md(manifest: dict) -> str:
    rows = "\n".join(f"{i+1}. `{step}`" for i, step in enumerate(LOOP_STEPS))
    return f"""# TESSERA Loopbook

## Purpose

The Loopbook is the canonical operator run record for Tessera. Every feature that changes the runtime loop, scripts, validation path, README run surface, or operator interface must update this file and `docs/loop/loopbook_manifest.json`.

```text
rehydrate -> loopbook -> launch -> observe -> worker -> check -> run -> validate -> ledger -> push -> root
```

## Canonical Command

```powershell
cd "C:\\Users\\jacks\\OneDrive\\Desktop\\Tessera"
.\\scripts\\run-tessera-full-loop.ps1
```

Dry run without push:

```powershell
.\\scripts\\run-tessera-full-loop.ps1 -NoPush
```

## What Opens Every Time

```text
Observer PowerShell = read-only human interface
Worker PowerShell   = local code runner
```

## Loop Steps

{rows}

## Gate Rule

```text
If feature surfaces change, sync the Loopbook.
If the Loopbook manifest is stale, validation fails.
If validation fails, no commit/push promotion.
```

## Expected Result

1. Repository root is locked.
2. Loopbook sync runs.
3. Observer PowerShell opens.
4. Worker PowerShell opens.
5. Checkers run.
6. Tessera runtime runs.
7. Latest evidence validates.
8. Ledger/report files update.
9. Git commit/push runs unless `-NoPush` is used.
10. RootMirror returns to the Tessera root.

## Non-Claim Boundary

The Loopbook does not prove truth, safety, production readiness, code correctness, AGI, consciousness, or real telemetry transfer. It records and gates the operator loop.

## Current Manifest Snapshot

```json
{json.dumps(manifest, indent=2)}
```
"""

def main() -> int:
    manifest = {
        "schema": "TESSERA-loopbook-manifest-v0.2.6",
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_head": git_head(),
        "loop_steps": LOOP_STEPS,
        "canonical_loopbook": "docs/loop/TESSERA_LOOPBOOK.md",
        "canonical_command": ".\\scripts\\run-tessera-full-loop.ps1",
        "observer": "scripts/tessera-watch.ps1",
        "worker": "scripts/tessera-worker.ps1",
        "launcher": "scripts/tessera-dual-console.ps1",
        "gate": "scripts/validation/validate_loopbook_gate.py",
        "feature_hashes": {},
        "claim_boundary": "Loopbook sync records operator surfaces only; it does not prove real telemetry transfer.",
    }
    for rel in FEATURE_FILES:
        manifest["feature_hashes"][rel] = sha(ROOT / rel)
    (ROOT / "docs/loop").mkdir(parents=True, exist_ok=True)
    (ROOT / "docs/loop/TESSERA_LOOPBOOK.md").write_text(loopbook_md(manifest), encoding="utf-8")
    manifest["feature_hashes"]["docs/loop/TESSERA_LOOPBOOK.md"] = sha(ROOT / "docs/loop/TESSERA_LOOPBOOK.md")
    (ROOT / "docs/loop/loopbook_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"schema": "TESSERA-loopbook-sync-v0.2.6", "status": "synced", "loopbook": "docs/loop/TESSERA_LOOPBOOK.md"}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())