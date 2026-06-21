# EVO-041 Exact Prefix-State Continuation

## Position

EVO-040 reused computation only when the complete normalized query was
identical. Appending one session still replayed every recurrent transition.

EVO-041 asks:

```text
If validated history is byte-identical and new rows are only appended, can
Tessera continue the recurrent computation exactly?
```

## Sufficient continuation state

The transition at time `t` depends on the current normalized observation,
field state, smoothed level, and previous latent code. Tessera therefore
retains:

```text
C_t = (field, level, previous code, last observation, metric rows)
```

For an appended observation:

```text
(row_t, C_(t+1)) = F(C_t, x_(t+1))
```

Continuation is permitted only when the incoming normalized history is
exactly equal to the cached prefix. Any changed value, shape, or order forces
full replay.

## Parity experiment

Twenty chronological prefixes, lengths 101 through 120, were evaluated by:

1. one persistent incremental Tessera instance;
2. a fresh full-replay instance for every prefix.

Promotion required equality of every final packet, every recurrent metric
row, every trust route, and every memory decision.

## Result

| Metric | Result |
|---|---:|
| Prefixes compared | 20 |
| Exact packet parity | 100% |
| Exact metric-row parity | 100% |
| Prefix extensions | 19 |
| Initial full replays | 1 |
| Incremental p95 | 1.60 ms |
| Full-replay p95 | 77.23 ms |
| p95 speedup | 48.32x |
| Historical-prefix mutation | full replay |

The first production-candidate diagnostic reached changed-prefix warm p95 of
`9.53 ms` while retaining 100% route parity.

## Emerging rule

```text
Identity may be reused.
Validated history may be extended.
Changed history must be replayed.
```

This creates a computational geometry:

```text
state identity  -> exact packet reuse
prefix identity -> exact recurrent continuation
prefix mismatch -> full reconstruction
```

Tessera is moving toward proof-carrying state: cached computation remains
valid only while its input lineage remains intact.

## Claim boundary

This proves exact parity on the current Python/PyTorch reference chronology.
It does not establish cross-platform floating-point identity, crash-persistent
state recovery, independent-host latency, consciousness, or autonomous
authority.
