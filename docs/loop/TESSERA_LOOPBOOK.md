# TESSERA Loopbook

## Purpose

The Loopbook is the canonical operator run record for Tessera. Every feature that changes the runtime loop, scripts, validation path, README run surface, or operator interface must update this file and `docs/loop/loopbook_manifest.json`.

```text
rehydrate -> agent-cli-mirror -> loopbook -> launch -> observe -> worker -> check -> run -> validate -> ledger -> push -> root
```

## Canonical Command

```powershell
cd "C:\Users\jacks\OneDrive\Desktop\Tessera"
.\scripts\run-tessera-full-loop.ps1
```

Dry run without push:

```powershell
.\scripts\run-tessera-full-loop.ps1 -NoPush
```

## What Opens Every Time

```text
Observer PowerShell = read-only human interface
Worker PowerShell   = registered Agent CLI Mirror command runner
```

## Loop Steps

1. `rehydrate`
2. `agent-cli-mirror`
3. `loopbook`
4. `launch`
5. `observe`
6. `worker`
7. `check`
8. `run`
9. `validate`
10. `ledger`
11. `push`
12. `root`

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
{
  "schema": "TESSERA-loopbook-manifest-v0.2.8",
  "updated_at_utc": "2026-06-20T11:58:18.792675+00:00",
  "git_head": "23ffd62",
  "loop_steps": [
    "rehydrate",
    "agent-cli-mirror",
    "loopbook",
    "launch",
    "observe",
    "worker",
    "check",
    "run",
    "validate",
    "ledger",
    "push",
    "root"
  ],
  "canonical_loopbook": "docs/loop/TESSERA_LOOPBOOK.md",
  "canonical_command": ".\\scripts\\run-tessera-full-loop.ps1",
  "agent_cli_mirror": "agent_cli_mirror/agent_mirror.py",
  "observer": "agent_cli_mirror/agent_mirror.py observe",
  "worker": "agent_cli_mirror/agent_mirror.py worker",
  "launcher": "scripts/agent-mirror.ps1",
  "gate": "scripts/validation/validate_loopbook_gate.py",
  "feature_hashes": {
    "README.md": "33936295ed64c13de872997cdb933072906977ed5c0d8399d486d6a4785b2374",
    "README_90_SECONDS.md": "893e524e264fad2733dd18dfdd1e2165bb9cfc40e6edca29b1c39fd726a9cb9c",
    "AGENTS.md": "165a8cd3a90dfb738aafe85bdbea88890fd6a9284a2e03b7741027de35f334ef",
    "docs/loop/TESSERA_LOOPBOOK.md": "02d6e50a8cc60b888af6c8d84dec89d9ab8a8ba51055cbb221533937d82ef2d0",
    "docs/loop/TESSERA_FAILURE_LESSONS.md": "87a784c6bad8bc856a278be4acdfae000261c6b9b93e7d119528ef2775456ad5",
    "docs/loop/TESSERA_OPERATOR_LOOP_CHART.md": "b2307dc67281c158ec0fa0eecd4900cc19229c8a79ced3036bc90e2144088e65",
    "scripts/run-tessera-full-loop.ps1": "99a61210dec85e0d20a4e05791c685518200d46c7451324f60ffe7674499f157",
    "scripts/run-tessera-full-loop.sh": "7c345b156c998ceb0bf8e7ed1adab78c0ea00731c59fac76900d918d4ec87ed5",
    "scripts/agent-mirror.ps1": "c247add82707f37d8663ddec5536c73ac156afe09b3a67c620f72d5b8940d434",
    "scripts/agent-mirror.sh": "de9606e85045c4529f82e58cbf28a9ebffbc83b4a6db9a5bde5f8c57920c1aaf",
    "scripts/loopbook/sync_loopbook.py": "03a4021000a6164016344445c1505d2b75bde6686cd613b454e66f126f54974a",
    "scripts/validation/validate_loopbook_gate.py": "d5c7a21df4e4dbbcd857c360c846542b19a7d84ad49d02ccc171894e85b9e8b9",
    "agent_cli_mirror/agent_mirror.py": "cdde0a0354b08f44338243bf0c272ddc81fce7b072adef272d50e60dc11ba1af",
    "agent_cli_mirror/config/commands.json": "9fd54f11dc5f5ad32b35fcba8dbb658f1733968a7d6ddc12a7708a0e43a90c29",
    "docs/context/rhp/latest-rhp.json": "4a0f3a0dfb8328bfaa38e04b05827b7d342aede25322d3aa4d8cd91732412740",
    "docs/context/nexus/surface_registry.json": "357a596d1fce0aa8022d60297e9c27b54f8370b41adb4171a725a477195bb451",
    "docs/geometry/repository_geometry.json": "f433be0bff97710aac4ff40b5a75a2ca2cbd6c9ba6241365831715806b7abbfc",
    "docs/lessons/lesson_chart.json": "8ee12c93074c3257c71410cc19569b4cf7332835161edef62ccab049ae9d8cba",
    "docs/roadmap/tessera_evolutionary_roadmap.json": "c3116610aec8c6bf5768a9b2f1be86cbc50e2c006be4dd2e48d841a75a005f99",
    "docs/research/CROSS_DOMAIN_EVOLUTION_2026-06-19.md": "1b7e04cf290452ab391cbbd68eef0ebcb1684357bbee54c11e91250026eb489b",
    "docs/research/MULTISCALE_AWARENESS_EVOLUTION_2026-06-19.md": "3f2f5657959610080aaaf9ce9294543b2fba7e42e77cf7f3947178502893b1ed",
    "docs/research/NAB_T1_TRANSFER_2026-06-19.md": "a80a538a24cf33e5b837d6d6a31052116d3944b3f23a309127cc27cdfb19c099",
    "datasets/nab/source_manifest.json": "30e206b446c7d541d6d7f6f639bd5474f774434daaf8841e0acddf839bda49fd",
    "src/tessera/experiments/run_nab_transfer.py": "a0bce4fb2819593405692b055c2532ae260e017a0eb54928d705044944c9c469",
    "datasets/telemanom/source_manifest.json": "e02089a2009701392e84d88157dc0774449e8893d9561e5e7a9a0d25c49b99b0",
    "src/tessera/experiments/run_smap_transfer.py": "da318dd027889d13c16495cb65642e1b2dd4571b5b0669609761c5be14e29258",
    "docs/research/NASA_SMAP_DIAGNOSTIC_2026-06-19.md": "73075cf7f8065d7525b7ad77971119ceba627a6c633991cb4e9d9cdb67b295bb",
    "datasets/ucr/source_manifest.json": "9c41f96324d72b999a66b104f880add08b7d67e79e337cad816513869abbdf2f",
    "src/tessera/experiments/run_ucr_transfer.py": "e20c85754667fdeb5c436d146a8c20be59c52d87c8d2292db6bab8a4dd3f5dad",
    "src/tessera/metrics/subsequence.py": "a14f462025aa8b6dfe42ed797d27a8e98c4fa2ccd630e723f75e0e0d3d02cadf",
    "docs/research/UCR_SUBSEQUENCE_EVOLUTION_2026-06-19.md": "46226d73d011ae5978b5864df8d2f509446a1393e4b77d61ca727f3d66abf27c",
    "src/tessera/memory/episodes.py": "f98483e5986c68fce5a89645ad041ed6de3a96346eda2dbb49854003bd10d9c2",
    "docs/research/UCR_EPISODE_GOVERNANCE_2026-06-19.md": "f0bce4776a533914246866463e6bfdee337df143b5a38a0c99bcd011ea9edae7",
    "src/tessera/metrics/router.py": "a77bc3c52d7e4956ce095a6b28301c9cbd0ab853bdedd2247afdecf97c6cb5c0",
    "docs/research/UCR_SENSOR_ROUTER_2026-06-19.md": "b2d264f90f6d77fb83f7bfd13615cf2a41ffd30bced39b8f6758e70a1e777bec",
    "src/tessera/memory/gates.py": "b32780ed269f120b1753807c0764372f6111157778050d451b6e4c2eb729a125",
    "docs/research/UCR_ABSTENTION_MEMORY_NORMALITY_2026-06-19.md": "e9242a3d60830cfcd3d0ca4ecd98511d33b4e4dcb38f9878178ba172b0599f38",
    "src/tessera/baselines/pca_codec.py": "0bccdb8d3ac34f88b0f08f92d78d638694515b22c5e4a4fcf1c489aaeda5fc6b",
    "src/tessera/baselines/random_projection.py": "864c554b003c34184e1fab5c84d66a69723be74bc2ff7fa04f3e7e60630ae914",
    "src/tessera/baselines/matrix_profile.py": "95d5ea9fc48f42e4f6cbad41023dee5b61f7c4a9b030a9543014493abce3d8da",
    "docs/research/UCR_SELECTIVE_FUSION_2026-06-19.md": "b5a6549fa9275d64cd93af995f3667a13567abf6ee82f6d11457456230925166",
    "src/tessera/model/prediction_experts.py": "d7b59ea795b47861b1e13b45e1442602e8e9c15d121a90385f6e7f7e4b5a9992",
    "docs/research/UCR_PREDICTION_EXPERT_TRANSFER_2026-06-19.md": "8b5552e9c9994bf2357b0e7d7e0353251bd556fc63b4995f14590a925ed91cce",
    "src/tessera/plugin/contracts.py": "eff9a6c19cdc275670bc8c10fc295d29ace310d8f7f23f154b7ab00c97e07878",
    "src/tessera/plugin/runtime.py": "88fdb063e4652ee6c574ce3fad5488e8b545a590077671393f5b48cdeb35c577",
    "docs/research/NAB_ENHANCED_NETWORK_DIAGNOSTIC_2026-06-19.md": "b6e54b91b5e861cb1c6647e0076229bfaa3d12889f8255991fc41b1512be0711",
    "src/tessera/experiments/trajectory_benchmark.py": "581934e8d34efda0d4ff695b1b97ca44d6814515515ed68f3bb63c04a04bc3fd",
    "docs/research/OFFLINE_TRAJECTORY_UTILITY_2026-06-19.md": "b886e0c04b614c9c2837e97d648e435d263cd41592cd2ee93b4915b39127550d",
    "docs/research/PRECURSOR_TRAJECTORY_UTILITY_2026-06-19.md": "9d181e6f3a207e095be3248e4d6a0e0ff30fc8aeb66d0fb932b7d06dcec1c7ba",
    "src/tessera/plugin/privacy_capture.py": "7192a3896764b56f41f0d0777b8c70658b2db283332a70ca446591f293f58756",
    "docs/research/LOCAL_TRAJECTORY_PRIVACY_DIAGNOSTIC_2026-06-19.md": "b390a6a53a55b8203d927b70c42a0280178dd362991e150854b6476cacb039a7",
    "docs/research/LOCAL_TRAJECTORY_IDENTIFIABILITY_2026-06-19.md": "37791be706b2989a0eef63f82a00f72bbf1f3796a0a1c58fd03ce4a0c9818bea",
    "docs/research/PHASE_CONDITIONED_TELEMETRY_SPECIALIST_2026-06-19.md": "d3f66a4a5924fbb36401b924ceaec916b9687145825b2ef56ee22dcebd3efde3",
    "docs/research/FINITE_SAMPLE_WORKFLOW_SHADOW_2026-06-19.md": "daa9a8fb8d3895a360338c5619b0cea3a349cd08397a40913ddb0a4900bd5c1a",
    "docs/research/NATURAL_CLEAN_SESSION_CALIBRATION_2026-06-20.md": "8691dd5b1f5b1521dbeeaf21e9b0ad3920a83f17dde648242c95530e2e50cdff",
    "scripts/telemetry/probe.py": "947dc1439ebf8407acbcad170bae81adb48272ea119f3b8959970fb08bb1ec22",
    "outputs/evidence/evo020/clean_calibration.json": "819f6b26d2c23ed81ceab03ce3b983a28bea83c2e1cc46e92d14eb6695909439",
    "outputs/evidence/evo020/controlled_confirmation.json": "a47126fe2ddae6ff90b430ed14b59f5a040b1da9c4a73da9514fd9125a3dd654",
    "outputs/evidence/evo020/natural_shadow.json": "beb56c759d478e8cc3ccf396c4d5265b83e60fc55ea6bdbf8498da5ed264783d",
    "outputs/evidence/evo020/frozen_calibration.json": "75f92e1286dcd9f827b111b01575d9f791a32a7a3281675b83a0dea019b7e024",
    "outputs/evidence/evo020/evo020_shadow_report.json": "b98f112fb61892c3cd8a3dfc905f10627d1d2cf15af0bd455f369e81c0e455fe",
    "outputs/evidence/evo021/natural_clean_confirmation.json": "b18042c3a6e1dd208f0f18977a1366b53b07b926167ff9b20ecb76e1803362b8",
    "outputs/evidence/evo021/natural_clean_shadow_report.json": "5ecb58e04737dea7e14480d4b95ef5378e5b0256ec00b6ec610e7a71fe8d326d",
    "outputs/evidence/evo021/natural_split_calibration.json": "f94e5ed3301420aafc3c6f314380f7910ac8b9a6e31d168a3881ccc687ee79cf",
    "outputs/evidence/evo021/frozen_session_calibration.json": "2a343b00e5576ac10b715075dc9fa61a3a65d9e09ad315dffd4d369411b2fea1",
    "outputs/evidence/evo021/natural_session_confirmation.json": "a55ec4a723c52d5238016936c1e6e1a81ae7eddd7466735272d7e0a51308d171",
    "outputs/evidence/evo021/natural_session_shadow_report.json": "50367dee60b99a100d6a7429fbb985ecbe3e8533dfa8953cc6fba46610f51021",
    "src/tessera/rhp/core.py": "5a5de2c6dd4424700d73ef4117e387c37e400c824ba0edc12e79d3123b15462c",
    "scripts/validation/validate_rhp_nexus.py": "e03fd4c3f2e2d681cbe06d39d99e48dffb78245f06e006e2157a1fdfb9ed92de"
  },
  "claim_boundary": "Loopbook sync records operator surfaces only; it does not prove real telemetry transfer."
}
```
