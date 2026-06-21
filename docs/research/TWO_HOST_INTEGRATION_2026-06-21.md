# EVO-037 Two-Host Integration

## Target

Move beyond generic JSON compatibility and bind Tessera to two different agent
telemetry contracts:

1. Tessera Agent CLI Mirror phase/state process telemetry;
2. Hermes Agent typed gateway stream and session-summary telemetry.

## Privacy projections

Agent CLI retains numeric timing and resource counters plus phase/state labels.
It drops commands, details, paths, and raw output.

Hermes retains tool completion duration/status, lifecycle state, and aggregate
session/token/tool counts. It drops message content, tool names, previews,
arguments, platform identifiers, and user identifiers.

## Results

- 2 source-bound host integrations;
- 3 Agent CLI events and 4 Hermes events adapted;
- both emitted the frozen five-feature session contract;
- 0 denied payload leaks;
- 2/2 malformed record types rejected;
- observed host failure triggered incident-latched abstention and memory
  suppression;
- Agent CLI adapter latency: 0.094 ms;
- Hermes adapter latency: 0.047 ms;
- both below the 10 ms adapter budget.

Source bindings:

- Agent CLI Mirror commit `cc0d5ad`, source SHA-256
  `6e329d37e6f67ed5bf1b12b439e65eb510aee299257a4f6148a0374715120ae8`;
- Hermes Agent commit `27e379d`, source SHA-256
  `6daee540722e021c1988c6beceeb8d7778f4e6221af2f77731e29bf5bf561d4e`.

## Decision

Promote both adapters as reference integrations. Do not close the independent
host gate until they are installed, operated, and observed in separate host
deployments.
