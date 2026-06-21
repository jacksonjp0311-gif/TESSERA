# EVO-039 Manifold Drift Governance

## Finding

EVO-038 established that the calibrated 84-coordinate session summary has
effective coordinate support on:

```text
mean_duration_ms
std_duration_ms
```

EVO-039 looked inside that two-coordinate support. After robust normalization
and 90% radial trimming, the first principal direction explains `99.1429%` of
calibration variance. The calibrated duration plane is therefore not filled
uniformly; it contains an approximately one-dimensional filament.

In standardized coordinates its principal direction is:

```text
v = (0.721978, 0.691916)
```

Mean duration and duration dispersion move together. This relationship is a
new invariant that simple schema or feature-presence checks cannot protect.

## Geometry

For normalized session summaries `z`, the dominant calibrated direction is:

```text
v_1 = argmax_{||v||=1} Var(z v)
```

Window drift is decomposed into separate tests:

```text
support drift  = observed coordinates != calibrated coordinates
angle drift    = acos(|v_calibration dot v_window|)
location drift = ||median(z_window)||_2
scale drift    = std(z_window v_calibration) / calibrated scale
rank drift     = dimensions needed to explain 98% of variance
```

This decomposition matters because equal coordinate names can conceal a
different operating system. A host can continue emitting both duration fields
while their relationship rotates, translates, expands, or collapses.

## Chronological result

The untouched chronological windows remained inside the preregistered
reference envelope:

| Window | Principal angle | Center shift | Scale ratio | First-axis variance |
|---|---:|---:|---:|---:|
| Validation | 0.717 deg | 1.105 | 2.041 | 99.329% |
| Replay | 4.144 deg | 0.972 | 0.298 | 98.567% |
| Final | 0.495 deg | 0.908 | 0.237 | 98.523% |

All retain intrinsic rank one under the 98% cumulative-energy definition.

## Fault sensitivity

Four controlled mutations were rejected:

- constant duration dispersion: `support_collapse`
- activation of a previously constant coordinate: `support_expansion`
- reversal of the duration relationship: `manifold_rotation` at 84.083 deg
- eight-scale translation: `location_drift` with center shift 10.409

Every rejected audit forces `abstain` and suppresses memory candidacy.

During release certification, an unrelated long-running training process
exposed soak-tail sensitivity. EVO-039 therefore also binds the persistent
worker to one PyTorch CPU and interop thread by default. This is a containment
and latency-isolation measure; it does not change model outputs or relax the
250 ms release budget.

## Emerging pattern

Tessera now distinguishes four nested geometries:

1. ambient geometry: the serialized 84-coordinate container;
2. support geometry: the two coordinates that genuinely vary;
3. intrinsic geometry: the one-dimensional relation inside that support;
4. authority geometry: the actions permitted by observability and stability.

The important evolution is not greater model authority. It is a stronger
ability to recognize when previously earned authority no longer applies.

## Claim boundary

This result demonstrates reference-cohort stability and sensitivity to
controlled geometric faults. It does not establish stability on independently
operated hosts, causal incident prediction, production safety, consciousness,
or autonomous authority.
