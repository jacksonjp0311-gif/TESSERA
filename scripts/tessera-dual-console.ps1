<# TESSERA DUAL-CONSOLE LAUNCHER v0.2.6 #>
param([string]$Root = "$env:USERPROFILE\OneDrive\Desktop\Tessera", [switch]$NoPush, [switch]$SkipRun, [switch]$SkipTests)
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path $Root).Path
Set-Location $Root
[System.IO.Directory]::SetCurrentDirectory($Root)
$Live = Join-Path $Root "reports\operator_shell\live"
New-Item -ItemType Directory -Force -Path $Live | Out-Null
Remove-Item -Force -ErrorAction SilentlyContinue (Join-Path $Live "events.jsonl")
Remove-Item -Force -ErrorAction SilentlyContinue (Join-Path $Live "status.json")
python scripts/loopbook/sync_loopbook.py
python scripts/validation/validate_loopbook_gate.py
$PsExe = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
$Observer = Join-Path $Root "scripts\tessera-watch.ps1"
$Worker = Join-Path $Root "scripts\tessera-worker.ps1"
$ObsArgs = @("-NoExit", "-ExecutionPolicy", "Bypass", "-File", $Observer, "-Root", $Root)
$WorkArgs = @("-NoExit", "-ExecutionPolicy", "Bypass", "-File", $Worker, "-Root", $Root)
if ($NoPush) { $WorkArgs += "-NoPush" }
if ($SkipRun) { $WorkArgs += "-SkipRun" }
if ($SkipTests) { $WorkArgs += "-SkipTests" }
Write-Host "[TESSERA] Opening Observer PowerShell..."
Start-Process -FilePath $PsExe -ArgumentList $ObsArgs -WorkingDirectory $Root
Start-Sleep -Seconds 1
Write-Host "[TESSERA] Opening Worker PowerShell..."
Start-Process -FilePath $PsExe -ArgumentList $WorkArgs -WorkingDirectory $Root
Write-Host "[TESSERA] Loopbook dual-console launched."
Write-Host "[ROOT] $Root"