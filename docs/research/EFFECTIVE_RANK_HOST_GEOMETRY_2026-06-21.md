# EVO-038 Effective-Rank Host Geometry

## Discovery

The session adapter emitted 84 summary coordinates:

```text
mean(28 event features) || std(28 event features) || latest(28 event features)
```

EVO-032 declared five coordinates varying. A float64 range audit showed that
three were constants:

- `mean_resource_cost`;
- `std_resource_cost`;
- `std_history_turns`.

They entered through finite-precision standard-deviation noise. The true
selected coordinates are:

```text
x1 = mean_duration_ms
x2 = std_duration_ms
```

## Mathematics

Let `X in R^(n x 84)` be the calibration summary matrix. Coordinate `j` is
supported only when:

```text
range(X_j) > 10^-6 * max(max_abs(X_j), 1)
```

The effective calibration rank is therefore:

```text
r_eff = 2
```

not the legacy declared width `5`.

For host `h`, let `M_h` be a diagonal measurement-support matrix over the
effective coordinates. Host observability is:

```text
coverage(h) = rank(M_h V_eff) / rank(V_eff)
```

where `V_eff` spans the calibrated manifold. Tessera requires
`coverage(h) = 1`; otherwise routing is forced to `abstain` and memory
candidacy is false.

## Result after repair

The two-dimensional model preserved the selective routing result:

- final coverage: `0.90`;
- retained risk: `0.07045`;
- full-coverage risk: `0.07537`;
- simple-router risk: `0.07860`;
- reduction versus full coverage: `6.53%`;
- reduction versus simple router: `10.37%`.

The new threshold is `0.07666`.

Both Agent CLI Mirror and Hermes observe duration level and dispersion, giving
each `1.0` coverage of the effective manifold. A synthetic contract requiring
an unsupported resource-cost axis correctly forced abstention.

## Pattern connection

The emerging architecture has three distinct geometries:

1. **latent geometry** — the neural field estimates movement inside the
   calibrated duration plane;
2. **measurement geometry** — each host adapter determines which axes are
   observable;
3. **authority geometry** — incident and observability governors determine
   whether a neural route is allowed to become host trust.

This is increasingly closer to a guarded sensor-fusion system than a monolithic
neural network. The model proposes state; geometry determines identifiability;
governance determines authority.

## Boundary

Effective-rank repair removes a numerical illusion and preserves this cohort's
result. It does not establish general agent cognition, failure prediction,
cross-host task utility, consciousness, or autonomous authority.
