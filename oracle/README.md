# oracle/ — reference implementation (provenance only)

This directory is a **read-only snapshot of the original GID-Flow implementation** that
first produced the results DART reports. It is kept for provenance and auditability and
is **isolated from the main line** — nothing in `../src` (the self-contained DART
package) imports from here.

- `src/gidflow/` — the original library (losses/distribution.py energy·MMD·sliced-W·
  coverage kernels, metrics/ranking.py, data loaders, and the exploratory SubFlow
  generative model in `models/`).
- `scripts/` — the original per-experiment scripts (`eval_controlled_mixture.py`,
  `eval_crossline_mixture.py`, `frangieh_*`, `cd34_*`, `verify_degenerate_limits.py`,
  the old PNG plotters, dataset-prep, and the demoted SubFlow training/scaling scripts).
- `configs/` — the original SubFlow / drug-rank configs.
- `FINDINGS.md` — the full honest experiment log (§1–§11); the reproduction targets in
  `../src/experiments/common.py` are transcribed from it.

**Why it's here and not deleted:** the DART package re-derives every headline number
self-contained (see `../results/all_existing_results_recomputed.csv`, 35/35 within
tolerance). This snapshot lets a reviewer diff the port against the source of truth.

**It is not wired to run standalone in this repo.** The oracle scripts expect the
original `data/`, `checkpoints/`, and `results/subflow/` layout of the GID-Flow monorepo
(SubFlow needs the git-ignored model checkpoints). To reproduce results here, use the
self-contained package instead:

```bash
bash scripts/run_all_core.sh     # from the repo root
```
