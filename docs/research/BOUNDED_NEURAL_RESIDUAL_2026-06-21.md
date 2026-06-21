# Bounded Neural Residual — EVO-031

## Question

Can the neural field improve the validation-selected stable expert through a
small clipped correction without acquiring independent prediction authority?

## Contract

EWMA remained the prediction owner. Candidate neural gains were:

- `0.0`
- `0.05`
- `0.10`
- `0.20`

Corrections were clipped to `0.10`, `0.25`, or `0.50` times the training
innovation scale. Validation selected the candidate before replay. Promotion
required nonzero authority, at least 1% replay improvement, and a 60% row win
rate. Failure collapsed deployed gain to zero before final-test inspection.

## Result

Validation selected gain `0.0`. Every nonzero residual increased validation
loss:

- stable expert: `1.75345`
- gain `0.05`: `1.75977`
- gain `0.10`: at least `1.76591`
- gain `0.20`: at least `1.77393`

The replay gate therefore failed automatically:

- stable replay loss: `0.06570`
- deployed residual loss: `0.06570`
- deployed gain: `0.0`

Final-test loss was unchanged at `0.03015`; the stable expert was protected.

## Decision

Reject neural residual authority. Preserve stable expert prediction ownership.

The neural correction direction is not useful on this natural workflow. The
next neural role should be uncertainty estimation, profile routing, or
abstention around the stable expert—not direct forecast mutation.

## Claim Boundary

Authority collapse proves local gate behavior only. It does not prove natural
failure sensitivity, task utility, production readiness, consciousness, or
autonomous authority.
