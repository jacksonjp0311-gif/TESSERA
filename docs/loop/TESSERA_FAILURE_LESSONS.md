# TESSERA Failure Lessons Chart

## Purpose

Failure is a learning artifact only when it becomes a named lesson, a chart entry, and a validation gate.

| ID | Failure / Wound | Learned Lesson | Gate / Artifact |
|---:|---|---|---|
| F001 | latest pointer published before artifacts existed | publish latest only after evidence/certificate/metrics/reports exist | latest validation |
| F002 | Windows latest pointer removal failed | handle symlink/file/directory removal explicitly | paths utility |
| F003 | Git scanned user home | all Git calls use git -C <repo-root> | root-bound git |
| F004 | missing bundle folder | critical installers must be paste-safe or run-from-anywhere | single-file bootstrap |
| F005 | top-level PowerShell param failed when pasted | paste-safe scripts avoid top-level param blocks | paste-safe convention |
| F006 | UTF-8 BOM JSON failed | write JSON/MD as UTF-8 without BOM | encoding normalization |
| F007 | Unicode console crash | operator output is ASCII-safe by default | ASCII display |
| F008 | README drift | README/AGENTS/Loopbook/registry update together | README discipline |
| F009 | no Observer CLI at loop start | launch Observer before Worker | observer-first launch |
| F010 | PowerShell absorbed loop logic | Python owns loop logic; shell launches only | Python loop kernel |
| F011 | engine patch notes accumulated in repo root | release docs live under docs/releases/engine | root hygiene |
| F012 | alignment and geometry gap | command registry, loopbook, lessons, chart, and README must align | geometry gate |
| F013 | launcher passed surface checks with invalid Python syntax | compile executable Python entrypoints before promotion | Agent CLI Mirror syntax gate |
| F032 | safe precursor existed but general policies discarded phase history | phase-semantic signals require separately calibrated bounded specialists | phase-conditioned holdout gate |

## Lessons Law

```text
Failure must become a lesson.
Lesson must become a chart.
Chart must become a gate.
Gate must run before promotion.
```
