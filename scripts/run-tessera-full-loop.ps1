$ErrorActionPreference = "Stop"
$Root = if ($args.Count -gt 0) { $args[0] } else { (Get-Location).Path }
Set-Location $Root
[System.IO.Directory]::SetCurrentDirectory($Root)
$env:PYTHONPATH = (Join-Path $Root "src")
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
Write-Host "::group::compile"
python -m tessera loop compile --out reports/runtime_loop
Write-Host "::endgroup::"
Write-Host "::group::check"
python scripts/rcc/check_rcc_nexus.py
python scripts/validation/validate_architecture_contracts.py
python scripts/readme/audit_readme_nexus_discipline.py
python scripts/validation/validate_operator_shell.py
python scripts/validation/validate_runtime_loop_compiler.py
python -m unittest discover -s tests
Write-Host "::endgroup::"
Write-Host "::group::runtime"
python -m tessera run --out outputs --steps 80 --epochs 1 --topology q4 --field-dim 16 --code-dim 8
python -m tessera validate --run outputs/runs/latest
Write-Host "::endgroup::"
