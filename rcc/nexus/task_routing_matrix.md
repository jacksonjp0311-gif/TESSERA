# Task Routing Matrix

| Task | Start Here | Validate With |
|---|---|---|
| Runtime/model edit | `src/tessera/README.md` | `python -m unittest discover -s tests` |
| Theory/reference edit | `docs/theory/README.md` | `python scripts/validation/validate_architecture_contracts.py` |
| Alignment/RCC edit | `docs/alignment/README.md`, `rcc/nexus/README.md` | `python scripts/rcc/check_rcc_nexus.py` |
| README/public surface edit | `README.md`, `README_90_SECONDS.md` | RCC checker + architecture checker |
| Evidence/run artifact check | `outputs/README.md` | `python -m tessera validate --run outputs/runs/latest` |
| GitHub push prep | root README + all validators | wait for James authorization |
