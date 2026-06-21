# Tessera Host Integrations

Tessera v0.3.3 includes two source-bound reference integrations.

## Agent CLI Mirror

Input contract:

- phase;
- state;
- timestamps and durations;
- process, memory, CPU, subprocess, and disk counters.

The adapter discards command strings, details, repository paths, mirror paths,
and raw outputs.

## Hermes Agent

Input contract:

- tool-call start and finish events;
- final message-stop events;
- gateway lifecycle notices;
- aggregate session counts, token counts, and end reason.

The adapter discards message text, tool names, previews, arguments, content,
platform identifiers, and user identifiers.

## Conformance

```powershell
python -m tessera host-integration-readiness `
  --root . `
  --hermes-root "C:\path\to\hermes-agent-evo"
```

Both integrations must:

- emit only allowlisted numeric and categorical metadata;
- produce the versioned five-feature session summary;
- reject unsupported records;
- trigger deterministic incident containment on observed failure;
- remain below the 10 ms adapter budget.

Passing conformance does not mean either integration is independently deployed
or production validated.
