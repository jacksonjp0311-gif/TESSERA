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
  "updated_at_utc": "2026-06-21T11:09:03.089713+00:00",
  "git_head": "21124a9",
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
    "README.md": "2095fdce548ad40066b6724ac8fe92449c3c8fd11ca20f61462eb194c2c604f9",
    "README_90_SECONDS.md": "893e524e264fad2733dd18dfdd1e2165bb9cfc40e6edca29b1c39fd726a9cb9c",
    "AGENTS.md": "165a8cd3a90dfb738aafe85bdbea88890fd6a9284a2e03b7741027de35f334ef",
    "docs/loop/TESSERA_LOOPBOOK.md": "6ee268728600ac26ab867d3f126b13fb650f2390861b953e5508571a283718da",
    "docs/loop/TESSERA_FAILURE_LESSONS.md": "a269066ea7f380cc6981f9cde8fca1ebbd6112bf53f2a201df786d6e111d20ec",
    "docs/loop/TESSERA_OPERATOR_LOOP_CHART.md": "b2307dc67281c158ec0fa0eecd4900cc19229c8a79ced3036bc90e2144088e65",
    "scripts/run-tessera-full-loop.ps1": "99a61210dec85e0d20a4e05791c685518200d46c7451324f60ffe7674499f157",
    "scripts/run-tessera-full-loop.sh": "7c345b156c998ceb0bf8e7ed1adab78c0ea00731c59fac76900d918d4ec87ed5",
    "scripts/agent-mirror.ps1": "c247add82707f37d8663ddec5536c73ac156afe09b3a67c620f72d5b8940d434",
    "scripts/agent-mirror.sh": "de9606e85045c4529f82e58cbf28a9ebffbc83b4a6db9a5bde5f8c57920c1aaf",
    "scripts/loopbook/sync_loopbook.py": "781d9c431ddf231884e788a7e4c08cdcbb4bdfc9134bea5d8bfb4038672c5fd3",
    "scripts/validation/validate_loopbook_gate.py": "d5c7a21df4e4dbbcd857c360c846542b19a7d84ad49d02ccc171894e85b9e8b9",
    "agent_cli_mirror/agent_mirror.py": "6e329d37e6f67ed5bf1b12b439e65eb510aee299257a4f6148a0374715120ae8",
    "agent_cli_mirror/config/commands.json": "de1fbee1a8abe2016781331b022e1c6fac85500726ebf440ae908132aa0c0eb4",
    "docs/context/rhp/latest-rhp.json": "2ae304becd9ad563f081dced27391db90236db1708e60638ea08f89716eb69ed",
    "docs/context/nexus/surface_registry.json": "357a596d1fce0aa8022d60297e9c27b54f8370b41adb4171a725a477195bb451",
    "docs/geometry/repository_geometry.json": "f433be0bff97710aac4ff40b5a75a2ca2cbd6c9ba6241365831715806b7abbfc",
    "docs/lessons/lesson_chart.json": "eadbb8c52a858afcb2192b4d51e60c0f217d40cf0a623b30a5ba366804085185",
    "docs/roadmap/tessera_evolutionary_roadmap.json": "3c850c078de9f7a0891ffc54e363ce3713e50d583934f3b9118138c9fe1c5e20",
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
    "src/tessera/plugin/contracts.py": "707327b8c91b271f990264a87031b6c3974e651e4a44e6d6ab2bf77c80776459",
    "src/tessera/plugin/runtime.py": "6d803a5646418db2600e8c5f7eb9efbf2ac92d323442466d82018c4f4eeb683d",
    "docs/research/NAB_ENHANCED_NETWORK_DIAGNOSTIC_2026-06-19.md": "b6e54b91b5e861cb1c6647e0076229bfaa3d12889f8255991fc41b1512be0711",
    "src/tessera/experiments/trajectory_benchmark.py": "c7661ce3de92bcde83df561a2c68a80acda9889b58d2d8b8bfe3bd85eee65c43",
    "docs/research/OFFLINE_TRAJECTORY_UTILITY_2026-06-19.md": "b886e0c04b614c9c2837e97d648e435d263cd41592cd2ee93b4915b39127550d",
    "docs/research/PRECURSOR_TRAJECTORY_UTILITY_2026-06-19.md": "9d181e6f3a207e095be3248e4d6a0e0ff30fc8aeb66d0fb932b7d06dcec1c7ba",
    "src/tessera/plugin/privacy_capture.py": "f42fe77320f4962f98ead3ad6994f51e6faeeb04e07b31a299d663ad4e306c5a",
    "docs/research/LOCAL_TRAJECTORY_PRIVACY_DIAGNOSTIC_2026-06-19.md": "b390a6a53a55b8203d927b70c42a0280178dd362991e150854b6476cacb039a7",
    "docs/research/LOCAL_TRAJECTORY_IDENTIFIABILITY_2026-06-19.md": "37791be706b2989a0eef63f82a00f72bbf1f3796a0a1c58fd03ce4a0c9818bea",
    "docs/research/PHASE_CONDITIONED_TELEMETRY_SPECIALIST_2026-06-19.md": "d3f66a4a5924fbb36401b924ceaec916b9687145825b2ef56ee22dcebd3efde3",
    "docs/research/FINITE_SAMPLE_WORKFLOW_SHADOW_2026-06-19.md": "daa9a8fb8d3895a360338c5619b0cea3a349cd08397a40913ddb0a4900bd5c1a",
    "docs/research/NATURAL_CLEAN_SESSION_CALIBRATION_2026-06-20.md": "8691dd5b1f5b1521dbeeaf21e9b0ad3920a83f17dde648242c95530e2e50cdff",
    "docs/research/NATURAL_PROFILE_PERTURBATION_RESPONSE_2026-06-20.md": "fdbd4b6d786d8b15f1b5aa049e36c5082f13463fd5d8a0bf952f38310ac63daf",
    "docs/research/EVO022_PERTURBATION_PREREGISTRATION.json": "77770c17bb80387e54b7413c2dbac37188fff25cd8f17900b0586abfb4236bed",
    "docs/research/NATURAL_TAIL_MODE_AUDIT_2026-06-20.md": "cddfc53beb4c89714fc10d759ab7bd1efc1cd69b5ee45d6fa57b0075199385e4",
    "docs/research/EVO023_MODE_AUDIT_PREREGISTRATION.json": "bc7d8914a437fb517287544f87eb286294c4e9555750796d4429ec1f7d71fc49",
    "docs/research/AGGREGATE_CONTEXT_ATTRIBUTION_2026-06-20.md": "ad5cfdbadd74ba787cb64a1827fb763fb855947f714f73f47ef16d778aad07bc",
    "docs/research/EVO024_CONTEXT_ATTRIBUTION_PREREGISTRATION.json": "23aea5c5c9de78b0951e0f15d24be14f8339b8c7f0b839ab3480386b126f3ae2",
    "docs/research/SUBPROCESS_IO_MECHANISM_ATTRIBUTION_2026-06-20.md": "6049ca3f9502b8168425873b533fd602a93a3ae64cef0e8ff1ce55ea6acee57e",
    "docs/research/EVO025_MECHANISM_ATTRIBUTION_PREREGISTRATION.json": "73eb544c5afe6d3f73289136d69fb85157f1459c9da1fa68053321a40d2c316c",
    "docs/research/PLUGIN_RUNTIME_CONTAINMENT_2026-06-20.md": "0d4450f7f4374fe2974fddc09c83028f4d58969e083e2dd2a87a19219dce496f",
    "src/tessera/plugin/supervisor.py": "7f1a96088a58f0cd0079baacf5d768da34cff0d5a9835aef84fd089889be4926",
    "src/tessera/experiments/plugin_readiness.py": "c640f1c294cd6814bb51e5b9902a4a8933a71ed5a8a80a32d0f46c232f4e4781",
    "docs/research/PLUGIN_LATENCY_SEPARATION_2026-06-20.md": "9f532a723e11a2e19708052abe70e01e596d61986c03c7e6abba95dcbe382ff6",
    "docs/research/SHADOW_CHECKPOINT_ADMISSION_2026-06-20.md": "5d7e891d9c4821b48347c47264dd25af5183b03011b80ddcc0ecc7caee3f17a7",
    "src/tessera/plugin/checkpoints.py": "0995468de3659fd929b33fe283ce18987c5ac33b3093835eee291114fa41b34c",
    "src/tessera/plugin/shadow_training.py": "f49d3f021f3c19fac804dbb20cf869554258e1373142c0c9e10a5d46b644ac38",
    "src/tessera/experiments/checkpoint_readiness.py": "b7fec69b935af4ef3624349f62f6718700a0efcd983f46afcf3ac7165e825900",
    "docs/research/NEURAL_CHECKPOINT_RUNTIME_2026-06-20.md": "0a1b1c4f73f37ea16b06437ba309dda8de680202bf90e85e7fcdebda8ab2641b",
    "src/tessera/plugin/neural_checkpoints.py": "6c1519ab5fd877e8718449e6f22cafe9964c0b9f3af7dc7572eb5c9710e81be1",
    "src/tessera/experiments/neural_checkpoint_readiness.py": "d97f387972bdd3be06c05b928f72d25638ad0e7781292faa2b530389ce756159",
    "docs/research/EVO030_NATURAL_CHECKPOINT_UTILITY_PREREGISTRATION.json": "48ee1b4202f33c05595d2684a31f93ad1b07db9d9eb38826e4e3114e9a7e0a0d",
    "docs/research/NATURAL_CHECKPOINT_UTILITY_2026-06-21.md": "67ed9a68d2982f5cc41f268ac338347f3040c4326c25027f5e552f91e89e158d",
    "src/tessera/experiments/natural_checkpoint_utility.py": "9fb95469e3190ad6a621b0a3a6bd9030b5a262b5b7e8a6bbf9c4fb099c372592",
    "docs/research/EVO031_BOUNDED_NEURAL_RESIDUAL_PREREGISTRATION.json": "6b228f6c8f5387fee69b4dbbf063c9f84bea9e46941c4dedbca9afd4e0e88272",
    "docs/research/BOUNDED_NEURAL_RESIDUAL_2026-06-21.md": "1de1924298d2c3af38df8671b2fe58d73767a899126d55a09584a1a51f52b075",
    "src/tessera/experiments/bounded_neural_residual.py": "d25f909a2f392d77782eea83e78d6631336985a68160f2efd49eb397c1818382",
    "docs/research/EVO032_NEURAL_UNCERTAINTY_ROUTER_PREREGISTRATION.json": "001357c8ecfd4ee599dc04cb79b367ac6eb08d6422ec88a1ec5c0104314b2704",
    "docs/research/NEURAL_UNCERTAINTY_ROUTING_2026-06-21.md": "3d262a890f80671a7a3413c1dc00565c5d8bdd66872305bec973b175e7068c37",
    "src/tessera/experiments/neural_uncertainty_router.py": "5ed797817810871a4800d6180834da398c4adcbb6b503a85a5eb94d241031eaf",
    "docs/research/RUNTIME_UNCERTAINTY_INTEGRATION_2026-06-21.md": "c42b44c827ff5db86c8bddfc97cd21f7785043aeb87cf1efd76b819693ba2f40",
    "src/tessera/experiments/runtime_uncertainty_readiness.py": "2f08688008a2ec1e8b12b0191ab7ed8d8bdedfd6667b042bcf21455706e201d0",
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
    "outputs/evidence/evo022/perturbation_response.json": "dccaefee58c37eb588c40420cd2057142b2ef541ed723113e5370f1c77c14cce",
    "outputs/evidence/evo023/mode_audit.json": "37a101a42e9174cc8333c080d3500d455b84e07e2e6a78e770667c4da8de15c9",
    "outputs/evidence/evo024/fresh_context_cohort.json": "112805c97e4527e2633b6a2c4ac816ef8589305191b6138ea09b6b66a7790ec2",
    "outputs/evidence/evo024/context_attribution.json": "105f247f7b699263fd0027354b015f7e9a8f6bd3a3662a86be0228f11f87db08",
    "outputs/evidence/evo025/fresh_mechanism_cohort.json": "de7c2a96e0769a8aa85ff8db72687c59c4a007422e1ab1b1110be9ff5240ae38",
    "outputs/evidence/evo025/mechanism_attribution.json": "b6e71b1958d7f1e921a285341c1367cbbe56f4332b36f6a1c8f68508a716aa8e",
    "outputs/evidence/evo026/plugin_readiness.json": "c02e0a3a9fdae287358702cd14ae593c29fcab84d9def942d615fc86e45ec638",
    "outputs/evidence/evo027/plugin_latency_separation.json": "60489b9ace4837f266f235f5fd8f5b8e7ea52b59f2acb64b9502b7b72c5791d9",
    "outputs/evidence/evo028/checkpoint_readiness.json": "6b6648f34461e3aef9c5bb46be959722f0655a92771603dbe006b1abac4c89ab",
    "outputs/evidence/evo029/neural_checkpoint_readiness.json": "b29f62bfc70f87ac0cc718713af678c40a2609bfa3743abec75dc70e74d78077",
    "outputs/evidence/evo030/natural_checkpoint_utility.json": "83f4434b8db6cf62f3aa28e95c8f4dd506149b19428d56fb32a66fb130999d8c",
    "outputs/evidence/evo031/bounded_neural_residual.json": "824c8228dcebcf237a8127c13c98c242d9214056334a9f8824da980dd4ce7a28",
    "outputs/evidence/evo032/neural_uncertainty_router.json": "0c60958011c2501c3108b29e010a009e5147bcc745a78ce2914a5f5b89ea4e7d",
    "outputs/evidence/evo033/runtime_uncertainty_readiness.json": "4998972abbe0becdaef8513b7bfbc409039c79c045a9de9c1f6ebfaf48da727a",
    "src/tessera/rhp/core.py": "5a5de2c6dd4424700d73ef4117e387c37e400c824ba0edc12e79d3123b15462c",
    "scripts/validation/validate_rhp_nexus.py": "e03fd4c3f2e2d681cbe06d39d99e48dffb78245f06e006e2157a1fdfb9ed92de"
  },
  "claim_boundary": "Loopbook sync records operator surfaces only; it does not prove real telemetry transfer."
}
```
