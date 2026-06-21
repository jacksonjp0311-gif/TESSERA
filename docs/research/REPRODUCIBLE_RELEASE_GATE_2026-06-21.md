# EVO-035 Reproducible Release Gate

## Question

Does the production-candidate behavior survive packaging, installation, and
execution outside the source checkout?

## Findings

The first audit found two release defects:

1. `tessera.__version__` reported `0.1.0` while project and plugin metadata
   reported `0.3.0`.
2. The developer Python environment contains unrelated packages with
   incompatible NumPy requirements.

EVO-035 aligned project, package, plugin, and wheel metadata at `0.3.1`.
Tessera's six declared direct dependencies satisfy their declared ranges. The
ambient conflicts are recorded but excluded from promotion because they belong
to unrelated packages.

## Final gate

The canonical command is:

```powershell
python -m tessera launch-readiness --root .
```

It runs certification sequentially:

1. semantic parity, latency, restart, rollback, failure isolation, and soak;
2. wheel build, metadata verification, RECORD verification, forbidden-path
   audit, isolated installation, packaged inference, and installed CLI smoke.

Results:

- 20/20 final route parity;
- 18 trusted and 2 abstained;
- 93.34 ms warm p95 against a 250 ms budget;
- 100-request soak with zero failures and 139.20 ms p99;
- 9/9 release checks passed;
- wheel `tessera-0.3.1-py3-none-any.whl`;
- 74 wheel files and zero forbidden paths;
- wheel SHA-256
  `009b4cc4436dc28cb7299a2a95cca8b7ef03fd973c98cfec9985ffcf2ccd78ba`.

## Decision

Promote Tessera to **repository launch candidate**. This closes source-to-wheel
reproducibility on the tested Windows environment. It does not close:

- untouched natural failure-and-recovery sensitivity;
- two independent external host integrations;
- independent vulnerability and security review;
- independent reproduction without inherited system packages;
- cross-platform subprocess certification.

No result grants host-memory writes, tools, prompt mutation, live model
replacement, or autonomous authority.
