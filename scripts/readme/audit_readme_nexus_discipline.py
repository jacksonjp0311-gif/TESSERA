import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_README_TOKENS = [
    "Human Director Box",
    "PART I — Human README",
    "PART II — RCC Nexus README",
    "PART III — AI Agent README",
    "Current Health Snapshot",
    "Run the Whole Tessera Local Loop",
    "What this repository is not",
    "No manifest, no transfer claim",
    "No baseline, no capability claim",
    "No replay, no memory promotion",
    "No human authorization, no push",
    "Navigation is not validation",
    "Synthetic success is not transfer",
]

REQUIRED_FILES = [
    "README.md",
    "README_90_SECONDS.md",
    "AGENTS.md",
    "docs/readme/README_DISCIPLINE.md",
    "docs/benchmarks/current_public_metrics.md",
    "rcc/nexus/route_map.json",
    "docs/context/repository_context_index.json",
    "docs/context/rcc_nexus_index.json",
    "docs/alignment/non_claim_locks.md",
]


def main() -> int:
    readme_path = ROOT / "README.md"
    readme_text = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    missing_files = [p for p in REQUIRED_FILES if not (ROOT / p).exists()]
    missing_tokens = [t for t in REQUIRED_README_TOKENS if t not in readme_text]
    route_ok = False
    route_path = ROOT / "rcc/nexus/route_map.json"
    if route_path.exists():
        try:
            route = json.loads(route_path.read_text(encoding="utf-8"))
            routes = route.get("routes", [])
            route_ok = "readme_discipline" in route and any(isinstance(r, dict) and r.get("id") == "readme_discipline" for r in routes)
        except Exception:
            route_ok = False
    passed = not missing_files and not missing_tokens and route_ok
    report = {
        "schema": "TESSERA-readme-nexus-discipline-audit-v0.1.2",
        "passed": passed,
        "missing_files": missing_files,
        "missing_readme_tokens": missing_tokens,
        "route_map_readme_discipline_present": route_ok,
        "claim_boundary": "README discipline is navigation and public-surface alignment, not code correctness or empirical validation",
    }
    out_json = ROOT / "reports/readme/latest_readme_nexus_discipline_audit.json"
    out_md = ROOT / "reports/readme/latest_readme_nexus_discipline_audit.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    out_md.write_text(
        "# Tessera README / Nexus Discipline Audit\n\n"
        f"Passed: `{passed}`\n\n"
        f"Missing files: `{missing_files}`\n\n"
        f"Missing README tokens: `{missing_tokens}`\n\n"
        f"Route map README discipline present: `{route_ok}`\n\n"
        "Boundary: README discipline is not code correctness, empirical validation, production readiness, or real telemetry transfer.\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))
    return int(not passed)

if __name__ == "__main__":
    raise SystemExit(main())
