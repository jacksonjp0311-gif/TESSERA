# TESSERA Engine v0.1.5 — GitHub Seed Latest-Pointer Publish Repair

## Purpose

Repairs the second Windows seed failure: `outputs/runs/latest` must point to or copy the completed run after artifacts are written, not before.

## Fix

- `make_run_dir()` creates the run directory and clears stale latest only.
- `publish_latest_run(run_dir)` publishes `latest` after artifacts exist.
- `run_synthetic.py` calls `publish_latest_run(run_dir)` after writing summary/evidence/certificates.

## Boundary

Synthetic success is not transfer. Validation remains required. Push requires `-Commit -AllowPush`.