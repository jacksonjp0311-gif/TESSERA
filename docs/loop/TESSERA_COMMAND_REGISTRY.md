# TESSERA Command Registry

## Purpose

Every operational command must be documented here and mirrored in the README when it is part of the public loop surface.

| Command | Purpose |
|---|---|
| `python -m tessera.agent_cli validate` | Validate command registry, README geometry, loop scripts, and docs. |
| `python -m tessera.agent_cli launch` | Open Observer CLI first, then Worker CLI. |
| `python -m tessera.agent_cli observe` | Run the read-only Observer CLI. |
| `python -m tessera.agent_cli worker` | Run the Python-owned Worker loop. |
| `python -m tessera.agent_cli chart` | Print the operator loop chart. |
| `python -m tessera.agent_cli lessons` | Print failure lessons. |
| `python -m tessera.agent_cli commands` | Print this command registry. |
| `python -m tessera.rhp rehydrate --root .` | Rebuild bounded zero-context state from the latest RHP pointer and evidence. |
| `python -m tessera.rhp validate --root .` | Validate RHP lineage, Nexus routes, mini READMEs, lessons, and repository geometry. |
| `python scripts/validation/validate_rhp_nexus.py` | Write the unified RHP-Nexus promotion report. |
| `python -m tessera benchmark --seeds 11,23,37` | Run a deterministic multi-seed synthetic benchmark. |
| `python -m tessera transfer-nab --root datasets/nab --depth 3 --hidden-dim 128 --epochs 10` | Run the EVO-014 enhanced NAB diagnostic while preserving the canonical supported codec. |
| `python -m tessera transfer-smap --channel P-1 --root .` | Run a pinned NASA SMAP Telemanom channel diagnostic with inherited-leakage lock. |
| `python -m tessera transfer-ucr --filename 174_UCR_Anomaly_insectEPG2_3700_8000_8025.txt --role confirmation` | Run the preregistered UCR subsequence confirmation. |
| `python -m tessera transfer-ucr --filename 229_UCR_Anomaly_mit14134longtermecg_16363_57960_57970.txt --role confirmation --sensor-mode router --episode-quarantine 12 --epochs 3` | Reproduce the EVO-008 point-tile confirmation and diagnostic routed-governance result. |
| `python -m tessera transfer-ucr --filename 155_UCR_Anomaly_PowerDemand4_18000_24005_24077.txt --role confirmation --sensor-mode abstaining-router --episode-quarantine 12 --epochs 3` | Reproduce the EVO-009 abstention and independent memory-normality confirmation. |
| `python -m tessera transfer-ucr --filename 235_UCR_Anomaly_mit14157longtermecg_18913_75450_75451.txt --role confirmation --sensor-mode selective-router --episode-quarantine 12 --epochs 3` | Reproduce the EVO-010 coverage-constrained point confirmation. |
| `python -m tessera transfer-ucr --filename 115_UCR_Anomaly_CIMIS44AirTemperature3_4000_6520_6544.txt --role confirmation --sensor-mode selective-router --episode-quarantine 12 --epochs 3` | Run the EVO-011 supported UCR T1 confirmation with validation-selected forecasting. |
| `python -m tessera plugin-demo --events 8` | Run the permission-bounded sparse-neural sidecar prototype. |
| `python -m tessera repair --seed 42 --steps 300 --channels 3 --epochs 2 --depth 2 --hidden-dim 64` | Run the replay-gated five-arm shadow repair ablation. |
| `python -m tessera trajectory-benchmark --seeds 0,1,2,3,4,5,6,7,8,9,10,11 --length 12` | Run the offline typed trajectory benchmark against recency and summary controls. |
| `python -m tessera trajectory-benchmark --seeds 100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123 --length 12 --precursor-only` | Run the fresh precursor-only utility benchmark without explicit failure flags. |
| `python -m tessera trajectory-local --events agent_cli_mirror/state/events.jsonl --minimum-prefix 7` | Privacy-audit and benchmark sanitized local Agent CLI Mirror sessions. |
| `python -m tessera trajectory-phase-holdout --events agent_cli_mirror/state/events.jsonl --minimum-prefix 9 --calibration-sessions 8 --holdout-sessions 8` | Calibrate normal phase-duration bounds and evaluate the frozen specialist on a later controlled holdout. |
| `python -m tessera trajectory-archive --role calibration --session-ids ... --out outputs/evidence/evo020/calibration.json` | Archive an exact privacy-sanitized cohort with a content hash outside rotating latest-run output. |
| `python -m tessera trajectory-evo020 --calibration ... --confirmation ... --natural-shadow ...` | Run finite-sample calibration, controlled confirmation, and read-only natural workflow shadow evaluation. |
| `python -m tessera trajectory-evo021 --calibration outputs/evidence/evo021/natural_split_calibration.json --confirmation outputs/evidence/evo021/natural_session_confirmation.json` | Reproduce split-conformal session-level clean shadow evaluation for the natural validation workflow. |
| `python -m tessera trajectory-evo022 --base-cohort outputs/evidence/evo021/natural_session_confirmation.json --calibration outputs/evidence/evo021/frozen_session_calibration.json --preregistration docs/research/EVO022_PERTURBATION_PREREGISTRATION.json` | Run the preregistered offline delay-response ladder without interpreting injected delays as natural failures. |
| `python -m tessera trajectory-evo023 --cohort outputs/evidence/evo021/natural_split_calibration.json --preregistration docs/research/EVO023_MODE_AUDIT_PREREGISTRATION.json` | Audit whether privacy-safe slow-tail signatures recur strongly enough to justify separate operational modes. |
| `python -m tessera.rhp summary --root .` | Print the canonical current-version summary: changes, findings, bounds, and next move. |
| `python -m tessera.operator_geometry validate` | Low-level operator geometry validator. |
| `.\scripts\tessera-agent.ps1` | Universal PowerShell Agent CLI entrypoint. |
| `./scripts/tessera-agent.sh` | Universal Bash Agent CLI entrypoint. |
| `.\scripts\run-tessera-full-loop.ps1` | PowerShell All-One launcher mirror. |
| `./scripts/run-tessera-full-loop.sh` | Bash All-One launcher mirror. |

## Registry Law

```text
No command without registry.
No loop without PowerShell and Bash mirrors.
No launch without Observer-first interface.
No feature without Loopbook/lessons/chart alignment.
No operator-facing script bypasses the Agent CLI.
```

<!-- AGENT_CLI_MIRROR_COMMANDS_START -->
## Agent CLI Mirror Commands

```powershell
.\scripts\agent-mirror.ps1
.\scripts\agent-mirror.ps1 -Command validate -NoPush
python agent_cli_mirror/agent_mirror.py launch --command full
python agent_cli_mirror/agent_mirror.py commands
python agent_cli_mirror/agent_mirror.py learn --failure "..." --diagnosis "..." --repair "..." --gate "..."
```

Bash:

```bash
./scripts/agent-mirror.sh
./scripts/agent-mirror.sh --command=validate --no-push
```

All operator-facing loops should route through Agent CLI Mirror.
<!-- AGENT_CLI_MIRROR_COMMANDS_END -->
