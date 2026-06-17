<# Agent CLI Mirror PowerShell Entrypoint #>
param(
    [string]$Root = "$env:USERPROFILE\OneDrive\Desktop\Tessera",
    [string]$Command = "full",
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
$ArgsList = @("agent_cli_mirror/agent_mirror.py", "launch", "--root", $Root, "--command", $Command)
if ($NoPush) { $ArgsList += "--no-push" }
if ($SkipRun) { $ArgsList += "--skip-run" }
if ($SkipTests) { $ArgsList += "--skip-tests" }
python @ArgsList