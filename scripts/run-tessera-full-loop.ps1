<# TESSERA FULL LOOP :: delegates to Agent CLI Mirror #>
param(
    [string]$Root = "$env:USERPROFILE\OneDrive\Desktop\Tessera",
    [switch]$NoPush,
    [switch]$SkipRun,
    [switch]$SkipTests
)
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path $Root).Path
$ArgsList = @("-ExecutionPolicy", "Bypass", "-File", (Join-Path $Root "scripts\agent-mirror.ps1"), "-Root", $Root, "-Command", "full")
if ($NoPush) { $ArgsList += "-NoPush" }
if ($SkipRun) { $ArgsList += "-SkipRun" }
if ($SkipTests) { $ArgsList += "-SkipTests" }
powershell @ArgsList