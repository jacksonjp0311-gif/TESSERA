# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║   TESSERA ENGINE v0.1.2 — README / NEXUS DISCIPLINE ALL-ONE PATCH           ║
# ║   README TRISECTION, PUBLIC METRICS, RCC-N ROUTE DISCIPLINE, README AUDIT,  ║
# ║   VALIDATION STACK, PUSH-BLOCKED RELEASE PREP, AND ROOTMIRROR RETURN        ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
param(
    [string]$Root = "C:\Users\jacks\OneDrive\Desktop\Tessera",
    [switch]$SkipInstall,
    [switch]$SkipRun,
    [switch]$SkipTests
)
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$script:TesseraRoot = $null
trap {
    if ($script:TesseraRoot -and (Test-Path $script:TesseraRoot)) {
        Set-Location $script:TesseraRoot
        Write-Host "🜄  RootMirror return after error: $script:TesseraRoot"
    }
    Write-Host "🔴  README / Nexus discipline patch stopped before completion."
    break
}
function Say { param([string]$Message, [string]$Glyph = "🜁"); Write-Host "$Glyph  $Message" }
function Run-Safe { param([string]$Exe, [string[]]$ArgList); Say "$Exe $($ArgList -join ' ')" "🜂"; & $Exe @ArgList; if ($LASTEXITCODE -ne 0) { throw "Command failed: $Exe $($ArgList -join ' ')" } }
if (-not (Test-Path $Root)) { throw "Root path does not exist: $Root" }
Set-Location $Root
$script:TesseraRoot = (Resolve-Path $Root).Path
$env:PYTHONPATH = Join-Path $script:TesseraRoot "src"
Say "Root anchored: $script:TesseraRoot" "🜄"
if (-not $SkipInstall) { Run-Safe -Exe "python" -ArgList @("-m", "pip", "install", "-e", ".") }
Run-Safe -Exe "python" -ArgList @("scripts/rcc/check_rcc_nexus.py")
Run-Safe -Exe "python" -ArgList @("scripts/validation/validate_architecture_contracts.py")
Run-Safe -Exe "python" -ArgList @("scripts/readme/audit_readme_nexus_discipline.py")
if (-not $SkipTests) { Run-Safe -Exe "python" -ArgList @("-m", "unittest", "discover", "-s", "tests") }
if (-not $SkipRun) {
    Run-Safe -Exe "python" -ArgList @("-m", "tessera", "run", "--out", "outputs", "--steps", "160", "--epochs", "2", "--topology", "q4", "--field-dim", "16", "--code-dim", "8")
    Run-Safe -Exe "python" -ArgList @("-m", "tessera", "validate", "--run", "outputs/runs/latest")
}
$ReportDir = Join-Path $script:TesseraRoot "reports/readme"
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$PatchReport = Join-Path $ReportDir "latest_v0_1_2_readme_nexus_patch.md"
@"
# Tessera v0.1.2 README / Nexus Discipline Patch

Status: complete locally.

Validated:

- RCC Nexus checker
- Architecture contract validator
- README / Nexus discipline audit
- Unit tests unless skipped
- Tessera smoke run unless skipped

Push boundary: blocked until James explicitly authorizes push.

RootMirror: returned to $script:TesseraRoot
"@ | Set-Content -Path $PatchReport -Encoding UTF8
Set-Location $script:TesseraRoot
Say "RootMirror returned to: $script:TesseraRoot" "🜄"
Say "Tessera v0.1.2 README / Nexus discipline patch complete." "🜄"
Say "Push remains blocked until James authorizes it." "🜁"
