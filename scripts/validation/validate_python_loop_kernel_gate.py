from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = [
    "src/tessera/loop_runtime.py",
    "scripts/run-tessera-full-loop.ps1",
    "docs/loop/TESSERA_LOOPBOOK.md",
    "docs/loop/TESSERA_FAILURE_LESSONS.md",
    "docs/loop/TESSERA_OPERATOR_LOOP_CHART.md",
]
TOKENS = {
    "docs/loop/TESSERA_LOOPBOOK.md": ["python-loop-kernel", "Canonical Python Command"],
    "docs/loop/TESSERA_FAILURE_LESSONS.md": ["Failure must become a lesson", "PowerShell should launch terminals only"],
    "docs/loop/TESSERA_OPERATOR_LOOP_CHART.md": ["Python owns", "PowerShell owns"],
}

def main() -> int:
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    token_failures = []
    for rel, toks in TOKENS.items():
        path = ROOT / rel
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        for tok in toks:
            if tok not in text:
                token_failures.append({"path": rel, "missing": tok})
    report = {
        "schema": "TESSERA-python-loop-kernel-gate-v0.2.8",
        "passed": not missing and not token_failures,
        "missing_files": missing,
        "token_failures": token_failures,
        "claim_boundary": "Python loop kernel gate validates operator surfaces only; it does not prove real telemetry transfer.",
    }
    out = ROOT / "reports/loopbook/latest_python_loop_kernel_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1

if __name__ == "__main__":
    raise SystemExit(main())