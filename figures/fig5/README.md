> ⚠️ **SUPERSEDED IN PART, 2026-07-12.** This document predates an audit that retracted
> several numbers as artifacts of our own code, including the "5.1x structure collapse", the
> hand-entered divergence-gate positions (CD34+ was 0.95; it measures 0.186), the MoA-nDCG
> statistics computed over 165 undefined sentinel values, and the Class A/B contrast that
> compared two different scorers. **Read [CORRECTIONS.md](../../CORRECTIONS.md) before using any
> number below.** Where this file and CORRECTIONS.md disagree, CORRECTIONS.md is right.
# Figure 5: HIR-Bench formalizes when distributional retrieval can and cannot help

One-line message: a controlled heterogeneous-retrieval benchmark (HIR-Bench) with an ANALYTIC
flip boundary alpha* = B/(A+B) separating "mean-sufficient" from "structure-matters" regimes, and a
leakage-safe test showing failure is predictable from observable features (AUC (see results/exp11_hir_benchmark/phase_grid_predictability.csv)). This is the
theory figure that bounds the whole claim.

## Panels

| Panel | Message | Source | Status |
|-------|---------|--------|--------|
| a | Generative model: query = majority(1-alpha) + minority(alpha), welfare A vs B, flip when alpha>alpha* | schematic | done |
| b | Analytic boundary alpha* = B/(A+B); decision regions (mean-sufficient vs structure-matters) | closed form | done |
| c | energy-minus-mean Hit@1 across (alpha, conflict) grid; DART advantage concentrates at high conflict/alpha | exp11 phase_diagram_source | done |
| d | Boundary margin: observed vs analytic prediction, mean vs worst welfare | theoretical_boundary | done |
| e | Benchmark sanity checks (no-conflict flip rate, boundary margin, predicted=mean identity) all PASS | sanity_checks | done |
| f | Failure predictability ROC: AUC (see results/exp11_hir_benchmark/phase_grid_predictability.csv) on FULL 13,440-instance grid (benchmark instances, NOT biological cells), leave-one-grid-out logistic regression | exp11_lean (see note) | gated on server run |

## 6f provenance note (important)
The manuscript cites the AUC recorded in results/exp11_hir_benchmark/phase_grid_predictability.csv from the FULL 13,440-cell run, NOT the on-disk QUICK 144-cell
backup (AUC 0.5, n_pos=48/n_neg=96). The FULL number is reproduced by a LEAN method-independent-only
runner (results/_audit/fig5f_roc_lean.py): it regenerates the identical 13,440-instance grid (benchmark instances, NOT biological cells) with the same
seeds and computes the 4 disagreement features + oracle_flip_risk, then runs the exact
leave-one-grid_id-out logistic regression from src/benchmarks/predictability.py. It SKIPS the
per-method retrieval-scoring loop (energy/MMD/sliced-W across every drug), which 6f does not use and
which was the sole reason the naive full rerun took ~50 min. The lean grid is bit-identical on the
method-independent columns because generate_hir_cell(seed=seed) is deterministic. Source data:
results/_audit/exp11_lean/fig5f_roc_curve.csv + fig5f_roc_summary.json.

## Files
- fig5a.py ... fig5f.py, fig5_assemble.py, fig5_hir_bench.{png,pdf}
