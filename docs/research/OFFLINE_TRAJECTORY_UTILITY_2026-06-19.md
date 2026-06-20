# Offline Agent-Trajectory Utility — EVO-015

## Scope

Exercise the EVO-013 typed trajectory adapters through an offline benchmark
against non-neural controls. This is a synthetic utility diagnostic, not live
agent integration.

## Policies

- recency heuristic;
- robust summary heuristic;
- Tessera bounded plugin.

Twelve deterministic mixed tool/test trajectories were evaluated, half with
degraded endings.

## Results

| Metric | Recency | Summary | Tessera |
|---|---:|---:|---:|
| failure recall | 1.00000 | 0.66667 | 1.00000 |
| false intervention | 0.00000 | 0.00000 | 0.00000 |
| safe-memory recall | 1.00000 | 1.00000 | 0.50000 |
| unsafe-memory rate | 0.00000 | 0.33333 | 0.00000 |
| decision accuracy | 1.00000 | 0.83333 | 1.00000 |
| mean latency | 0.07 ms | 0.26 ms | 158.73 ms |

Tessera matched recency and rejected unsafe memories, but retained only half of
safe memories and incurred much greater latency. Because the final degraded
event exposed an explicit error, the recency control saturated the benchmark.
No superiority claim is supported.

## Repair-Gate Correction

The EVO-013 repair ablation originally selected winners using prediction loss
alone, allowing wrong-target repair to win with zero replay support. EVO-015
requires prediction parity, replay at least `0.60`, recall at least `0.65`, and
false-memory rate at most `0.05`. Under that bundle,
`targeted_shadow_repair` is the only eligible arm.

## Next Operation

Run a precursor-only trajectory benchmark without explicit final error flags,
then evaluate captured local agent trajectories after schema and privacy review.

## Non-Claim Boundary

Synthetic trajectory accuracy is not live agent utility, production readiness,
safe autonomous memory, consciousness, or tool authority.
