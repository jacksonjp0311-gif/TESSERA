# EVO-034 Semantic Production Candidate

## Question

Can the EVO-032 natural-session uncertainty router be transferred into the
supervised plugin without changing its calibrated feature meaning or route
decisions?

## Result

Yes, within the repository's local evidence boundary.

- 120 chronological clean sessions were reconstructed.
- The versioned adapter reproduced the calibrated mean/std/latest session
  geometry and the same five varying features.
- Native AgentEvent and JSON-safe reference adapters were numerically identical.
- All 20 untouched final routes matched the offline router: 18 trusted and 2
  abstained.
- Warm p95 was 95.19 ms against a 250 ms budget.
- A 100-request soak had zero failures and 126.79 ms p99.
- Restart routing was deterministic.
- Worker crashes were contained and opened the circuit breaker.
- An isolated lifecycle transaction probe verified immutable checkpoint
  activation and rollback without promoting the checkpoint's rejected
  forecasting utility.
- Critical release files were bound into the evidence artifact by SHA-256.

## Decision

Promote Tessera v0.3.0 to **local production candidate**. Do not call it an
externally production-ready deployment until the following gates close:

1. untouched natural failure-and-recovery evidence;
2. two genuinely independent external host integrations;
3. independent security and dependency review;
4. independent clean-environment reproduction.

The neural field owns selective trust routing only. Stable EWMA retains
forecast ownership, and the plugin has no host-memory, tool, prompt, topology,
codec, or external API authority.
