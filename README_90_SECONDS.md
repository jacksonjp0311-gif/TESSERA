# Tessera in 90 Seconds

Tessera is a sparse compressive memory engine with RCC Nexus navigation and a Loopbook-gated dual-console operator mode.

Canonical full loop:

```powershell
cd "C:\Users\jacks\OneDrive\Desktop\Tessera"
.\scripts\run-tessera-full-loop.ps1
```

This opens:

```text
Observer PowerShell = read-only human interface
Worker PowerShell   = local code runner
```

Core loop:

```text
rehydrate -> loopbook -> launch -> observe -> worker -> check -> run -> validate -> ledger -> push -> root
```

Gate rule: if feature surfaces change, sync and validate `docs/loop/TESSERA_LOOPBOOK.md` before promotion.

Claim boundary: Tessera v0.2.6 improves operator-visible loop control and validation routing. It does not prove real telemetry transfer, production readiness, safety, AGI, consciousness, or universal anomaly-detection superiority.