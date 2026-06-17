# TESSERA Failure Lessons

## Purpose

Failures are now first-class learning artifacts. Every repeat failure must become a lesson, and every lesson must become a gate or chart element.

| ID | Failure | Lesson | Gate |
|---|---|---|---|
| F001 | latest pointer published before runtime artifacts existed | Publish latest only after certificates, evidence, metrics, ledgers, and reports exist. | latest evidence validation |
| F002 | Windows symlink/copy latest directory removal failed | Use robust latest pointer removal for symlink, file, and directory cases. | paths utility test |
| F003 | Git command scanned C:\Users\jacks instead of Tessera root | Every Git call must be root-bound with git -C <repo-root>. | root-lock check |
| F004 | bundle folder was missing | Critical installers must be runnable from anywhere or paste-safe. | single-file bootstrap |
| F005 | top-level PowerShell param block failed when pasted | Installer scripts meant for pasting must avoid top-level param blocks. | paste-safe script convention |
| F006 | UTF-8 BOM broke JSON parsing | Write JSON and markdown UTF-8 without BOM before validators run. | encoding normalization |
| F007 | Unicode box drawing crashed Windows cp1252 console | Operator output must be ASCII-safe unless terminal encoding is proven UTF-8. | ASCII-safe display |
| F008 | README discipline drifted after new loop surfaces | README, Loopbook, AGENTS, and route docs must update together. | README discipline + loopbook gate |
| F009 | raw PowerShell scroll hid the agent-like operator state | Separate worker execution from human observer display. | observer/worker split |
| F010 | PowerShell accumulated too much loop logic | PowerShell should launch terminals only; Python should own loop logic. | Python loop kernel |

## Law

```text
Failure must become a lesson.
Lesson must become a chart.
Chart must become a gate.
Gate must run before promotion.
```
