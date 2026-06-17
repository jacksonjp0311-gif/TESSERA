import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
TOKENS = ["What Tessera Is","Current Health Snapshot","PowerShell All-One Loop Box","Bash All-One Loop Box","What Opens at the Start of Every Loop","Command Registry","Runtime Geometry","Failure Lessons Chart","Alignment and Geometry Gap","Non-Claim Lock","No manifest, no transfer claim","No baseline, no capability claim","No replay, no memory promotion","No validated loop, no push","Navigation is not validation","Synthetic success is not transfer"]
FILES = ["README.md","README_90_SECONDS.md","AGENTS.md","docs/loop/TESSERA_COMMAND_REGISTRY.md","docs/loop/TESSERA_OPERATOR_LOOP_CHART.md","docs/loop/TESSERA_FAILURE_LESSONS.md","docs/alignment/TESSERA_ALIGNMENT_GEOMETRY_GAP.md","scripts/run-tessera-full-loop.ps1","scripts/run-tessera-full-loop.sh","docs/readme/README_DISCIPLINE.md","rcc/nexus/route_map.json","docs/context/repository_context_index.json","docs/context/rcc_nexus_index.json","docs/alignment/non_claim_locks.md"]
def main():
    readme = (ROOT / "README.md").read_text(encoding="utf-8") if (ROOT / "README.md").exists() else ""
    missing_files = [p for p in FILES if not (ROOT / p).exists()]
    missing_tokens = [t for t in TOKENS if t not in readme]
    root_engine = [p.name for p in ROOT.glob("TESSERA_ENGINE_*.md")]
    passed = not missing_files and not missing_tokens and not root_engine
    report = {"schema":"TESSERA-readme-nexus-discipline-audit-v0.3.2","passed":passed,"missing_files":missing_files,"missing_readme_tokens":missing_tokens,"root_engine_markdown_files":root_engine,"claim_boundary":"README discipline is navigation and public-surface alignment, not code correctness or empirical validation"}
    out_json = ROOT / "reports/readme/latest_readme_nexus_discipline_audit.json"; out_md = ROOT / "reports/readme/latest_readme_nexus_discipline_audit.md"; out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    out_md.write_text("# Tessera README / Nexus Discipline Audit\n\n" + f"Passed: `{passed}`\n\n" + f"Missing files: `{missing_files}`\n\n" + f"Missing README tokens: `{missing_tokens}`\n\n" + f"Root engine markdown files: `{root_engine}`\n\nBoundary: README discipline is not code correctness, empirical validation, production readiness, or real telemetry transfer.\n", encoding="utf-8")
    print(json.dumps(report, indent=2)); return 0 if passed else 1
if __name__ == "__main__": raise SystemExit(main())
