<# TESSERA CANONICAL FULL LOOP v0.3.2 :: PowerShell launcher only #>
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
$ArgsList = @("-m", "tessera.operator_geometry", "launch", "--root", $Root)
if ($NoPush) { $ArgsList += "--no-push" }
if ($SkipRun) { $ArgsList += "--skip-run" }
if ($SkipTests) { $ArgsList += "--skip-tests" }
python @ArgsList
