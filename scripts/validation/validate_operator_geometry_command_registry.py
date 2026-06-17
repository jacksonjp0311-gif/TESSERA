import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def read(rel):
    p = ROOT / rel
    return p.read_text(encoding="utf-8") if p.exists() else ""
def main():
    required = ["docs/loop/TESSERA_COMMAND_REGISTRY.md","docs/loop/TESSERA_OPERATOR_LOOP_CHART.md","docs/loop/TESSERA_FAILURE_LESSONS.md","docs/alignment/TESSERA_ALIGNMENT_GEOMETRY_GAP.md","scripts/run-tessera-full-loop.ps1","scripts/run-tessera-full-loop.sh","src/tessera/operator_geometry.py"]
    readme = read("README.md"); registry = read("docs/loop/TESSERA_COMMAND_REGISTRY.md"); chart = read("docs/loop/TESSERA_OPERATOR_LOOP_CHART.md"); geom = read("docs/alignment/TESSERA_ALIGNMENT_GEOMETRY_GAP.md"); ps = read("scripts/run-tessera-full-loop.ps1"); sh = read("scripts/run-tessera-full-loop.sh")
    missing = [p for p in required if not (ROOT / p).exists()]
    missing_readme = [t for t in ["PowerShell All-One Loop Box","Bash All-One Loop Box","Observer CLI opens first","Command Registry","Failure Lessons Chart","Alignment and Geometry Gap"] if t not in readme]
    missing_registry = [t for t in ["python -m tessera.operator_geometry launch",".\\scripts\\run-tessera-full-loop.ps1","./scripts/run-tessera-full-loop.sh","Observer-first"] if t not in registry]
    missing_chart = [t for t in ["TESSERA OPERATOR GEOMETRY","LAUNCH-OBSERVER","LAUNCH-WORKER"] if t not in chart]
    missing_geom = [t for t in ["No command without registry","No loop without Observer-first launch","No feature without Loopbook/lessons/chart alignment"] if t not in geom]
    missing_ps = [t for t in ["tessera.operator_geometry","launch","--root","NoPush","SkipRun","SkipTests"] if t not in ps]
    missing_sh = [t for t in ["tessera.operator_geometry","launch","--root","--no-push","--skip-run","--skip-tests"] if t not in sh]
    root_engine = [p.name for p in ROOT.glob("TESSERA_ENGINE_*.md")]
    passed = not any([missing, missing_readme, missing_registry, missing_chart, missing_geom, missing_ps, missing_sh, root_engine])
    report = {"schema":"TESSERA-v0.3.2-operator-geometry-command-registry-validation","passed":passed,"missing_files":missing,"missing_readme_tokens":missing_readme,"missing_registry_tokens":missing_registry,"missing_chart_tokens":missing_chart,"missing_geometry_tokens":missing_geom,"missing_powershell_tokens":missing_ps,"missing_bash_tokens":missing_sh,"root_engine_markdown_files":root_engine,"claim_boundary":"operator geometry validation is not real telemetry transfer proof"}
    out = ROOT / "reports/loopbook/latest_operator_geometry_command_registry_gate.json"; out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(report, indent=2), encoding="utf-8"); print(json.dumps(report, indent=2)); return 0 if passed else 1
if __name__ == "__main__": raise SystemExit(main())
