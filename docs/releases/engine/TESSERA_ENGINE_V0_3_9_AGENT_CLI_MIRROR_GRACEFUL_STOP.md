# TESSERA Engine v0.3.9 - Agent CLI Mirror Graceful Stop

This patch hardens the Agent CLI Mirror so operator interrupts are handled as governed events rather than raw Python tracebacks.

## Fixes

```text
Observer Ctrl+C exits cleanly.
Worker Ctrl+C records a lesson and emits STOP state.
Subprocess commands are isolated into a process group where supported.
Agent CLI contract validator accepts --command mirror routing.
README documents lightweight interface checks with -SkipRun / command=validate.
```

## Boundary

This is operator-interface hardening. It does not prove autonomy, production readiness, safety, code correctness, AGI, consciousness, or real telemetry transfer.
