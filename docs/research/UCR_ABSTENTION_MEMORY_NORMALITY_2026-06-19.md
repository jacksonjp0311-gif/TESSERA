# UCR Abstention and Independent Memory Normality — EVO-009

## Hypothesis

A confidence-aware `point | subsequence | abstain` router plus a separately
calibrated joint-normality memory gate should preserve specialist evidence and
reduce false-memory contamination on fresh UCR streams.

## Preregistered Series

| Role | Point-scale | Subsequence-scale |
|---|---|---|
| Discovery | `159_UCR_Anomaly_TkeepSecondMARS_3500_9330_9340.txt` | `154_UCR_Anomaly_PowerDemand3_16000_23405_23477.txt` |
| Confirmation | `250_UCR_Anomaly_weallwalk_2951_7290_7296.txt` | `155_UCR_Anomaly_PowerDemand4_18000_24005_24077.txt` |

The files were selected from filename metadata only, before outcome scoring.

## Frozen Mechanism

- normal-validation-only point and subsequence scaling;
- explicit specialist activation and disagreement margin;
- `point`, `subsequence`, or `abstain` route;
- conservative abstain episode hold;
- joint point/subsequence normality distance for memory eligibility;
- no final-test tuning.

## Confirmation Results

| Metric | Point confirmation | Shape confirmation |
|---|---:|---:|
| Routed/max-fusion AUC | 0.92274 | 0.96784 |
| Best specialist AUC | 0.92903 | 0.98863 |
| Warning recall | 0.85714 | 0.98630 |
| False-memory rate | 0.00000 | 0.00000 |
| Normal replay coverage | 0.58078 | 0.56556 |
| Abstention rate | 0.81746 | 0.82531 |
| Forecasting baseline gap | -0.51741 | -0.42784 |

## Finding

Independent memory normality transferred across both confirmations and removed
anomaly-memory contamination. The router also abstained heavily on normal
states and less often on anomalies.

However, abstention did not yet control score fusion: `anomaly_score` remained
the maximum normalized specialist score. Consequently, max fusion still
reduced both specialist AUCs, and replay coverage remained below the `0.60`
gate. Forecasting also remained independently below baseline.

## Decision

EVO-009 confirms the independent memory-normality branch, but does not confirm
the detector router or UCR T1 transfer. The next router must make abstention
operational in score fusion, preserve specialist evidence under a declared
coverage budget, and keep prediction repair as a separate workstream.

## Non-Claim Boundary

Zero false memories on two confirmation series does not prove general memory
safety, transfer, production readiness, consciousness, or autonomous authority.
