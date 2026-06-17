from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = [
    "docs/loop/TESSERA_FAILURE_LESSONS.md",
    "docs/loop/TESSERA_OPERATOR_LOOP_CHART.md",
    "docs/loop/TESSERA_README_FEATURE_IMPORTS.md",
    "docs/context/tessera_v0_2_7_failure_lessons_chart_manifest.json",
]
README_TOKENS = [
    "TESSERA Failure Lessons + Loop Chart Gate",
    "docs/loop/TESSERA_FAILURE_LESSONS.md",
    "docs/loop/TESSERA_OPERATOR_LOOP_CHART.md",
    "Failure -> Lesson -> Gate",
]
LESSON_TOKENS = [
    "F01", "F02", "F03", "F04", "F05", "F06", "F07", "F08", "F09", "F10", "F11", "F12", "F13", "F14",
    "git -C <Root>", "UTF-8 no BOM", "dual-console", "Loopbook"
]
CHART_TOKENS = ["TESSERA OPERATOR LOOP", "Mermaid Chart", "Observer PowerShell", "Worker PowerShell", "No validation pass"]
IMPORT_TOKENS = ["One-command full loop", "UI starts before loop", "Read-only UI law", "Non-claim lock"]


def text(path: str) -> str:
    p = ROOT / path
    return p.read_text(encoding="utf-8") if p.exists() else ""


def main() -> int:
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    readme = text("README.md")
    lessons = text("docs/loop/TESSERA_FAILURE_LESSONS.md")
    chart = text("docs/loop/TESSERA_OPERATOR_LOOP_CHART.md")
    imports = text("docs/loop/TESSERA_README_FEATURE_IMPORTS.md")
    missing_readme = [t for t in README_TOKENS if t not in readme]
    missing_lessons = [t for t in LESSON_TOKENS if t not in lessons]
    missing_chart = [t for t in CHART_TOKENS if t not in chart]
    missing_imports = [t for t in IMPORT_TOKENS if t not in imports]
    report = {
        "schema": "TESSERA-v0.2.7-failure-lessons-chart-gate-validation",
        "passed": not missing and not missing_readme and not missing_lessons and not missing_chart and not missing_imports,
        "missing_files": missing,
        "missing_readme_tokens": missing_readme,
        "missing_lessons_tokens": missing_lessons,
        "missing_chart_tokens": missing_chart,
        "missing_import_tokens": missing_imports,
        "claim_boundary": "Failure lessons chart gate validates operator documentation surfaces only; it does not prove real telemetry transfer.",
    }
    out = ROOT / "reports/loopbook/latest_failure_lessons_chart_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())