# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                                                                              ║
# ║   TESSERA ENGINE v0.1 — ALIGNMENT + RCC NEXUS ALL-ONE PATCH                  ║
# ║   ────────────────────────────────────────────────────────────────────────   ║
# ║   ORIGIN ALIGNMENT, RCC-N REPOSITORY NAVIGATION, THEORY IMPORT SURFACES,     ║
# ║   MINI README COVERAGE, VALIDATION REPORTS, LOCAL SMOKE RUN, AND             ║
# ║   PUSH-BLOCKED RELEASE PREP FOR C:\Users\jacks\OneDrive\Desktop\Tessera     ║
# ║                                                                              ║
# ║   VERSION                                                                    ║
# ║   ───────                                                                    ║
# ║   v0.1.1 — Local Alignment / RCC Nexus Integration Patch · RootMirror Guarded              ║
# ║                                                                              ║
# ║   AUTHOR                                                                     ║
# ║   ──────                                                                     ║
# ║   James Paul Jackson                                                         ║
# ║                                                                              ║
# ║   CANONICAL LOCK                                                             ║
# ║   ─────────────                                                              ║
# ║   • Rehydrate before reasoning.                                              ║
# ║   • Orient before action.                                                    ║
# ║   • Validate before mutation.                                                ║
# ║   • Navigation is not validation.                                            ║
# ║   • Documentation is not correctness.                                        ║
# ║   • Synthetic success is not transfer.                                       ║
# ║   • Push remains blocked until James explicitly authorizes it.               ║
# ║                                                                              ║
# ║   WHAT THIS SCRIPT DOES                                                      ║
# ║   ─────────────────────                                                      ║
# ║   Anchors the local Tessera repo; creates RCC/Nexus surfaces; creates        ║
# ║   alignment/origin surfaces; imports theory files from inbox folders;        ║
# ║   writes mini READMEs; writes route maps and context indexes; writes         ║
# ║   validators; runs RCC checks, architecture checks, tests, and a local       ║
# ║   smoke run; emits a local patch report; returns to root.                    ║
# ║                                                                              ║
# ║   PUSH / CLAIM BLOCKS                                                       ║
# ║   ─────────────────────────                                                  ║
# ║   It does not push to GitHub. It does not claim production readiness.         ║
# ║   It does not claim code correctness, empirical validation, AGI, safety,      ║
# ║   truth, or universal transfer.                                              ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

param(
    [string]$Root = "",
    [switch]$SkipInstall,
    [switch]$SkipRun,
    [switch]$SkipTests,
    [switch]$SkipPackage
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$script:TesseraRoot = $null

trap {
    if ($script:TesseraRoot -and (Test-Path $script:TesseraRoot)) {
        Set-Location $script:TesseraRoot
        Write-Host "🜄  RootMirror return after error: $script:TesseraRoot"
    }
    Write-Host "🔴  All-One patch stopped before completion."
    break
}

function Say {
    param([string]$Message, [string]$Glyph = "🜁")
    Write-Host "$Glyph  $Message"
}

function Ensure-Dir {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        [void](New-Item -ItemType Directory -Force -Path $Path)
    }
}

function Write-Utf8 {
    param([string]$Path, [string]$Content)
    $Parent = Split-Path -Parent $Path
    Ensure-Dir $Parent
    [System.IO.File]::WriteAllText($Path, $Content, [System.Text.UTF8Encoding]::new($false))
}

function Write-JsonFile {
    param([string]$Path, [object]$Object)
    $Json = $Object | ConvertTo-Json -Depth 30
    Write-Utf8 $Path $Json
}

function Run-Safe {
    param([string]$Exe, [string[]]$ArgList, [int]$TimeoutSeconds = 240)
    Say "$Exe $($ArgList -join ' ')" "🜂"
    & $Exe @ArgList
    $Code = $LASTEXITCODE
    if ($null -eq $Code) {
        $Code = 0
    }
    if ($Code -ne 0) {
        throw "Command failed with exit code $Code`: $Exe $($ArgList -join ' ')"
    }
}

function Normalize-FileName {
    param([string]$Name)
    $Safe = $Name.ToLowerInvariant()
    $Safe = $Safe -replace '[^a-z0-9\.\-_]+','_'
    $Safe = $Safe.Trim('_')
    if ($Safe.Length -eq 0) { $Safe = "imported_theory" }
    return $Safe
}

# ─────────────────────────────────────────────────────────────────────────────
# Step 1 — Root Anchor
# ─────────────────────────────────────────────────────────────────────────────

if ($Root -eq "") {
    if ($PSScriptRoot -and $PSScriptRoot.Trim().Length -gt 0) {
        $CandidateRoot = Split-Path -Parent $PSScriptRoot
        if (Test-Path (Join-Path $CandidateRoot "pyproject.toml")) {
            $Root = (Resolve-Path $CandidateRoot).Path
        }
    }
}

if ($Root -eq "") {
    $DesktopRoot = "C:\Users\jacks\OneDrive\Desktop\Tessera"
    if (Test-Path $DesktopRoot) {
        $Root = (Resolve-Path $DesktopRoot).Path
    }
}

if ($Root -eq "") {
    $Root = (Get-Location).Path
}

if (-not (Test-Path $Root)) {
    throw "Root path does not exist: $Root"
}

Set-Location $Root
$script:TesseraRoot = $Root
Say "Root anchored: $Root" "🜄"

# ─────────────────────────────────────────────────────────────────────────────
# Step 2 — Directory Grammar
# ─────────────────────────────────────────────────────────────────────────────

$Dirs = @(
    "docs",
    "docs\alignment",
    "docs\architecture",
    "docs\context",
    "docs\theory",
    "docs\theory\imports",
    "docs\theory\inbox",
    "docs\theory\tessera_lineage",
    "rcc",
    "rcc\nexus",
    "reports",
    "reports\rcc_nexus",
    "reports\validation",
    "scripts",
    "scripts\rcc",
    "scripts\validation",
    "scripts\release",
    "outputs",
    "outputs\runs",
    "outputs\evidence",
    "outputs\reports",
    "ledgers",
    "configs",
    "src",
    "tests"
)

foreach ($D in $Dirs) {
    Ensure-Dir (Join-Path $Root $D)
}

# ─────────────────────────────────────────────────────────────────────────────
# Step 3 — Theory Import
# ─────────────────────────────────────────────────────────────────────────────

$ImportLog = @()
$InboxCandidates = @(
    (Join-Path $Root "theory_inbox"),
    (Join-Path $Root "_theory_inbox"),
    (Join-Path $Root "docs\theory\inbox"),
    (Join-Path $Root "docs\theory\imports_pending")
)

foreach ($Inbox in $InboxCandidates) {
    if (Test-Path $Inbox) {
        $Files = Get-ChildItem -Path $Inbox -File -Recurse -Include *.md,*.txt,*.tex,*.json,*.csv,*.pdf -ErrorAction SilentlyContinue
        foreach ($F in $Files) {
            $SafeName = Normalize-FileName $F.Name
            $Dest = Join-Path $Root (Join-Path "docs\theory\imports" $SafeName)
            Copy-Item -Path $F.FullName -Destination $Dest -Force
            $ImportLog += [ordered]@{
                source = $F.FullName
                destination = $Dest
                imported_at = (Get-Date).ToString("s")
            }
        }
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# Step 4 — Alignment Surfaces
# ─────────────────────────────────────────────────────────────────────────────

$OriginManifest = [ordered]@{
    schema = "TESSERA-v0.1-origin-manifest"
    system = "Tessera"
    package = "tessera"
    cli = "tessera"
    root = $Root
    created_or_refreshed = (Get-Date).ToString("s")
    origin_geometry = [ordered]@{
        required_files = @(
            "README.md",
            "README_90_SECONDS.md",
            "AGENTS.md",
            "pyproject.toml",
            "docs/context/repository_context_index.json",
            "docs/context/rcc_nexus_index.json",
            "rcc/nexus/route_map.json",
            "docs/alignment/non_claim_locks.md",
            "docs/theory/import_manifest.json"
        )
        required_commands = @(
            "python scripts/rcc/check_rcc_nexus.py",
            "python scripts/validation/validate_architecture_contracts.py",
            "python -m unittest discover -s tests",
            "python -m tessera validate --run outputs/runs/latest"
        )
        claim_ceiling = "diagnostic_baseline_limited_until_real_telemetry_transfer"
    }
    non_claim_locks = @(
        "navigation_is_not_validation",
        "documentation_is_not_correctness",
        "context_reconstruction_is_not_code_quality",
        "synthetic_success_is_not_transfer",
        "replay_is_not_safety",
        "repair_is_not_truth",
        "certificate_is_not_empirical_validation",
        "validation_remains_required",
        "human_authorization_required_for_push"
    )
}
Write-JsonFile (Join-Path $Root "docs\alignment\origin_manifest.json") $OriginManifest

$NonClaimLocks = @'
# Tessera Non-Claim Locks

Tessera is a local-first reference engine for sparse compressive memory, replay validation, wound recording, baseline comparison, and transfer-certification discipline.

It does not prove:

- AGI
- consciousness
- safety
- truth
- empirical validation
- production readiness
- universal anomaly detection superiority
- biological equivalence
- physical manifold identity
- code correctness
- patch safety
- GitHub release readiness

## Locks

- navigation_is_not_validation
- documentation_is_not_correctness
- context_reconstruction_is_not_code_quality
- synthetic_success_is_not_transfer
- dataset_win_is_not_universal_claim
- replay_is_not_safety
- repair_is_not_truth
- lower_loss_is_not_memory
- certificate_is_not_empirical_validation
- baseline_guard_sets_claim_ceiling
- validation_remains_required
- human_authorization_required_for_push

## Operating Seal

Build small. Declare the graph. Compress the stream. Replay every memory. Wound every failure. Repair only in shadow. Promote only by certificate. Claim only what transfers.
'@
Write-Utf8 (Join-Path $Root "docs\alignment\non_claim_locks.md") $NonClaimLocks

$AlignmentDoc = @'
# Tessera Alignment + RCC Nexus Integration

## Purpose

This patch converts the Tessera Engine v0.1 repository into an alignment-aware, RCC-N navigable Nexus surface before any GitHub push.

## Runtime Spine

```text
origin manifest
-> repository context index
-> RCC route map
-> AGENTS operating contract
-> theory import manifest
-> validation scripts
-> smoke run
-> evidence package
-> claim ceiling
```

## Alignment Rule

No durable repository mutation is considered release-ready until origin surfaces, RCC surfaces, theory imports, validation commands, smoke-run evidence, and non-claim locks are present.

## RCC-N Rule

RCC tells the agent what the repository means. RCC-N tells the agent where it is. Validation tells the agent whether reality agreed.

## Push Lock

This patch does not push to GitHub. Push authority remains human-controlled.
'@
Write-Utf8 (Join-Path $Root "docs\alignment\tessera_alignment_and_rcc_nexus_integration.md") $AlignmentDoc

# ─────────────────────────────────────────────────────────────────────────────
# Step 5 — RCC Nexus Surfaces
# ─────────────────────────────────────────────────────────────────────────────

$RccReadme = @'
# Folder Purpose

## S - Specification

RCC root shell for Tessera Nexus routing and repository navigation.

## H - Hooks

Inbound hooks:

- README.md
- AGENTS.md
- README_90_SECONDS.md
- docs/context/repository_context_index.json
- docs/context/rcc_nexus_index.json

Outbound hooks:

- rcc/nexus
- reports/rcc_nexus

## A - Artifacts

Evidence / output surfaces:

- reports/rcc_nexus
- docs/context
- rcc/nexus/route_map.json

## T - Theory / Basis

Governed by RCC-N v1.7, Rehydration Protocol origin alignment, SFT-style non-claim locks, and Tessera v1.7 real-telemetry transfer discipline.

## I - Invariants

- Preserve Tessera source attribution.
- Preserve non-claim locks.
- Preserve evidence-bound claims.
- Navigation is not validation.
- Context is not correctness.
- Synthetic success is not transfer.
- Validation remains required.

## E - Examples

Validation examples:

```powershell
python scripts/rcc/check_rcc_nexus.py
python scripts/validation/validate_architecture_contracts.py
python -m unittest discover -s tests
```

## RCC Nexus Echo Location

Sphere Position:

- Shell: center
- Meridian(s): agent, drift, documentation, safety, telemetry, memory
- Sector: rcc
- Version / TTL: RCC-N-v1.7 / 180 days
- Last Verified: generated by All-One patch

Local Role:

- RCC root shell for Nexus routing and navigation.

Evidence Surface:

- reports/rcc_nexus
- docs/context

Validation Surface:

```powershell
python scripts/rcc/check_rcc_nexus.py
python -m unittest discover -s tests
```

Claim Boundary:

This folder improves implementation, evidence, documentation, and navigation only within its declared scope. It does not prove code correctness, patch safety, empirical validation, causality, mechanism, AI understanding, production readiness, or universal transfer.
'@
Write-Utf8 (Join-Path $Root "rcc\README.md") $RccReadme

$NexusReadme = @'
# Tessera RCC Nexus

## S - Specification

Repository Context Canon Nexus for Tessera Engine.

## H - Hooks

Inbound hooks:

- README.md
- AGENTS.md
- README_90_SECONDS.md
- docs/context/repository_context_index.json
- docs/context/rcc_nexus_index.json

Outbound hooks:

- route_map.json
- task_routing_matrix.md
- agent_handoff_contract.md
- reports/rcc_nexus/latest_rcc_nexus_check.json

## A - Artifacts

- route_map.json
- task_routing_matrix.md
- agent_handoff_contract.md
- validation reports

## T - Theory / Basis

RCC-N v1.7 adoption-profile governance, Rehydration Protocol origin alignment, Tessera v1.7 transfer discipline.

## I - Invariants

- Human README -> RCC Nexus README -> AI Agent README.
- Route map before edits.
- Echo Location before mutation.
- Validation before claim.
- Push only when James authorizes.

## E - Examples

```powershell
python scripts/rcc/check_rcc_nexus.py
```

## RCC Nexus Echo Location

Sphere Position:

- Shell: center
- Meridian(s): agent, drift, documentation, safety, telemetry, memory
- Sector: rcc/nexus
- Version / TTL: RCC-N-v1.7 / 180 days
- Last Verified: generated by All-One patch

Local Role:

- AI navigation and route-map layer for Tessera.

Claim Boundary:

RCC-N improves navigation. It does not prove correctness, safety, transfer, or validation.
'@
Write-Utf8 (Join-Path $Root "rcc\nexus\README.md") $NexusReadme

$RouteMap = [ordered]@{
    schema = "TESSERA-RCC-N-v1.7-route-map"
    repository = "Tessera"
    selected_profile = "Full"
    profile_reason = "neural runtime, evidence package, repair/transfer certificates, agent handoff, and future GitHub push"
    claim_boundary = "RCC navigation is not validation"
    entry_sequence = @(
        "README.md",
        "README_90_SECONDS.md",
        "AGENTS.md",
        "docs/context/repository_context_index.json",
        "docs/context/rcc_nexus_index.json",
        "rcc/nexus/route_map.json",
        "docs/alignment/origin_manifest.json"
    )
    routes = [ordered]@{
        architecture = @("docs/architecture", "docs/alignment", "docs/theory")
        runtime = @("src/tessera", "configs", "scripts")
        evidence = @("outputs", "reports", "ledgers")
        validation = @("tests", "scripts/rcc", "scripts/validation")
        agents = @("AGENTS.md", "rcc/nexus/agent_handoff_contract.md")
    }
    blocked_actions = @(
        "git push without explicit human authorization",
        "claiming transfer from synthetic run",
        "claiming correctness from README or RCC navigation",
        "live repair without shadow validation"
    )
}
Write-JsonFile (Join-Path $Root "rcc\nexus\route_map.json") $RouteMap

$TaskMatrix = @'
# Tessera RCC Task Routing Matrix

| Task | Read first | Validate with | Claim ceiling |
|---|---|---|---|
| README edit | README.md, README_90_SECONDS.md, docs/context indexes | scripts/rcc/check_rcc_nexus.py | documentation alignment only |
| Model/runtime edit | docs/architecture, src/tessera, tests | python -m unittest discover -s tests | local runtime health only |
| Evidence edit | outputs, reports, evidence writers | python -m tessera validate --run outputs/runs/latest | artifact consistency only |
| Theory import | docs/theory, import_manifest | scripts/validation/validate_architecture_contracts.py | source-surface preservation only |
| RCC edit | rcc/nexus, docs/context | scripts/rcc/check_rcc_nexus.py | navigation health only |
| Release prep | README, release notes, reports, outputs | tests + RCC + architecture validation | push candidate only |

## Push Rule

No GitHub push until James explicitly says to push.
'@
Write-Utf8 (Join-Path $Root "rcc\nexus\task_routing_matrix.md") $TaskMatrix

$AgentHandoff = @'
# Tessera Agent Handoff Contract

## Entry Order

1. Read `README.md`.
2. Read `README_90_SECONDS.md`.
3. Read `AGENTS.md`.
4. Read `docs/context/repository_context_index.json`.
5. Read `docs/context/rcc_nexus_index.json`.
6. Read `rcc/nexus/route_map.json`.
7. Read `docs/alignment/origin_manifest.json`.

## Before Editing

- Identify route.
- Identify validation command.
- Identify claim ceiling.
- Preserve non-claim locks.
- Preserve source attribution.

## After Editing

Run:

```powershell
python scripts/rcc/check_rcc_nexus.py
python scripts/validation/validate_architecture_contracts.py
python -m unittest discover -s tests
```

## Push Boundary

Do not push unless James explicitly authorizes push in the active session.
'@
Write-Utf8 (Join-Path $Root "rcc\nexus\agent_handoff_contract.md") $AgentHandoff

# ─────────────────────────────────────────────────────────────────────────────
# Step 6 — Context Indexes
# ─────────────────────────────────────────────────────────────────────────────

$RepoIndex = [ordered]@{
    schema = "TESSERA-repository-context-index-v0.1"
    repository = "Tessera"
    package = "tessera"
    cli = "tessera"
    status = "alignment_rcc_nexus_integrated_local"
    claim_ceiling = "diagnostic_baseline_limited_until_real_telemetry_transfer"
    read_order = @(
        "README.md",
        "README_90_SECONDS.md",
        "AGENTS.md",
        "docs/alignment/origin_manifest.json",
        "rcc/nexus/route_map.json",
        "docs/theory/import_manifest.json"
    )
    main_surfaces = [ordered]@{
        architecture = "docs/architecture/TESSERA_ENGINE_V0_1_SOFTWARE_ARCHITECTURE.md"
        alignment = "docs/alignment"
        rcc = "rcc/nexus"
        theory = "docs/theory"
        runtime = "src/tessera"
        tests = "tests"
        outputs = "outputs"
        reports = "reports"
    }
    validation_commands = @(
        "python scripts/rcc/check_rcc_nexus.py",
        "python scripts/validation/validate_architecture_contracts.py",
        "python -m unittest discover -s tests"
    )
}
Write-JsonFile (Join-Path $Root "docs\context\repository_context_index.json") $RepoIndex

$RccIndex = [ordered]@{
    schema = "TESSERA-rcc-nexus-index-v0.1"
    rcc_n_version = "RCC-N-v1.7"
    selected_profile = "Full"
    minimal_viable_compliance = "present"
    route_map = "rcc/nexus/route_map.json"
    task_matrix = "rcc/nexus/task_routing_matrix.md"
    handoff = "rcc/nexus/agent_handoff_contract.md"
    echo_locations = @(
        "rcc/README.md",
        "rcc/nexus/README.md",
        "docs/alignment/README.md",
        "docs/context/README.md",
        "docs/theory/README.md"
    )
    validation_surface = "scripts/rcc/check_rcc_nexus.py"
    claim_boundary = "profile adoption is not validation"
}
Write-JsonFile (Join-Path $Root "docs\context\rcc_nexus_index.json") $RccIndex

# ─────────────────────────────────────────────────────────────────────────────
# Step 7 — Theory Manifest and README Surfaces
# ─────────────────────────────────────────────────────────────────────────────

$TheoryFiles = @()
$TheoryRoots = @("docs\theory\imports", "docs\theory\tessera_lineage")
foreach ($TR in $TheoryRoots) {
    $Full = Join-Path $Root $TR
    if (Test-Path $Full) {
        $Found = Get-ChildItem -Path $Full -File -Recurse -ErrorAction SilentlyContinue
        foreach ($F in $Found) {
            $TheoryFiles += [ordered]@{
                path = ($F.FullName.Replace($Root + [System.IO.Path]::DirectorySeparatorChar, "") -replace '\\','/')
                bytes = $F.Length
                last_write = $F.LastWriteTime.ToString("s")
            }
        }
    }
}

$TheoryManifest = [ordered]@{
    schema = "TESSERA-theory-import-manifest-v0.1"
    generated_at = (Get-Date).ToString("s")
    source_boundary = "theory imports preserve attribution and do not create validation claims"
    imported_this_run = $ImportLog
    theory_files = $TheoryFiles
    non_claim_locks = @(
        "theory_import_is_not_validation",
        "documentation_is_not_correctness",
        "synthetic_success_is_not_transfer"
    )
}
Write-JsonFile (Join-Path $Root "docs\theory\import_manifest.json") $TheoryManifest

$TheoryReadme = @'
# Tessera Theory Surface

This folder stores imported theory sources and Tessera lineage documents.

## Boundary

Theory import preserves context. It does not prove runtime correctness, empirical transfer, or model superiority.

## Subfolders

- `imports/` — supporting external/internal theory references copied into the repo.
- `tessera_lineage/` — TESSERA v1.3 through v1.7 theory lineage when present.
- `inbox/` — drop zone for files to import with the All-One script.

## Validation

```powershell
python scripts/validation/validate_architecture_contracts.py
```
'@
Write-Utf8 (Join-Path $Root "docs\theory\README.md") $TheoryReadme

$ImportsReadme = @'
# Theory Imports

Place `.md`, `.txt`, `.tex`, `.json`, `.csv`, or `.pdf` theory files here, or place them in `docs/theory/inbox` and rerun the All-One patch.

## Boundary

Imported theory is context, not validation.
'@
Write-Utf8 (Join-Path $Root "docs\theory\imports\README.md") $ImportsReadme

$LineageReadme = @'
# Tessera Theory Lineage

This folder stores TESSERA theory versions and source lineage.

## Expected lineage

- v1.3 Spectral Triadic Field Architecture
- v1.4 Compressive Field Memory Architecture
- v1.5 Rate-Distortion Triadic Memory
- v1.6 Replay-Guided Codec Repair
- v1.7 Real Telemetry Transfer

## Boundary

Lineage preservation does not prove implementation correctness.
'@
Write-Utf8 (Join-Path $Root "docs\theory\tessera_lineage\README.md") $LineageReadme

# ─────────────────────────────────────────────────────────────────────────────
# Step 8 — Root README, 90-Second README, AGENTS
# ─────────────────────────────────────────────────────────────────────────────

$Readme = @'
# Tessera

Sparse compressive memory engine with replay-certified memory, wound-ledger repair, RCC Nexus navigation, and real-telemetry transfer discipline.

## Human Director Box

Tessera is a local-first reference runtime for testing whether a sparse spectral field can compress telemetry into candidate memories, replay those memories, compare against baselines, record wounds, and emit certificates without overclaiming.

## Current Health Snapshot

| Surface | Status |
|---|---|
| Package / CLI | `tessera` |
| Current engine | Tessera Engine v0.1 |
| RCC-N profile | Full |
| Alignment patch | present |
| Theory imports | `docs/theory/import_manifest.json` |
| Evidence package | emitted by local runs |
| Claim ceiling | diagnostic_baseline_limited |
| GitHub push | blocked until human authorization |

## Run

```powershell
python -m pip install -e .
python -m unittest discover -s tests
python -m tessera run --out outputs --steps 160 --epochs 2 --topology q4 --field-dim 16 --code-dim 8
python -m tessera validate --run outputs/runs/latest
```

## All-One Alignment Patch

```powershell
.\scripts\tessera_alignment_rcc_nexus_all_one_v0_1.ps1 -Root "C:\Users\jacks\OneDrive\Desktop\Tessera"
```

## Repository Spine

```text
README.md
-> README_90_SECONDS.md
-> AGENTS.md
-> docs/context/repository_context_index.json
-> docs/context/rcc_nexus_index.json
-> rcc/nexus/route_map.json
-> docs/alignment/origin_manifest.json
```

## What This Is Not

- Not AGI.
- Not consciousness.
- Not empirical validation.
- Not production readiness.
- Not proof of general anomaly-detection superiority.
- Not permission to push without James.

## Operating Law

Build small. Declare the graph. Compress the stream. Replay every memory. Wound every failure. Repair only in shadow. Promote only by certificate. Claim only what transfers.
'@
Write-Utf8 (Join-Path $Root "README.md") $Readme

$Readme90 = @'
# Tessera in 90 Seconds

Tessera is a sparse compressive memory engine.

It runs this loop:

```text
telemetry
-> sparse spectral field
-> compressed code
-> reconstruction / prediction
-> rate-distortion score
-> warning / block / memory gates
-> replay buffer
-> wound ledger
-> certificate
```

The repository is RCC-N navigable:

```text
README -> README_90_SECONDS -> AGENTS -> context indexes -> route map -> validation
```

Fast start:

```powershell
python -m pip install -e .
python -m unittest discover -s tests
python -m tessera run --out outputs --steps 160 --epochs 2 --topology q4 --field-dim 16 --code-dim 8
python -m tessera validate --run outputs/runs/latest
```

Claim boundary:

This is a local reference engine. It does not prove real telemetry transfer until V1.7 transfer protocol runs on declared real datasets with leakage guards, baselines, replay, and transfer certificates.
'@
Write-Utf8 (Join-Path $Root "README_90_SECONDS.md") $Readme90

$Agents = @'
# AGENTS.md — Tessera Agent Operating Contract

## Required Read Order

1. `README.md`
2. `README_90_SECONDS.md`
3. `docs/context/repository_context_index.json`
4. `docs/context/rcc_nexus_index.json`
5. `rcc/nexus/route_map.json`
6. `docs/alignment/origin_manifest.json`

## Before Editing

- Identify route.
- Identify validation command.
- Preserve source attribution.
- Preserve non-claim locks.
- Avoid claim inflation.
- Do not push without James.

## Validation Commands

```powershell
python scripts/rcc/check_rcc_nexus.py
python scripts/validation/validate_architecture_contracts.py
python -m unittest discover -s tests
python -m tessera validate --run outputs/runs/latest
```

## Claim Locks

- navigation_is_not_validation
- documentation_is_not_correctness
- context_reconstruction_is_not_code_quality
- synthetic_success_is_not_transfer
- replay_is_not_safety
- repair_is_not_truth
- validation_remains_required

## Push Rule

Do not push to GitHub unless James explicitly authorizes push in the active session.
'@
Write-Utf8 (Join-Path $Root "AGENTS.md") $Agents

# ─────────────────────────────────────────────────────────────────────────────
# Step 9 — Mini READMEs
# ─────────────────────────────────────────────────────────────────────────────

$MiniMap = @{
    "docs" = "Documentation, architecture, theory, context, and alignment surfaces."
    "docs\alignment" = "Origin alignment, non-claim locks, and local mutation boundaries."
    "docs\context" = "Repository context and RCC Nexus indexes."
    "docs\architecture" = "Tessera software architecture documents."
    "rcc" = "RCC root shell for Nexus routing."
    "scripts" = "Local automation, validation, release, and All-One scripts."
    "scripts\rcc" = "RCC validation scripts."
    "scripts\validation" = "Architecture and release validation scripts."
    "src" = "Python source root."
    "src\tessera" = "Tessera Python package and CLI."
    "tests" = "Unit and integration tests."
    "outputs" = "Generated local runtime artifacts."
    "reports" = "Generated validation and RCC reports."
    "configs" = "Runtime configuration profiles."
}

foreach ($K in $MiniMap.Keys) {
    $Folder = Join-Path $Root $K
    if (Test-Path $Folder) {
        $Content = @"
# Folder Purpose

## S - Specification

$($MiniMap[$K])

## H - Hooks

Inbound hooks:

- README.md
- AGENTS.md
- rcc/nexus/route_map.json

Outbound hooks:

- reports/
- outputs/
- validation commands

## A - Artifacts

This folder may contain source files, docs, reports, schemas, scripts, visuals, generated state, or validation records depending on its role.

## T - Theory / Basis

Governed by Tessera Engine v0.1, TESSERA v1.7 transfer discipline, RCC-N v1.7, and repository non-claim locks.

## I - Invariants

- Preserve source attribution.
- Preserve non-claim boundaries.
- Do not treat navigation as validation.
- Do not treat documentation as correctness.
- Keep evidence and validation surfaces inspectable.

## E - Examples

Read this file before editing this folder.

Run relevant validation after changes:

```powershell
python scripts/rcc/check_rcc_nexus.py
python scripts/validation/validate_architecture_contracts.py
python -m unittest discover -s tests
```

## RCC Nexus Echo Location

Sphere Position:

- Shell: middle
- Meridian(s): agent, drift, documentation, safety, telemetry, memory
- Sector: $K
- Version / TTL: RCC-N-v1.7 / 180 days
- Last Verified: generated by All-One patch

Claim Boundary:

This mini README improves local navigation and agent orientation. It does not prove code correctness, patch safety, empirical validation, production readiness, AI understanding, or transfer.
"@
        Write-Utf8 (Join-Path $Folder "README.md") $Content
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# Step 10 — Validators
# ─────────────────────────────────────────────────────────────────────────────

$RccChecker = @'
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = [
    "README.md",
    "README_90_SECONDS.md",
    "AGENTS.md",
    "rcc/README.md",
    "rcc/nexus/README.md",
    "rcc/nexus/route_map.json",
    "rcc/nexus/task_routing_matrix.md",
    "rcc/nexus/agent_handoff_contract.md",
    "docs/context/repository_context_index.json",
    "docs/context/rcc_nexus_index.json",
    "docs/alignment/origin_manifest.json",
    "docs/alignment/non_claim_locks.md",
    "docs/theory/import_manifest.json",
]

def main() -> int:
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    route = ROOT / "rcc/nexus/route_map.json"
    profile = None
    if route.exists():
        profile = json.loads(route.read_text(encoding="utf-8")).get("selected_profile")
    passed = not missing and profile in {"Lite", "Standard", "Full", "Federated", "Critical"}
    report = {
        "schema": "TESSERA-rcc-nexus-check-v0.1",
        "passed": passed,
        "missing": missing,
        "selected_profile": profile,
        "claim_boundary": "RCC navigation is not validation",
    }
    out = ROOT / "reports/rcc_nexus/latest_rcc_nexus_check.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return int(not passed)

if __name__ == "__main__":
    raise SystemExit(main())
'@
Write-Utf8 (Join-Path $Root "scripts\rcc\check_rcc_nexus.py") $RccChecker

$ArchValidator = @'
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED_DIRS = [
    "docs/alignment",
    "docs/context",
    "docs/theory",
    "rcc/nexus",
    "src/tessera",
    "tests",
    "reports/rcc_nexus",
    "reports/validation",
]
REQUIRED_LOCKS = [
    "navigation_is_not_validation",
    "documentation_is_not_correctness",
    "synthetic_success_is_not_transfer",
    "validation_remains_required",
]

def main() -> int:
    missing_dirs = [p for p in REQUIRED_DIRS if not (ROOT / p).exists()]
    locks_path = ROOT / "docs/alignment/non_claim_locks.md"
    locks_text = ""
    if locks_path.exists():
        locks_text = locks_path.read_text(encoding="utf-8")
    missing_locks = [x for x in REQUIRED_LOCKS if x not in locks_text]
    theory_manifest = ROOT / "docs/theory/import_manifest.json"
    theory_ok = theory_manifest.exists()
    passed = not missing_dirs and not missing_locks and theory_ok
    report = {
        "schema": "TESSERA-architecture-contract-validation-v0.1",
        "passed": passed,
        "missing_dirs": missing_dirs,
        "missing_locks": missing_locks,
        "theory_manifest_present": theory_ok,
        "claim_boundary": "architecture validation is not empirical validation",
    }
    out = ROOT / "reports/validation/latest_architecture_contract_validation.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return int(not passed)

if __name__ == "__main__":
    raise SystemExit(main())
'@
Write-Utf8 (Join-Path $Root "scripts\validation\validate_architecture_contracts.py") $ArchValidator

# ─────────────────────────────────────────────────────────────────────────────
# Step 11 — Validation and Smoke Run
# ─────────────────────────────────────────────────────────────────────────────

if (-not $SkipInstall) {
    if (Test-Path "pyproject.toml") {
        Run-Safe -Exe "python" -ArgList @("-m", "pip", "install", "-e", ".") -TimeoutSeconds 600
    }
}

Run-Safe -Exe "python" -ArgList @("scripts/rcc/check_rcc_nexus.py") -TimeoutSeconds 120
Run-Safe -Exe "python" -ArgList @("scripts/validation/validate_architecture_contracts.py") -TimeoutSeconds 120

if (-not $SkipTests) {
    if (Test-Path "tests") {
        Run-Safe -Exe "python" -ArgList @("-m", "unittest", "discover", "-s", "tests") -TimeoutSeconds 600
    }
}

if (-not $SkipRun) {
    Run-Safe -Exe "python" -ArgList @("-m", "tessera", "run", "--out", "outputs", "--steps", "160", "--epochs", "2", "--topology", "q4", "--field-dim", "16", "--code-dim", "8") -TimeoutSeconds 900
    Run-Safe -Exe "python" -ArgList @("-m", "tessera", "validate", "--run", "outputs/runs/latest") -TimeoutSeconds 240
}

# ─────────────────────────────────────────────────────────────────────────────
# Step 12 — Patch Report and Optional Package
# ─────────────────────────────────────────────────────────────────────────────

$PatchReport = [ordered]@{
    schema = "TESSERA-alignment-rcc-nexus-all-one-report-v0.1"
    root = $Root
    completed_at = (Get-Date).ToString("s")
    rcc_check = "reports/rcc_nexus/latest_rcc_nexus_check.json"
    architecture_check = "reports/validation/latest_architecture_contract_validation.json"
    theory_manifest = "docs/theory/import_manifest.json"
    origin_manifest = "docs/alignment/origin_manifest.json"
    route_map = "rcc/nexus/route_map.json"
    push_status = "blocked_until_james_authorizes"
    claim_ceiling = "diagnostic_baseline_limited_until_real_telemetry_transfer"
}
Write-JsonFile (Join-Path $Root "reports\rcc_nexus\latest_alignment_rcc_all_one_report.json") $PatchReport

$PatchMd = @"
# Tessera Alignment + RCC Nexus All-One Patch Report

Completed at: $((Get-Date).ToString("s"))

## Surfaces

- RCC check: `reports/rcc_nexus/latest_rcc_nexus_check.json`
- Architecture check: `reports/validation/latest_architecture_contract_validation.json`
- Theory manifest: `docs/theory/import_manifest.json`
- Origin manifest: `docs/alignment/origin_manifest.json`
- Route map: `rcc/nexus/route_map.json`

## Push Status

GitHub push is blocked until James explicitly authorizes it.

## Claim Ceiling

`diagnostic_baseline_limited_until_real_telemetry_transfer`
"@
Write-Utf8 (Join-Path $Root "TESSERA_ENGINE_V0_1_ALIGNMENT_RCC_NEXUS_PATCH.md") $PatchMd

if (-not $SkipPackage) {
    $Zip = Join-Path (Split-Path -Parent $Root) "Tessera_alignment_rcc_nexus_all_one_patch.zip"
    if (Test-Path $Zip) {
        Remove-Item $Zip -Force
    }
    Compress-Archive -Path (Join-Path $Root "*") -DestinationPath $Zip -Force
    Say "Package written: $Zip" "🜂"
}

Set-Location $Root
Say "RootMirror returned to: $Root" "🜄"
Say "Tessera Alignment + RCC Nexus All-One patch complete." "🜄"
Say "Push remains blocked until James authorizes it." "🜁"
