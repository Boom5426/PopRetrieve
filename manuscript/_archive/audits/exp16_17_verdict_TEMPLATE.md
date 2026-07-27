<!-- TEMPLATE — filled programmatically by the exp16/17 verdict generator from FULL CSVs.
     Do not hand-edit numbers here; they are injected from:
       results/exp16_gate_diagnosis/gate_vs_true_divergence.csv
       results/exp16_gate_diagnosis/gate_variants_sweep.csv
       results/exp17_true_divergence_subset/divergence_stratified.csv
       results/exp17_true_divergence_subset/power_analysis.csv
-->
# exp16 / exp17 — Gate Diagnosis & True-Divergence Audit: Verdict

## Question
exp12's diagnostic gate labels a "DART_recommended" subset whose non-circular advantage is
no better than the non-recommended subset (+0.119 vs +0.122 energy-regret; MoA-nDCG −0.013).
This audit locates the lesion — gate calibration vs data/task layer — and re-tests, under
the two NON-CIRCULAR judge metrics only, whether any high-divergence subset shows a real
DART advantage.

Judge metrics (both non-circular, computed independently of any DART-aligned score):
- **minority_state_coverage** = (cos(P̄_selected, μ_minority) + 1)/2 — a MEAN-based cosine
  proxy; if anything it disadvantages DART (DART optimizes distributional distance, not
  mean-to-minority-mean cosine).
- **moa_ndcg** = binary-relevance nDCG@10 over MoA annotation (annotation used for
  evaluation only, never for scoring).

## Lesion localization
{LESION}

## Outcome (A / B / C)
{OUTCOME}

## Phase 1 — gate vs true divergence
{PHASE1}

## Phase 2 — gate-variant sweep (non-circular, leave-one-cell-line-out CV (all lines from SciPlex3; NOT cross-dataset), BH-corrected)
{PHASE2}

## Phase 3 — true-divergence stratification (Q2)
{PHASE3}

## Phase 3 — power analysis (Q3)
{POWER}

## Impact on the manuscript
{IMPACT}

## Retained null results
{NULLS}

---
*All verdicts from the FULL run. No energy-based / DART-aligned metric was used as a primary
judge. Multiple comparisons BH-corrected. "Trend" is never reported as "advantage".*
