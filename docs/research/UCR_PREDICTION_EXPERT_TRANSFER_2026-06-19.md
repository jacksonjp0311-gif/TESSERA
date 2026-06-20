# UCR Validation-Selected Prediction Expert Transfer — EVO-011

## Goal

Close the remaining forecasting gate without changing Tessera's confirmed
selective anomaly router, episode governance, or independent memory normality.

## Protocol

- Discovery: `007_UCR_Anomaly_DISTORTEDCIMIS44AirTemperature3_4000_6520_6544.txt`
- Confirmation: `115_UCR_Anomaly_CIMIS44AirTemperature3_4000_6520_6544.txt`
- Candidate experts: persistence, five EWMA rates, and ridge autoregression
  with lags `2`, `4`, `8`, `16`, and `32`.
- Selection source: normal validation rows only.
- Final-test labels did not influence expert selection.

## Results

| Metric | Discovery | Confirmation |
|---|---:|---:|
| Selected expert | ridge AR lag 32 | ridge AR lag 32 |
| AUC | 0.96112 | 0.96081 |
| Replay coverage | 0.64084 | 0.61215 |
| Warning recall | 1.00000 | 1.00000 |
| False-memory rate | 0.00000 | 0.00000 |
| Selected prediction loss | 0.02036 | 0.01888 |
| Neural prediction loss | 0.43141 | 0.42327 |
| Best comparison baseline | 0.02468 | 0.02299 |

Both runs issued `T1_dataset_scoped` support.

## Finding

Prediction and anomaly sensing should be modular. The sparse neural field
continues to provide compression, reconstruction, latent dynamics, and
observability, while a validation-selected causal expert owns the forecasting
floor. The router and memory gates remain independently calibrated.

## Decision

UCR becomes Tessera's second supported dataset family after NAB. Phase 2
diversity is now `2 of 3`; this does not establish general transfer.

The same selection boundary is integrated into the local plugin runtime.
Inference packets and checkpoints expose the chosen causal expert, while
neural loss remains the anomaly-awareness channel and all host authority locks
remain active.

## Non-Claim Boundary

Two supported benchmark families do not prove production readiness, universal
generalization, safe autonomous memory, consciousness, or tool authority.
