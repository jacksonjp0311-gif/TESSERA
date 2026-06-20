# Subprocess and I/O Mechanism Attribution — EVO-025

## Sensor Contract

Fresh Agent CLI completion events added only numeric, payload-free fields:

- subprocess spawn-call duration
- aggregate disk read and write byte deltas
- aggregate disk read and write time deltas

Process identity, command-line expansion, paths, prompts, and raw output remain
excluded from the trajectory feature surface.

## Method

Forty new clean validation sessions were split chronologically into 20
discovery and 20 validation sessions. A phase/field association required:

- absolute Spearman correlation of at least `0.4` in both halves
- the same correlation sign
- at least three robust tail observations in both halves

## Result

No one of the 15 phase/field pairs passed every preregistered gate.

MIRROR spawn duration correlated with ordinary latency in discovery
(`0.537`) but weakened in validation (`0.257`) and had only `0/1` robust tail
support. REHYDRATE had no robust tails. GEOMETRY had `2/0` tail support and no
stable mechanism association.

Aggregate disk-time counters were usually zero at this workflow scale. They
do not provide enough resolution to attribute the remaining latency tail.

## Decision

Mechanism-conditioned calibration is rejected. The frozen session threshold
remains unchanged.

## Next Gate

Measure privacy-safe child-process execution aggregates such as CPU time and
context switches, then collect a fresh cohort. These measurements should
remain numeric and must not expose process identity or payload.

## Claim Boundary

This result does not prove latency causality, natural failure sensitivity,
production readiness, consciousness, or autonomous authority.
