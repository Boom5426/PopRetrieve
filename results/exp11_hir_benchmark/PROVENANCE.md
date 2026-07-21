# Which HIR-Bench grid produced which file

HIR-Bench has two layers with very different costs. The method-independent layer
(oracle labels, conflict features, observable features) runs on the FULL
13,440-instance grid in about an hour. The method-performance layer scores 9
retrieval methods against up to 100 candidates per instance with an O(n^2 d) population
distance, and does not finish on the FULL grid in a reasonable time.

They therefore come from different grids, and this file says which is which so that no
reader has to guess.

**FULL (13,440 instances = 672 configurations x 20 seeds):**
- `phase_grid_method_independent_FULL.csv`
- `phase_grid_predictability.csv`

**QUICK (144 instances = 48 configurations x 3 seeds):**
- `phase_grid_method_independent.csv`
- `phase_grid_method_performance.csv`
- `method_dominance.csv`
- `uncertainty_band.csv`
- `sanity_checks.csv`
- `theoretical_boundary.csv`

## Why the method-independent layer is here twice

`phase_grid_method_independent.csv` is the QUICK one **on purpose**. exp13's regime
boundary fit merges it with `phase_grid_method_performance.csv` on `(grid_id, seed)`,
and the method-performance layer only exists on the QUICK grid, so the two must come
from the same grid or the merge is empty. (It used to fail there with an unrelated
`KeyError` several lines later; `fit_hir_boundary` now checks and says so.)

`phase_grid_method_independent_FULL.csv` is the FULL layer, and it is what the
predictability model was actually fitted on. That is why the predictability numbers
are FULL while the file directly above them is QUICK.

**Consequence for the paper:** the regime boundary that exp13 projects onto real data
is fitted on 72 QUICK grid cells, not on 13,440 instances. The paper says so.

## Do not quote the QUICK numbers

At n=144 the Hit@1 granularity alone exceeds the effect sizes being compared.
Regenerate the FULL method-independent layer with:

    PYTHONPATH=src python src/experiments/exp11_hir_benchmark.py --skip-method-perf

Before 2026-07-12 this directory held only a QUICK run, whose predictability CSV
reported AUC 0.5 while the manuscript quoted 0.640 from a runner that lived outside
the repository, and nothing on disk recorded the discrepancy.
