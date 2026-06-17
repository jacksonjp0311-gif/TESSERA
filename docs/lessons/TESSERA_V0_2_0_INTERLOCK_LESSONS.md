# Tessera v0.2.0 Lessons Learned — Interconnect Then Disconnect

## What We Learned

1. **Actor and governor must stay separate.** Hermes-Agent-Evo treats Hermes as the actor, RCC as orientation, CMS as governance, and human authorization as the dangerous-transition boundary. Tessera mirrors that pattern without importing Hermes runtime authority.
2. **A loop should compile before it runs.** The runtime is easier to audit when every cycle can emit ASCII, Bash, PowerShell, manifest, and evidence surfaces.
3. **Latest pointers must be published after evidence exists.** The v0.1.4 failure proved that creating `latest` before artifacts exist produces validation drift.
4. **Validation is not push.** The v0.1.5 log showed validation can pass while push remains blocked if commit/push authorization is not active.
5. **Interlock is not dependency.** Tessera can learn from Hermes geometry, but it must remain a self-contained runtime.

## Disconnect Boundary

Tessera carries forward the lessons and formatting discipline only. It does not import Hermes runtime folders, CMS write surfaces, external API authority, autonomous apply, self-authorization, automatic rollback, or production-readiness claims.

## v0.2.0 Operating Law

```text
Compile the loop.
Run the loop.
Validate the loop.
Ledger the lesson.
Disconnect foreign authority.
Push only after local evidence passes.
```