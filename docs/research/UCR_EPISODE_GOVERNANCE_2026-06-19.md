# UCR Episode Governance — EVO-007

## Specification

Test whether causal event episodes and memory quarantine can convert the
confirmed UCR subsequence sensor into safer operational behavior.

## Preregistered pair

- Discovery: `176_UCR_Anomaly_insectEPG4_1300_6508_6558.txt`
- Untouched confirmation:
  `177_UCR_Anomaly_insectEPG5_3200_8500_8501.txt`

The window-24 discord sensor and 12-sample evidence hold were frozen from
EVO-006. Confirmation used a 12-sample post-warning memory quarantine.

## Discovery

- AUC: `0.976288`
- recall: `1.0`
- replay coverage: `0.747010`
- false-memory rate: `0.0`
- governance harm: `0.054573`

The detector already handled the 51-sample anomaly before quarantine.

## Untouched confirmation

The confirmation anomaly spans only two samples:

- AUC: `0.436749`
- recall: `0.0`
- replay coverage: `0.664225`
- false-memory rate: `1.0`
- governance harm: `0.685092`

No warning opened, so the episode quarantine could not activate.

## Learned boundary

```text
sensor detects
-> episode opens
-> quarantine protects memory
```

The arrow cannot run backward. Governance cannot manufacture evidence for a
sensor-blind event.

TESSERA therefore needs a sensor router:

- point-scale surprise;
- subsequence shape discord;
- contextual relational deviation;
- shared episode and memory governance.

## Next experiment

Preregister duration-stratified UCR pairs. Freeze a point-scale sensor and a
subsequence sensor separately, route by declared scale metadata, and evaluate
the router on untouched series. Forecasting remains an independent blocked
gate.

## Claim Boundary

Episode governance was implemented, but universal UCR transfer was rejected.
No memory promotion, generalization, safety, consciousness, or autonomous
authority is claimed.
