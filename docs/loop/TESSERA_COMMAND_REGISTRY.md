# TESSERA Command Registry

## Purpose

Every operational command must be documented here and mirrored in the README when it is part of the public loop surface.

| Command | Purpose |
|---|---|
| `python -m tessera.operator_geometry validate` | Validate command registry, README geometry, loop scripts, and docs. |
| `python -m tessera.operator_geometry launch` | Open Observer CLI first, then Worker CLI. |
| `python -m tessera.operator_geometry observe` | Run the read-only Observer CLI. |
| `python -m tessera.operator_geometry worker` | Run the Python-owned worker loop. |
| `python -m tessera.operator_geometry chart` | Print the operator loop chart. |
| `python -m tessera.operator_geometry lessons` | Print failure lessons. |
| `python -m tessera.operator_geometry commands` | Print this command registry. |
| `.\scripts\run-tessera-full-loop.ps1` | PowerShell All-One launcher mirror. |
| `./scripts/run-tessera-full-loop.sh` | Bash All-One launcher mirror. |

## Registry Law

```text
No command without registry.
No loop without PowerShell and Bash mirrors.
No launch without Observer-first interface.
No feature without Loopbook/lessons/chart alignment.
```

## Canonical All-One Entrypoints

PowerShell:

```powershell
cd "C:\Users\jacks\OneDrive\Desktop\Tessera"
.\scripts\run-tessera-full-loop.ps1
```

Bash:

```bash
cd "$HOME/OneDrive/Desktop/Tessera"
./scripts/run-tessera-full-loop.sh
```
