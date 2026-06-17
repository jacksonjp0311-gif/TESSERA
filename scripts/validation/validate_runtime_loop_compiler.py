from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = [
    "src/tessera/loop_compiler.py",
    "docs/interlock/hermes_evo_rehydration_extract.md",
    "docs/interlock/tessera_hermes_interlock_geometry.json",
    "docs/lessons/TESSERA_V0_2_0_INTERLOCK_LESSONS.md",
]

def main() -> int:
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    commands = [
        [sys.executable, "-m", "tessera", "loop", "ascii"],
        [sys.executable, "-m", "tessera", "loop", "manifest"],
        [sys.executable, "-m", "tessera", "loop", "compile", "--out", "reports/runtime_loop"],
    ]
    failures = []
    for cmd in commands:
        proc = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode != 0:
            failures.append({"command": cmd, "stderr": proc.stderr[-1000:]})
    manifest = ROOT / "reports/runtime_loop/tessera_runtime_loop_manifest.json"
    manifest_ok = manifest.exists()
    if manifest_ok:
        data = json.loads(manifest.read_text(encoding="utf-8"))
        manifest_ok = data.get("schema") == "TESSERA-runtime-loop-compiler-v0.2.0"
    report = {
        "schema": "TESSERA-runtime-loop-compiler-validation-v0.2.0",
        "passed": not missing and not failures and manifest_ok,
        "missing": missing,
        "failures": failures,
        "manifest_ok": manifest_ok,
        "claim_boundary": "Runtime loop compilation proves operator visibility only; it does not prove transfer, safety, or correctness.",
    }
    out = ROOT / "reports/runtime_loop/latest_runtime_loop_compiler_validation.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return int(not report["passed"])

if __name__ == "__main__":
    raise SystemExit(main())