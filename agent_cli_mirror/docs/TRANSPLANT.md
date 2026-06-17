# Transplant Guide

`agent_cli_mirror/` is intentionally portable.

## Copy Set

```text
agent_cli_mirror/
scripts/agent-mirror.ps1
scripts/agent-mirror.sh
scripts/validation/validate_agent_cli_mirror.py
```

## Adaptation

Edit:

```text
agent_cli_mirror/config/commands.json
```

Then validate:

```bash
python agent_cli_mirror/agent_mirror.py validate
```