<#
TESSERA OPERATOR SHELL v0.2.2
A compressed local PowerShell console for running the Tessera loop.
Commands: status, compile, check, run, validate, full, push, help, exit
#>
param(
    [string]$Root = "$env:USERPROFILE\OneDrive\Desktop\Tessera",
    [switch]$NoPush
)

$ErrorActionPreference = "Stop"
$script:Root = (Resolve-Path $Root).Path
Set-Location $script:Root
[System.IO.Directory]::SetCurrentDirectory($script:Root)
$env:PYTHONPATH = Join-Path $script:Root "src"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

function Open-Box([string]$Name) { Write-Host "`n::group::$Name"; Write-Host "[RUN] $Name" }
function Close-Box { Write-Host "::endgroup::" }
function OK([string]$Text) { Write-Host "[OK] $Text" }
function NO([string]$Text) { Write-Host "[FAIL] $Text" }
function CMD([string]$Label, [string]$Exe, [string[]]$Args) {
    Write-Host "[CMD] $Label"
    & $Exe @Args
    $Code = $LASTEXITCODE
    if ($null -eq $Code) { $Code = 0 }
    if ($Code -ne 0) { throw "failed: $Label" }
    OK $Label
}

function Show-Header {
    Clear-Host
    Write-Host "+--------------------------------------------------------------+"
    Write-Host "| TESSERA OPERATOR SHELL v0.2.2                                |"
    Write-Host "+--------------------------------------------------------------+"
    Write-Host "| rehydrate -> shell -> compile -> check -> run -> validate     |"
    Write-Host "| ledger -> push -> root                                       |"
    Write-Host "+--------------------------------------------------------------+"
    Write-Host "| commands: status compile check run validate full push help exit|"
    Write-Host "+--------------------------------------------------------------+"
    Write-Host "root: $script:Root"
    Write-Host "push: $(if ($NoPush) { 'disabled' } else { 'enabled after validation' })"
}

function Invoke-Status {
    Open-Box "status"
    Write-Host "Root: $script:Root"
    Write-Host "PYTHONPATH: $env:PYTHONPATH"
    git status --short
    if (Test-Path "reports/runtime_loop/tessera_shell_status.json") {
        Get-Content "reports/runtime_loop/tessera_shell_status.json"
    }
    Close-Box
}

function Invoke-Compile {
    Open-Box "compile"
    CMD "loop ascii" python @("-m", "tessera", "loop", "ascii")
    CMD "loop compile" python @("-m", "tessera", "loop", "compile", "--out", "reports/runtime_loop")
    Close-Box
}

function Invoke-Check {
    Open-Box "check"
    CMD "rcc nexus" python @("scripts/rcc/check_rcc_nexus.py")
    CMD "architecture" python @("scripts/validation/validate_architecture_contracts.py")
    CMD "readme discipline" python @("scripts/readme/audit_readme_nexus_discipline.py")
    CMD "operator shell" python @("scripts/validation/validate_operator_shell.py")
    if (Test-Path "scripts/validation/validate_runtime_loop_compiler.py") {
        CMD "runtime loop compiler" python @("scripts/validation/validate_runtime_loop_compiler.py")
    }
    CMD "unit tests" python @("-m", "unittest", "discover", "-s", "tests")
    Close-Box
}

function Invoke-RunLoop {
    Open-Box "runtime"
    CMD "tessera run" python @("-m", "tessera", "run", "--out", "outputs", "--steps", "80", "--epochs", "1", "--topology", "q4", "--field-dim", "16", "--code-dim", "8")
    Close-Box
}

function Invoke-ValidateLatest {
    Open-Box "validate"
    CMD "validate latest" python @("-m", "tessera", "validate", "--run", "outputs/runs/latest")
    Close-Box
}

function Invoke-Push {
    Open-Box "push"
    if ($NoPush) { Write-Host "[SKIP] NoPush active"; Close-Box; return }
    git add -A
    $Status = git status --porcelain
    if (-not $Status) { Write-Host "[OK] clean; nothing to commit"; Close-Box; return }
    git commit -m "feat: update Tessera operator shell loop surfaces"
    git push -u origin main
    OK "pushed origin main"
    Close-Box
}

function Invoke-Full {
    Invoke-Compile
    Invoke-Check
    Invoke-RunLoop
    Invoke-ValidateLatest
    Invoke-Push
}

Show-Header
while ($true) {
    $Cmd = Read-Host "tessera"
    switch ($Cmd.Trim().ToLowerInvariant()) {
        "status" { Invoke-Status }
        "compile" { Invoke-Compile }
        "check" { Invoke-Check }
        "run" { Invoke-RunLoop }
        "validate" { Invoke-ValidateLatest }
        "push" { Invoke-Push }
        "full" { Invoke-Full }
        "help" { Show-Header }
        "exit" { break }
        "quit" { break }
        default { Write-Host "commands: status compile check run validate full push help exit" }
    }
}
Set-Location $script:Root
[System.IO.Directory]::SetCurrentDirectory($script:Root)
Write-Host "[ROOT] $script:Root"