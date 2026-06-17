import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED_DIRS = [
    "docs/alignment", "docs/context", "docs/theory", "docs/readme", "docs/benchmarks",
    "rcc/nexus", "src/tessera", "tests", "reports/rcc_nexus", "reports/validation", "reports/readme",
]
REQUIRED_FILES = [
    "docs/readme/README_DISCIPLINE.md",
    "docs/benchmarks/current_public_metrics.md",
    "scripts/readme/audit_readme_nexus_discipline.py",
]
REQUIRED_LOCKS = ["navigation_is_not_validation", "documentation_is_not_correctness", "synthetic_success_is_not_transfer", "validation_remains_required"]

def main() -> int:
    errors=[]
    missing_dirs=[p for p in REQUIRED_DIRS if not (ROOT/p).exists()]
    missing_files=[p for p in REQUIRED_FILES if not (ROOT/p).exists()]
    locks_path=ROOT/"docs/alignment/non_claim_locks.md"
    locks_text=locks_path.read_text(encoding="utf-8") if locks_path.exists() else ""
    missing_locks=[x for x in REQUIRED_LOCKS if x not in locks_text]
    theory_ok=(ROOT/"docs/theory/import_manifest.json").exists()
    for x in missing_dirs: errors.append(f"missing_dir:{x}")
    for x in missing_files: errors.append(f"missing_file:{x}")
    for x in missing_locks: errors.append(f"missing_lock:{x}")
    if not theory_ok: errors.append("missing_theory_manifest")
    passed=not errors
    report={
        "schema":"TESSERA-architecture-contract-validation-v0.1.2",
        "passed":passed,
        "status":"passed" if passed else "failed",
        "errors":errors,
        "missing_dirs":missing_dirs,
        "missing_files":missing_files,
        "missing_locks":missing_locks,
        "theory_manifest_present":theory_ok,
        "readme_discipline_present":(ROOT/"docs/readme/README_DISCIPLINE.md").exists(),
        "claim_boundary":"architecture validation is not empirical validation",
    }
    out=ROOT/"reports/validation/latest_architecture_contract_validation.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return int(not passed)
if __name__ == "__main__":
    raise SystemExit(main())
