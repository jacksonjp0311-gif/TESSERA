# Tessera Engine v0.1 — Alignment and RCC Nexus Patch

## Patch status

Applied locally in the sandbox repository copy. No GitHub push has been performed.

Target local user path after extraction:

```text
C:\Users\jacks\OneDrive\Desktop\Tessera
```

## What changed

- Preserved runnable Tessera Engine v0.1.
- Injected RCC-N v1.7 repository navigation as a Nexus layer.
- Rebuilt the root README into Human / RCC Nexus / AI Agent trisection.
- Added/expanded `AGENTS.md` and `README_90_SECONDS.md` as required orientation surfaces.
- Added `rcc/` and `rcc/nexus/` route surfaces:
  - `rcc/nexus/route_map.json`
  - `rcc/nexus/task_routing_matrix.md`
  - `rcc/nexus/agent_handoff_contract.md`
- Added `docs/context/` indexes:
  - `docs/context/repository_context_index.json`
  - `docs/context/rcc_nexus_index.json`
- Added `docs/alignment/` surfaces:
  - `origin_manifest.json`
  - `non_claim_locks.md`
  - `tessera_alignment_and_rcc_nexus_integration.md`
- Imported attached theory/reference documents into `docs/theory/imports/`.
- Added TESSERA lineage documents under `docs/theory/tessera_lineage/`.
- Added folder-level mini READMEs with RCC Nexus Echo Location blocks for runtime, scripts, reports, configs, theory imports, and core module folders.
- Added RCC and architecture validation scripts:
  - `scripts/rcc/check_rcc_nexus.py`
  - `scripts/validation/validate_architecture_contracts.py`
- Updated route/context indexes after mini README expansion.

## Imported theory/reference surface

- RP-SA v0.1 Rehydration Protocol Software Architecture
- LFTE-SA v0.1 Lattice Field Theory Software Architecture format reference
- RCC-N v1.7 RCC Nexus standard reference
- OMN runtime README/RCC pattern reference
- ASF-R evidence-gated continuation runtime reference
- TESSERA v1.3-v1.7 lineage documents

## Validation performed

```bash
python scripts/rcc/check_rcc_nexus.py
python scripts/validation/validate_architecture_contracts.py
python -m unittest discover -s tests
PYTHONPATH=src python -m tessera run --out outputs --steps 160 --epochs 2 --topology q4 --field-dim 16 --code-dim 8
PYTHONPATH=src python -m tessera validate --run outputs/runs/latest
```

Latest smoke run:

```text
outputs/runs/tessera_run_20260617_020243
claim_ceiling: diagnostic_baseline_limited
false_memory_rate: 0.0
```

## Push boundary

No GitHub push has been performed. Push remains blocked until James explicitly authorizes it.

## Claim boundary

This patch improves repository orientation, alignment, evidence surfaces, RCC-N navigation, and validation readiness. It does not prove real telemetry transfer, production readiness, code correctness, patch safety, safety, AGI, consciousness, or universal model capability.
