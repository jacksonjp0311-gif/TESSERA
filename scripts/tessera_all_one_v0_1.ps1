# ============================================================================
# TESSERA ENGINE V0.1 -- ALL-ONE LOCAL RUNNER
# ----------------------------------------------------------------------------
# Fixed-root, local-first bootstrap. Builds environment, runs tests, executes a
# reference TESSERA synthetic run, validates artifacts, and returns to root.
# ============================================================================

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "TESSERA ENGINE V0.1 :: local bootstrap" -ForegroundColor Cyan

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

$Py = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) {
    $Py = "python"
}

& $Py -m pip install -e .
& $Py -m unittest discover -s tests
& $Py -m tessera run --out outputs --steps 900 --epochs 6 --topology q4 --field-dim 16 --code-dim 8
& $Py -m tessera validate --run outputs/runs/latest

Set-Location $Root
Write-Host "TESSERA ENGINE V0.1 :: complete" -ForegroundColor Green
