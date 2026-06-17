from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
REQUIRED = [
    "src/tessera/loop_compiler.py",
    "scripts/run-tessera-full-loop.ps1",
    "scripts/run-tessera-full-loop.sh",
    "reports/runtime_loop/tessera_loop_ascii.txt",
    "reports/runtime_loop/tessera_loop_manifest.json",
]

def run(args):
    return subprocess.run(args, cwd=ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True)

def main() -> int:
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    failures = []
    commands = [
        [sys.executable, "-m", "tessera", "loop", "ascii"],
        [sys.executable, "-m", "tessera", "loop", "manifest"],
    ]
    for cmd in commands:
        p = run(cmd)
        if p.returncode != 0:
            failures.append({"command": cmd, "stderr": p.stderr[-1200:]})
    manifest_ok = False
    schema = None
    mp = ROOT / "reports/runtime_loop/tessera_loop_manifest.json"
    if mp.exists():
        data = json.loads(mp.read_text(encoding="utf-8"))
        schema = data.get("schema")
        manifest_ok = schema == "TESSERA-runtime-loop-compiler-v0.2.2"
    report = {
        "schema": "TESSERA-runtime-loop-compiler-validation-v0.2.2",
        "passed": not missing and not failures and manifest_ok,
        "missing": missing,
        "failures": failures,
        "manifest_schema": schema,
        "claim_boundary": "Runtime loop compilation proves operator visibility only; it does not prove transfer, safety, or correctness.",
    }
    out = ROOT / "reports/runtime_loop/latest_runtime_loop_compiler_validation.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1
if __name__ == "__main__":
    raise SystemExit(main())