<# TESSERA CANONICAL FULL LOOP v0.2.6 :: always opens observer/worker #>
param(
    [string]$Root = "$env:USERPROFILE\OneDrive\Desktop\Tessera",
    [switch]$NoPush,
    [switch]$SkipRun,
    [switch]$SkipTests
)
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path $Root).Path
Set-Location $Root
[System.IO.Directory]::SetCurrentDirectory($Root)
$env:PYTHONPATH = Join-Path $Root "src"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
python scripts/loopbook/sync_loopbook.py
python scripts/validation/validate_loopbook_gate.py
$ArgsList = @("-Root", $Root)
if ($NoPush) { $ArgsList += "-NoPush" }
if ($SkipRun) { $ArgsList += "-SkipRun" }
if ($SkipTests) { $ArgsList += "-SkipTests" }
& (Join-Path $Root "scripts\tessera-dual-console.ps1") @ArgsList
Set-Location $Root
[System.IO.Directory]::SetCurrentDirectory($Root)
Write-Host "[ROOT] $Root"
