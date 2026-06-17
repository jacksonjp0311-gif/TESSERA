# TESSERA Engine v0.2.8 - Python Loop Kernel

## Change

- Moves loop ownership into `src/tessera/loop_runtime.py`.
- Keeps PowerShell as a thin terminal launcher only.
- Adds direct Python commands:
  - `python -m tessera.loop_runtime sync`
  - `python -m tessera.loop_runtime validate-loopbook`
  - `python -m tessera.loop_runtime launch`
  - `python -m tessera.loop_runtime worker`
  - `python -m tessera.loop_runtime observe`
  - `python -m tessera.loop_runtime check`
- Writes Loopbook, Failure Lessons, and Operator Loop Chart from Python.
- Preserves dual-console observer/worker behavior while making Python the source of truth.

## Boundary

This improves portability, testability, and loop governance. It does not prove real telemetry transfer, production readiness, safety, or correctness.