# TESSERA Command Registry

## Purpose

Every operational command must be documented here and mirrored in the README when it is part of the public loop surface.

| Command | Purpose |
|---|---|
| `python -m tessera.agent_cli validate` | Validate command registry, README geometry, loop scripts, and docs. |
| `python -m tessera.agent_cli launch` | Open Observer CLI first, then Worker CLI. |
| `python -m tessera.agent_cli observe` | Run the read-only Observer CLI. |
| `python -m tessera.agent_cli worker` | Run the Python-owned Worker loop. |
| `python -m tessera.agent_cli chart` | Print the operator loop chart. |
| `python -m tessera.agent_cli lessons` | Print failure lessons. |
| `python -m tessera.agent_cli commands` | Print this command registry. |
| `python -m tessera.operator_geometry validate` | Low-level operator geometry validator. |
| `.\scripts\tessera-agent.ps1` | Universal PowerShell Agent CLI entrypoint. |
| `./scripts/tessera-agent.sh` | Universal Bash Agent CLI entrypoint. |
| `.\scripts\run-tessera-full-loop.ps1` | PowerShell All-One launcher mirror. |
| `./scripts/run-tessera-full-loop.sh` | Bash All-One launcher mirror. |

## Registry Law

```text
No command without registry.
No loop without PowerShell and Bash mirrors.
No launch without Observer-first interface.
No feature without Loopbook/lessons/chart alignment.
No operator-facing script bypasses the Agent CLI.
```

<!-- AGENT_CLI_MIRROR_COMMANDS_START -->
## Agent CLI Mirror Commands

```powershell
.\scripts\agent-mirror.ps1
.\scripts\agent-mirror.ps1 -Command validate -NoPush
python agent_cli_mirror/agent_mirror.py launch --command full
python agent_cli_mirror/agent_mirror.py commands
python agent_cli_mirror/agent_mirror.py learn --failure "..." --diagnosis "..." --repair "..." --gate "..."
```

Bash:

```bash
./scripts/agent-mirror.sh
./scripts/agent-mirror.sh --command=validate --no-push
```

All operator-facing loops should route through Agent CLI Mirror.
<!-- AGENT_CLI_MIRROR_COMMANDS_END -->
