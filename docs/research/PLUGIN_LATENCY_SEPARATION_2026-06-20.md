# Plugin Latency Separation — EVO-027

## Wound

EVO-026 contained plugin failures but measured approximately `1,115 ms` warm
p95 against a declared `250 ms` interactive budget.

Profiling showed that the supervised request path crossed the neural threshold
at eight events and fitted a new model before returning to the host.

## Architecture Change

EVO-027 separates synchronous inference from fitting:

- the supervised production path disables inline neural fitting by default
- bounded robust fallback inference remains synchronous
- once neural support is available, the packet explicitly reports
  `fast_path_shadow_training_required`
- direct research-mode `TesseraPlugin` instances retain the original neural
  path for experiments
- worker warmup is explicit so interpreter and dependency startup is outside
  interactive request latency

No unvalidated checkpoint is admitted to the fast path.

## Measurement

Twenty consecutive warm supervised requests were evaluated after explicit
worker warmup:

- success rate: `1.0`
- median latency: `1.57 ms`
- p95 latency: `3.11 ms`
- maximum latency: `5.10 ms`
- declared budget: `250 ms`
- fitting observed on host path: no
- crash and timeout containment: `1.0`
- unauthorized host mutations: `0`

The warm p95 improved by more than 99% from EVO-026 and passed the interactive
latency gate with substantial margin. Cold startup is environment-sensitive
and reached `13.54 s` in the final run, so host initialization must prewarm the
worker and expose readiness before accepting traffic.

## Decision

Promote the synchronous latency separation and interactive runtime candidate.
Do not promote the complete plugin to production candidate.

The neural path now needs an asynchronous shadow trainer, immutable checkpoint
format, replay validation, atomic admission, and rollback before neural output
can return to the production fast path.

## Claim Boundary

Low local latency does not prove agent utility, neural superiority, production
readiness, security, consciousness, or autonomous authority.
