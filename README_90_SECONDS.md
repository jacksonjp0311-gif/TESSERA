# Tessera in 90 Seconds

Tessera is a sparse compressive memory engine with RCC Nexus navigation and a local PowerShell operator shell.

Core loop:

```text
rehydrate -> shell -> compile -> check -> run -> validate -> ledger -> push -> root
```

Open the shell:

```powershell
cd "C:\Users\jacks\OneDrive\Desktop\Tessera"
.\scripts\tessera-shell.ps1
```

Run the full loop without reinstalling:

```powershell
.\scripts\run-tessera-full-loop.ps1
```

Claim boundary: Tessera v0.2.2 improves operator-visible loop control, validation routing, and push discipline. It does not prove real telemetry transfer, production readiness, safety, AGI, consciousness, or universal anomaly-detection superiority.