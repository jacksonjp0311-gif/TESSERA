# TESSERA Agent CLI Contract

## Purpose

Tessera uses a Hermes-style agent interface. Every operator-facing script or loop must enter through the Agent CLI, which opens the Observer before the Worker.

## Agent Interface Law

```text
No operator-facing script without Agent CLI entry.
No loop without Observer-first launch.
No Worker without live state emission.
No internal validator may spawn another Observer.
No shell owns the loop; shells launch Python.
```

## Precision

Operator-facing entrypoints include PowerShell launchers, Bash launchers, and direct public loop commands. Internal validators and library modules do not open new windows because they run inside the Worker and report into the existing Observer state.

## Canonical Entrypoints

PowerShell:

```powershell
cd "C:\Users\jacks\OneDrive\Desktop\Tessera"
.\scripts\tessera-agent.ps1
```

Bash:

```bash
cd "$HOME/OneDrive/Desktop/Tessera"
./scripts/tessera-agent.sh
```

Direct Python:

```powershell
python -m tessera.agent_cli launch
```

## What Opens

```text
Observer CLI opens first.
Worker CLI opens second.
```

The Observer is read-only. The Worker runs checks, runtime, validation, ledger, and push routing.