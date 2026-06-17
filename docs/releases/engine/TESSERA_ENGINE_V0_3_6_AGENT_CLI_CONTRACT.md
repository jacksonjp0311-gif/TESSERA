# TESSERA Engine v0.3.6 - Universal Agent CLI Contract

This patch enforces the Hermes-style Agent CLI rule across operator-facing entrypoints.

## Rule

```text
Every operator-facing loop opens the Agent CLI.
Observer opens first.
Worker opens second.
Internal validators report into the live Worker/Observer state instead of spawning new windows.
```

## Boundary

This improves operator visibility and loop governance. It does not prove correctness, safety, production readiness, AGI, consciousness, or real telemetry transfer.