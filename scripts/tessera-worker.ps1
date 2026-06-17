<# TESSERA WORKER v0.2.6 :: runs code, emits live state for observer #>
param([string]$Root = "$env:USERPROFILE\OneDrive\Desktop\Tessera", [switch]$NoPush, [switch]$SkipRun, [switch]$SkipTests)
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path $Root).Path
Set-Location $Root
[System.IO.Directory]::SetCurrentDirectory($Root)
$env:PYTHONPATH = Join-Path $Root "src"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$Live = Join-Path $Root "reports\operator_shell\live"
New-Item -ItemType Directory -Force -Path $Live | Out-Null
$StatusPath = Join-Path $Live "status.json"
$EventsPath = Join-Path $Live "events.jsonl"
if (Test-Path $EventsPath) { Remove-Item $EventsPath -Force }
function Emit([string]$Phase, [string]$State, [string]$Detail) {
    $Obj = [ordered]@{ schema="TESSERA-live-status-v0.2.6"; timestamp=(Get-Date).ToString("s"); phase=$Phase; state=$State; detail=$Detail; root=$Root; no_push=[bool]$NoPush }
    $Json = $Obj | ConvertTo-Json -Depth 20 -Compress
    [System.IO.File]::WriteAllText($StatusPath, ($Obj | ConvertTo-Json -Depth 20), [System.Text.UTF8Encoding]::new($false))
    [System.IO.File]::AppendAllText($EventsPath, $Json + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
}
function Cmd([string]$Phase, [string]$Label, [string]$Exe, [string[]]$Args) {
    Emit $Phase "RUN" $Label
    Write-Host "`n::group::$Phase :: $Label"
    & $Exe @Args
    $Code = $LASTEXITCODE
    if ($null -eq $Code) { $Code = 0 }
    Write-Host "::endgroup::"
    if ($Code -ne 0) { Emit $Phase "FAIL" "$Label exit=$Code"; throw "$Label failed" }
    Emit $Phase "OK" $Label
}
function GitCmd([string]$Phase, [string]$Label, [string[]]$Args) {
    Emit $Phase "RUN" $Label
    Write-Host "`n::group::$Phase :: $Label"
    & git -C $Root @Args
    $Code = $LASTEXITCODE
    if ($null -eq $Code) { $Code = 0 }
    Write-Host "::endgroup::"
    if ($Code -ne 0) { Emit $Phase "FAIL" "$Label exit=$Code"; throw "$Label failed" }
    Emit $Phase "OK" $Label
}
try {
    Emit "REHYDRATE" "RUN" "worker opened"
    Cmd "LOOPBOOK" "sync loopbook" python @("scripts/loopbook/sync_loopbook.py")
    Cmd "LOOPBOOK" "validate loopbook gate" python @("scripts/validation/validate_loopbook_gate.py")
    Cmd "CHECK" "rcc nexus" python @("scripts/rcc/check_rcc_nexus.py")
    Cmd "CHECK" "architecture contracts" python @("scripts/validation/validate_architecture_contracts.py")
    Cmd "CHECK" "readme discipline" python @("scripts/readme/audit_readme_nexus_discipline.py")
    if (-not $SkipTests) { Cmd "CHECK" "unit tests" python @("-m", "unittest", "discover", "-s", "tests") }
    if ($SkipTests) { Emit "CHECK" "SKIP" "unit tests skipped" }
    if (-not $SkipRun) {
        Cmd "RUN" "tessera runtime" python @("-m", "tessera", "run", "--out", "outputs", "--steps", "80", "--epochs", "1", "--topology", "q4", "--field-dim", "16", "--code-dim", "8")
        Cmd "VALIDATE" "validate latest evidence" python @("-m", "tessera", "validate", "--run", "outputs/runs/latest")
    }
    if ($SkipRun) { Emit "RUN" "SKIP" "runtime skipped" }
    $Report = [ordered]@{ schema="TESSERA-v0.2.6-worker-report"; completed_at=(Get-Date).ToString("s"); root=$Root; claim_boundary="diagnostic runtime only; not real telemetry transfer" }
    New-Item -ItemType Directory -Force -Path (Join-Path $Root "reports\release") | Out-Null
    [System.IO.File]::WriteAllText((Join-Path $Root "reports\release\tessera_v0_2_6_worker_report.json"), ($Report | ConvertTo-Json -Depth 30), [System.Text.UTF8Encoding]::new($false))
    Emit "LEDGER" "OK" "worker report written"
    if ($NoPush) { Emit "PUSH" "SKIP" "NoPush active" }
    if (-not $NoPush) {
        GitCmd "PUSH" "git status" @("status", "--short")
        GitCmd "PUSH" "git add" @("add", "-A")
        $Dirty = & git -C $Root status --porcelain
        if ($Dirty) {
            GitCmd "PUSH" "git commit" @("commit", "-m", "feat: update Tessera loopbook gate evidence")
            GitCmd "PUSH" "git push" @("push", "-u", "origin", "main")
        }
        if (-not $Dirty) { Emit "PUSH" "OK" "nothing to commit" }
    }
    Set-Location $Root
    [System.IO.Directory]::SetCurrentDirectory($Root)
    Emit "ROOT" "OK" "RootMirror returned"
    Write-Host "[DONE] Worker complete. Root: $Root"
} catch {
    Emit "FAIL" "FAIL" "$_."
    Set-Location $Root
    [System.IO.Directory]::SetCurrentDirectory($Root)
    throw
}