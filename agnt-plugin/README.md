# Tessera Neural Trust Layer — AGNT Plugin

## What It Does

Tessera is a **neural trust layer** that watches an agent's operational trajectory, compresses it into sparse neural state, and emits **trusted/abstain** decisions. It runs as a supervised read-only sidecar — it never mutates host memory, calls tools, or changes prompts.

## AGNT Integration

This plugin exposes 5 tools to AGNT agents:

| Tool | Purpose |
|---|---|
| `tessera-analyze` | Analyze agent session trajectory for drift and anomalies |
| `tessera-trust` | Get trust decision (trusted/abstain) for current session |
| `tessera-memory` | Propose memory candidates from session events |
| `tessera-health` | Get plugin health and runtime status |
| `tessera-status` | Get full status dashboard with metrics and evidence |

## Quick Start

```bash
# Install via AGNT CLI
agnt plugins install-file --name tessera-neural-sidecar --file tessera.agnt

# Or manually: AGNT dashboard → Plugins → Install from File → upload tessera.agnt
```

## Architecture

```
AGNT Agent Session
    ↓
AGNT Event Stream (agent events from chat, tools, execution)
    ↓
tessera-analyze → trajectory analysis + anomaly detection
tessera-trust → trusted/abstain decision
tessera-memory → memory proposals (host-gated)
tessera-plugin → PluginSupervisor (subprocess isolation)
    ↓
TESSERANet (GRU gating, multi-scale prediction)
    ↓
Neural Uncertainty Router → trust decision
    ↓
Atomic Capsule Store → durable state
```

## Source Code

Full source: https://github.com/jacksonjp0311-gif/TESSERA

## Version

v0.4.1 — EVO-045 — 162/162 tests passing
