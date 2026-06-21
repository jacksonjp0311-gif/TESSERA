# Tessera Production Candidate

Tessera may be labeled a **local production candidate** only when:

```powershell
python -m tessera launch-readiness --root .
python scripts/loopbook/sync_loopbook.py
python scripts/validation/validate_loopbook_gate.py
python -m unittest discover -s tests
```

passes on the same repository state. The command intentionally runs the
latency-sensitive runtime gate before wheel construction; do not run those
certifications concurrently on the same host.

## What the local gate certifies

- The versioned session-summary adapter reproduces the EVO-032 calibration
  space.
- The AgentEvent and JSON reference adapters emit identical vectors.
- Runtime trust routes match the offline final-test routes exactly.
- Abstention suppresses memory candidacy without changing forecast ownership.
- Warm latency, restart determinism, sustained-load latency, circuit breaking,
  checkpoint admission, and rollback pass their declared gates.
- Critical runtime and release files are recorded by SHA-256.
- The distributable wheel has coherent versions, valid RECORD hashes, no
  forbidden repository payloads, a successful isolated installation, a
  successful package inference smoke test, and a working installed CLI.

## Deployment sequence

1. Run both production and release-readiness gates on the release commit.
2. Pin the admitted checkpoint, summary contract, router threshold, and
   `configs/production.json` together as one release unit.
3. Start the supervised worker and complete warmup before traffic.
4. Emit one summary only after each host session closes; preserve chronological
   order and never include sensitive payloads.
5. Treat `abstain` as no memory candidacy and no automated host intervention.
6. Latch abstention after any observed host failure; release only after the
   configured number of clean terminal sessions.
7. Monitor latency, worker failures, route coverage, and schema mismatches.
8. On failure, unload the worker or roll back the active checkpoint pointer.

## External launch blockers

- Four additional independent natural failure-and-recovery incidents.
- Two genuinely independent external host integrations.
- Independent security review and dependency vulnerability scan.
- Independent reproduction in a clean environment.
- Cross-platform subprocess certification.

Passing the repository gate does not prove general safety, natural failure
sensitivity, production readiness in an external host, AGI, consciousness, or
autonomous authority.
