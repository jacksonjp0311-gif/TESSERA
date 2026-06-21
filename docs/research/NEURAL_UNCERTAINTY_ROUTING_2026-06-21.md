# Neural Uncertainty Routing — EVO-032

## Question

Can neural state identify low-trust regions around the stable expert without
changing its forecast?

## Contract

Only target-free information available before the next session was allowed:

- reconstruction surprise
- latent drift
- field movement
- neural/expert disagreement

A recent-observation-jump heuristic served as the simple control. Validation
selected score and target coverage. Replay required at least 2% retained-risk
improvement, bounded coverage drift, and risk no worse than the simple router.
The final test remained untouched until replay passed.

## Result

Validation selected latent drift at `60%` target coverage. The simple control
selected recent observation jump at the same coverage and identical validation
risk.

Replay:

- full-coverage risk: `0.06570`
- neural retained risk: `0.06314`
- neural coverage: `0.65`
- simple retained risk: `0.06314`
- simple coverage: `0.65`

The replay gate passed.

Untouched final test:

- full-coverage risk: `0.03015`
- neural retained risk: `0.02818`
- neural coverage: `0.90`
- simple retained risk: `0.03144`
- simple coverage: `0.75`

Latent drift reduced risk by `6.53%` versus full coverage and by `10.37%`
versus the simple router, while retaining three additional sessions.

## Decision

Promote neural latent-drift abstention around the stable expert. Forecasts
remain unchanged.

This is Tessera's first supported natural-session neural authority: selective
trust routing, not prediction ownership.

## What Is Emerging

Tessera is separating cognition into roles:

- stable experts act;
- neural fields sense regime and uncertainty;
- replay controls whether either role gains authority;
- checkpoints provide transactional learning;
- authority collapses safely when evidence fails.

This resembles a governed metacognitive layer more than a monolithic neural
agent.

## Claim Boundary

Selective clean-session risk does not establish natural failure sensitivity,
task success, production readiness, consciousness, or autonomous authority.
