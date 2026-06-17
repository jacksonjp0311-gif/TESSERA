# TESSERA README Feature Imports

## Purpose

This file records the README features imported from ASF-R style loop documentation into Tessera.

| Source Feature | Tessera Import | Why It Matters |
|---|---|---|
| One-command full loop | `scripts/run-tessera-full-loop.ps1` | Anyone can run the system without reconstructing commands. |
| UI starts before loop | Observer PowerShell opens before Worker completes | Human sees the loop while it is alive, not after it ends. |
| Final state printout | live `status.json` and `events.jsonl` | Operator can inspect phase, decision, certificate, and failures. |
| Wound / trace visibility | failure lessons registry + live phase board | Failures become visible records instead of hidden terminal noise. |
| Expected result block | Loopbook expected-result section | Users know what successful execution should look like. |
| Read-only UI law | Observer boundary section | Dashboard observes; it does not authorize or mutate. |
| Runtime geometry section | Operator loop chart | The loop has a stable public shape. |
| Quick start commands | README + README_90_SECONDS | New users can run, validate, and inspect quickly. |
| Non-claim lock | README / Loopbook / lessons boundary | Local diagnostics do not become inflated claims. |

## Tessera Compression

```text
ASF-R teaches: show the whole governed loop.
Hermes teaches: separate actor runtime from governance geometry.
Tessera compresses both into: Loopbook + dual-console PowerShell + failure lessons gate.
```