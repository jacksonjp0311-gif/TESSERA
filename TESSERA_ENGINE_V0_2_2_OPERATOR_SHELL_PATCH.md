# TESSERA Engine v0.2.2 - PowerShell Operator Shell

## Change

- Adds `scripts/tessera-shell.ps1`, a local compressed operator shell.
- Uses local `PYTHONPATH`; pip install is optional with `-Install` in the All-One script.
- Adds grouped `::group::` output and `[OK]` status rows.
- Adds ASCII-safe loop compiler output for Windows terminals.
- Normalizes JSON/markdown without BOM before validators run.
- Pushes by default after validation unless `-NoPush` is supplied.
- Records Hermes-Agent-Evo and ASF-R lessons, then disconnects foreign authority.

## Boundary

This improves local operator visibility and runtime repeatability. It does not prove real telemetry transfer, production readiness, safety, or correctness.