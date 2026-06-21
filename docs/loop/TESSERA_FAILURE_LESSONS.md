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
| F033 | controlled thresholds did not semantically transfer to full operator loops | require finite-sample support and matching privacy-safe workflow profiles; otherwise abstain | archived workflow-shadow gate |
| F034 | phase-local warning budgets compounded at the session level | calibrate the combined host decision with a split-conformal session score | natural clean session-shadow gate |
| F035 | clean-tail calibration required 200-250 ms injected delays for full response | report effect-size sensitivity separately and investigate operational modes before recalibration | preregistered perturbation ladder |
| F036 | two isolated slow sessions could be miscast as a second operating mode | require recurrent signatures in chronological discovery and validation; otherwise keep calibration frozen | tail-mode recurrence audit |
| F037 | broad host load correlated with routine latency but not the problematic tail | require tail-specific replicated association; instrument subprocess startup and I/O wait next | aggregate context attribution gate |
| F038 | spawn timing and aggregate disk I/O did not explain the remaining tail | use higher-resolution privacy-safe child execution aggregates and preserve calibration | mechanism attribution gate |
| F039 | permission declarations alone did not contain plugin crashes, hangs, or lifecycle risk | enforce a supervised fail-closed subprocess boundary and retain latency as a production blocker | plugin readiness gate |
| F040 | synchronous model fitting drove warm plugin latency above one second | separate fast inference from shadow learning and require replay-gated checkpoint admission | latency separation gate |
| F041 | asynchronous learning without transactional admission could replace live state unsafely | require immutable candidates, replay gates, atomic activation, and rollback | checkpoint lifecycle gate |
| F042 | controlled neural checkpoint success could be mistaken for natural agent utility | separate integration proof from chronological natural utility against matched controls | neural checkpoint gate |
| F043 | the natural checkpoint beat persistence but lost to stable EWMA and failed replay consistency | preserve stable expert ownership and test only bounded neural residual authority | natural checkpoint utility gate |
| F044 | every nonzero bounded neural correction worsened validation loss | collapse authority to zero and test neural uncertainty routing instead of forecast mutation | bounded residual gate |
| F045 | neural state was unhelpful as a correction but useful for identifying low-trust forecast regions | grant selective routing authority independently from prediction authority | neural uncertainty router gate |
| F046 | an offline session router integrated mechanically but its semantic feature space did not automatically transfer to host events | version and validate the host session-summary adapter separately | runtime uncertainty integration gate |

## Lessons Law

```text
Failure must become a lesson.
Lesson must become a chart.
Chart must become a gate.
Gate must run before promotion.
```
