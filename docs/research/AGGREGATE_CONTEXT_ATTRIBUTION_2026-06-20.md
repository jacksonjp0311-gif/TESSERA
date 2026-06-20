# Aggregate Context Attribution — EVO-024

## Sensor Contract

Fresh Agent CLI events added only:

- system CPU percentage
- available-memory ratio
- process count

The capture excludes process IDs, process names, command lines, paths, prompts,
and raw outputs.

## Method

Forty new clean validation sessions were split chronologically into 20
discovery and 20 validation sessions. A phase/context association required:

- absolute Spearman correlation of at least `0.4` in both halves
- the same correlation sign
- at least three robust tail observations in both halves

## Result

MIRROR latency associated reproducibly with CPU, memory availability, and
process count, but MIRROR had no robust tail observations.

REHYDRATE and GEOMETRY produced a small number of tail observations, but their
context associations were weak, changed sign, or lacked support. No association
passed every gate.

## Decision

Context-conditioned calibration is rejected. The existing session threshold
remains unchanged.

## Next Gate

Measure subprocess startup latency and aggregate I/O wait directly. These
sensors remain numeric and payload-free and are closer to the suspected
mechanism than broad host load.

## Claim Boundary

Aggregate resource association does not prove causality, natural failure
detection, production readiness, consciousness, or autonomous authority.
