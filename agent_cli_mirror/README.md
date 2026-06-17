# Agent CLI Mirror

Agent CLI Mirror is a transplantable operator substrate. It turns scripts into agent/API calls with a read-only Observer, a Worker, a command registry, live state, and a lessons ledger.

## Start

```powershell
.\scripts\agent-mirror.ps1
```

```bash
./scripts/agent-mirror.sh
```

## Transplant

Copy `agent_cli_mirror/` and the two wrapper scripts into another repository, edit `agent_cli_mirror/config/commands.json`, then run validation.