from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "v0.2.8"
LOOP_STEPS = ["rehydrate", "agent-cli-mirror", "loopbook", "launch", "observe", "worker", "check", "run", "validate", "ledger", "push", "root"]
FEATURE_FILES = [
    "README.md", "README_90_SECONDS.md", "AGENTS.md", "docs/loop/TESSERA_LOOPBOOK.md",
    "docs/loop/TESSERA_FAILURE_LESSONS.md", "docs/loop/TESSERA_OPERATOR_LOOP_CHART.md",
    "scripts/run-tessera-full-loop.ps1", "scripts/run-tessera-full-loop.sh",
    "scripts/agent-mirror.ps1", "scripts/agent-mirror.sh",
    "scripts/loopbook/sync_loopbook.py", "scripts/validation/validate_loopbook_gate.py",
    "agent_cli_mirror/agent_mirror.py", "agent_cli_mirror/config/commands.json",
    "docs/context/rhp/latest-rhp.json", "docs/context/nexus/surface_registry.json",
    "docs/geometry/repository_geometry.json", "docs/lessons/lesson_chart.json",
    "docs/roadmap/tessera_evolutionary_roadmap.json",
    "docs/research/CROSS_DOMAIN_EVOLUTION_2026-06-19.md",
    "docs/research/MULTISCALE_AWARENESS_EVOLUTION_2026-06-19.md",
    "docs/research/NAB_T1_TRANSFER_2026-06-19.md",
    "datasets/nab/source_manifest.json",
    "src/tessera/experiments/run_nab_transfer.py",
    "datasets/telemanom/source_manifest.json",
    "src/tessera/experiments/run_smap_transfer.py",
    "docs/research/NASA_SMAP_DIAGNOSTIC_2026-06-19.md",
    "datasets/ucr/source_manifest.json",
    "src/tessera/experiments/run_ucr_transfer.py",
    "src/tessera/metrics/subsequence.py",
    "docs/research/UCR_SUBSEQUENCE_EVOLUTION_2026-06-19.md",
    "src/tessera/memory/episodes.py",
    "docs/research/UCR_EPISODE_GOVERNANCE_2026-06-19.md",
    "src/tessera/metrics/router.py",
    "docs/research/UCR_SENSOR_ROUTER_2026-06-19.md",
    "src/tessera/memory/gates.py",
    "docs/research/UCR_ABSTENTION_MEMORY_NORMALITY_2026-06-19.md",
    "src/tessera/baselines/pca_codec.py",
    "src/tessera/baselines/random_projection.py",
    "src/tessera/baselines/matrix_profile.py",
    "docs/research/UCR_SELECTIVE_FUSION_2026-06-19.md",
    "src/tessera/model/prediction_experts.py",
    "docs/research/UCR_PREDICTION_EXPERT_TRANSFER_2026-06-19.md",
    "src/tessera/plugin/contracts.py",
    "src/tessera/plugin/runtime.py",
    "docs/research/NAB_ENHANCED_NETWORK_DIAGNOSTIC_2026-06-19.md",
    "src/tessera/experiments/trajectory_benchmark.py",
    "docs/research/OFFLINE_TRAJECTORY_UTILITY_2026-06-19.md",
    "docs/research/PRECURSOR_TRAJECTORY_UTILITY_2026-06-19.md",
    "src/tessera/plugin/privacy_capture.py",
    "docs/research/LOCAL_TRAJECTORY_PRIVACY_DIAGNOSTIC_2026-06-19.md",
    "docs/research/LOCAL_TRAJECTORY_IDENTIFIABILITY_2026-06-19.md",
    "docs/research/PHASE_CONDITIONED_TELEMETRY_SPECIALIST_2026-06-19.md",
    "docs/research/FINITE_SAMPLE_WORKFLOW_SHADOW_2026-06-19.md",
    "docs/research/NATURAL_CLEAN_SESSION_CALIBRATION_2026-06-20.md",
    "docs/research/NATURAL_PROFILE_PERTURBATION_RESPONSE_2026-06-20.md",
    "docs/research/EVO022_PERTURBATION_PREREGISTRATION.json",
    "docs/research/NATURAL_TAIL_MODE_AUDIT_2026-06-20.md",
    "docs/research/EVO023_MODE_AUDIT_PREREGISTRATION.json",
    "docs/research/AGGREGATE_CONTEXT_ATTRIBUTION_2026-06-20.md",
    "docs/research/EVO024_CONTEXT_ATTRIBUTION_PREREGISTRATION.json",
    "scripts/telemetry/probe.py",
    "outputs/evidence/evo020/clean_calibration.json",
    "outputs/evidence/evo020/controlled_confirmation.json",
    "outputs/evidence/evo020/natural_shadow.json",
    "outputs/evidence/evo020/frozen_calibration.json",
    "outputs/evidence/evo020/evo020_shadow_report.json",
    "outputs/evidence/evo021/natural_clean_confirmation.json",
    "outputs/evidence/evo021/natural_clean_shadow_report.json",
    "outputs/evidence/evo021/natural_split_calibration.json",
    "outputs/evidence/evo021/frozen_session_calibration.json",
    "outputs/evidence/evo021/natural_session_confirmation.json",
    "outputs/evidence/evo021/natural_session_shadow_report.json",
    "outputs/evidence/evo022/perturbation_response.json",
    "outputs/evidence/evo023/mode_audit.json",
    "outputs/evidence/evo024/fresh_context_cohort.json",
    "outputs/evidence/evo024/context_attribution.json",
    "src/tessera/rhp/core.py", "scripts/validation/validate_rhp_nexus.py",
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
rehydrate -> agent-cli-mirror -> loopbook -> launch -> observe -> worker -> check -> run -> validate -> ledger -> push -> root
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
Worker PowerShell   = registered Agent CLI Mirror command runner
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
2. Agent CLI Mirror validates its launcher and command registry.
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
        "schema": f"TESSERA-loopbook-manifest-{SCHEMA_VERSION}",
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_head": git_head(),
        "loop_steps": LOOP_STEPS,
        "canonical_loopbook": "docs/loop/TESSERA_LOOPBOOK.md",
        "canonical_command": ".\\scripts\\run-tessera-full-loop.ps1",
        "agent_cli_mirror": "agent_cli_mirror/agent_mirror.py",
        "observer": "agent_cli_mirror/agent_mirror.py observe",
        "worker": "agent_cli_mirror/agent_mirror.py worker",
        "launcher": "scripts/agent-mirror.ps1",
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
    print(json.dumps({"schema": f"TESSERA-loopbook-sync-{SCHEMA_VERSION}", "status": "synced", "loopbook": "docs/loop/TESSERA_LOOPBOOK.md"}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
