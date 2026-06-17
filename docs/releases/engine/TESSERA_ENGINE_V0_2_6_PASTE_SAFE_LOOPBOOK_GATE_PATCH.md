# TESSERA Engine v0.2.6 - Paste-Safe Loopbook Gate Launcher

## Change

- Removes top-level `param(...)` dependency so the installer can be pasted or run as a file.
- Hard-locks root to `C:\Users\jacks\OneDrive\Desktop\Tessera`.
- Uses `git -C` for every Git command.
- Adds permanent `docs/loop/TESSERA_LOOPBOOK.md`.
- Adds `docs/loop/loopbook_manifest.json`.
- Adds `scripts/loopbook/sync_loopbook.py`.
- Adds `scripts/validation/validate_loopbook_gate.py`.
- Makes `scripts/run-tessera-full-loop.ps1` the canonical command.
- Ensures the full loop opens Observer and Worker PowerShell windows every time.
- Keeps pip install off by default.

## Boundary

This improves local operator visibility and runtime repeatability. It does not prove real telemetry transfer, production readiness, safety, or correctness.