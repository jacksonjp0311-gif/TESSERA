# UCR Subsequence Evolution — EVO-006

## Specification

Clean-lineage evaluation of Tessera on preregistered UCR 2021 anomaly series.

## Provenance

- DOI: `10.6084/m9.figshare.26410744.v1`
- License: CC BY 4.0
- Archive SHA-256:
  `3d80622074d07b7fe70e356aa093c59a8d31febd65a26099a31c60abd54f931a`
- Discovery: series `173`, insect EPG 1
- Untouched confirmation: series `174`, insect EPG 2

## Discovery

The pointwise Tessera sensor failed on discovery:

- AUC `0.56050`
- missed warnings `0.90323`
- false memories `0.80645`

Local derivative and range channels were insufficient. A z-normalized nearest
normal subsequence score was then evaluated on discovery windows. Window `24`
was selected on discovery and frozen.

## Confirmation

The frozen window reached AUC `0.67002` on untouched confirmation. Threshold
calibration could not satisfy replay and false-memory gates, so threshold
relaxation was rejected.

A causal 12-sample evidence hold was then introduced. It carries detected
subsequence evidence forward without accessing future observations.

Final untouched confirmation:

- AUC `0.87849`
- recall `0.80769`
- missed warnings `0.19231`
- normal replay coverage `0.58323`
- false-memory rate `0.15385`
- governance harm `0.14270`

## Conclusion

The shape-aware sensing hypothesis transferred across the two preregistered
series, but the operational transfer certificate did not pass. Forecasting was
also substantially below persistence.

Tessera therefore gains a confirmed subsequence sensor, not a supported UCR T1
result.

## Next evolution

Separate event detection from memory eligibility:

```text
subsequence discord
-> causal event episode
-> episode confidence and duration
-> normal-memory quarantine near event boundaries
```

The next experiment must improve replay and false-memory gates on a newly
preregistered UCR pair without changing window `24` or hold `12`.

## Claim Boundary

No UCR T1 transfer, archive-wide performance, safety, consciousness, memory
promotion, or autonomous authority is claimed.
