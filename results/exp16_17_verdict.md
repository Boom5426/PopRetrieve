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
**Data/task layer (Phase 3), not (only) the gate.** The gate carries a weak but significant divergence signal, yet even stratifying directly by true divergence — bypassing the gate entirely — DART shows no MATERIAL non-circular advantage in the highest-divergence stratum. The signal is either absent or negligibly small in the expression data itself, so no gate re-calibration can recover a practical advantage. **Secondary gate design flaw:** structure_reliability correlates NEGATIVELY with true divergence (ρ=-0.21, p=3.79e-09) — it moves opposite to the quantity it should track, so the gate's reliability axis is mis-wired. This explains why the binary recommendation label fails to separate on divergence even though the conflict axis weakly does.

## Outcome (A / B / C)
**B(−) — statistically real but negligible.** In the highest-divergence stratum DART significantly exceeds mean retrieval on a non-circular metric, but the effect size is negligible (well below a small-effect floor). The mean→distribution mechanism is intact and divergence-monotone, yet its practical magnitude is tiny; on the annotation-recovery metric there is no advantage at all.

## Phase 1 — gate vs true divergence
Gate vs true divergence: **WEAKLY ALIGNED (continuous conflict signal correlates, ρ=+0.18, but the binary recommendation label does NOT separate high- from low-divergence queries)**.

- **recommended_vs_nonrecommended_divergence**: statistic=40663.000, p=0.090, n=621
- **spearman_preference_conflict_vs_divergence**: statistic=0.183, p=3.72e-07, n=765
- **spearman_structure_reliability_vs_divergence**: statistic=-0.211, p=3.79e-09, n=765

Interpretation: the binary DART_recommended label does NOT separate high- from low-divergence queries (Mann-Whitney p=0.090); the continuous preference_conflict signal is weakly but significantly correlated with true divergence (ρ=+0.18); structure_reliability is NEGATIVELY correlated with true divergence (ρ=-0.21) — a design flaw.

## Phase 2 — gate-variant sweep (non-circular, leave-one-cell-line-out CV (all lines from SciPlex3; NOT cross-dataset), BH-corrected)
No variant achieved cross-cell-line-consistent, BH-significant non-circular separation.

| conflict | reliability | metric | gap_of_gaps | p | q | xline_pos |
|---|---|---|---|---|---|---|
| min_pairwise_cos_neg | gate_structure_reliability | minority_state_coverage | 0.0006 | 0.167 | 0.187 | 1.0000 |
| true_divergence | gate_structure_reliability | minority_state_coverage | 0.0006 | 0.167 | 0.187 | 1.0000 |
| true_divergence | structure_x_conflict | minority_state_coverage | 0.0006 | 0.140 | 0.184 | 1.0000 |
| min_pairwise_cos_neg | structure_x_conflict | minority_state_coverage | 0.0006 | 0.140 | 0.184 | 1.0000 |
| min_pairwise_cos_neg | gate_structure_reliability | moa_ndcg | 0.0000 | 0.020 | 0.051 | 0.0000 |
| gate_preference_conflict | gate_structure_reliability | moa_ndcg | 0.0000 | 0.553 | 0.553 | 0.0000 |

## Phase 3 — true-divergence stratification (Q2)
| metric | stratum | div_med | n | median_gap | frac+ | p | q |
|---|---|---|---|---|---|---|---|
| minority_state_coverage | Q1 | 1.3354 | 192 | 9.24e-04 | 0.5469 | 0.0000 | 6.14e-07 |
| minority_state_coverage | Q2 | 1.6210 | 191 | 0.002 | 0.6911 | 0.0000 | 3.84e-14 |
| minority_state_coverage | Q3 | 1.6935 | 191 | 0.002 | 0.7016 | 0.0000 | 1.27e-14 |
| minority_state_coverage | Q4 | 1.7594 | 191 | 0.002 | 0.7120 | 0.0000 | 1.27e-14 |
| moa_ndcg | Q1 | 1.3354 | 166 | -3.00e-02 | 0.2892 | 0.0000 | 5.79e-05 |
| moa_ndcg | Q2 | 1.6210 | 150 | 0.00e+00 | 0.3667 | 0.0366 | 0.073 |
| moa_ndcg | Q3 | 1.6935 | 141 | 0.00e+00 | 0.3404 | 0.5324 | 0.566 |
| moa_ndcg | Q4 | 1.7594 | 143 | 0.00e+00 | 0.3776 | 0.5658 | 0.566 |

## Phase 3 — power analysis (Q3)
| metric | stratum | n | eff | sd | power | n@80% | sufficient |
|---|---|---|---|---|---|---|---|
| minority_state_coverage | Q4 | 191 | 0.006 | 0.013 | 0.9999 | 45.4585 | True |
| moa_ndcg | Q4 | 143 | 0.003 | 0.163 | 0.0562 | 20844.3170 | False |

## Impact on the manuscript
Sharpens Claim 4 without overturning it. The mean→distribution advantage is (a) real and divergence-monotone on the coverage proxy — DART's sensitivity to response divergence is mechanistically confirmed — but (b) negligibly small in magnitude and (c) entirely absent on annotation-recovery (moa_ndcg), where the study is orders-of-magnitude underpowered. Report the monotone coverage trend WITH its effect size and the moa_ndcg null side-by-side. Do NOT upgrade to a practical advantage. Claim 4 stays 'metric-dependent'; add: the direction of the effect tracks true divergence exactly as the theory predicts, but its size does not reach practical relevance in expression space.

## Retained null results
- [moa_ndcg] Q1 (div~1.34): median_gap=-0.0300, p=1.45e-05, q=5.79e-05 — no significant advantage.
- [moa_ndcg] Q2 (div~1.62): median_gap=+0.0000, p=0.037, q=0.073 — no significant advantage.
- [moa_ndcg] Q3 (div~1.69): median_gap=+0.0000, p=0.532, q=0.566 — no significant advantage.
- [moa_ndcg] Q4 (div~1.76): median_gap=+0.0000, p=0.566, q=0.566 — no significant advantage.

---
*All verdicts from the FULL run. No energy-based / DART-aligned metric was used as a primary
judge. Multiple comparisons BH-corrected. "Trend" is never reported as "advantage".*
