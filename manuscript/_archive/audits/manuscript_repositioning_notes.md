# Manuscript Repositioning Notes (v1 → v2)

This file records what changed between `manuscript_CRM_draft_v1.md` and
`manuscript_CRM_draft_v2_metric_circularity.md`, and why. It is the decision log
for the repositioning, so a co-author can see the reasoning without diffing prose.

---

## 1. The one-sentence shift

**v1 thesis (method-conditioned):**
> Information conditions determine when distributional retrieval improves ranking.

**v2 thesis (evaluation-conditioned):**
> Distributional retrieval can show large apparent gains under objective-aligned
> welfare proxies, but these gains vanish under oracle-independent criteria;
> information-condition diagnostics explain when distributional structure exists,
> but current gates do not yet establish therapeutic utility.

The center of gravity moves from *"when does DART help?"* to *"why do DART's
apparent gains depend on the metric class, and what does that reveal about
evaluation in the field?"* DART becomes the **instrument** that exposes the risk,
not the method being defended.

---

## 2. Why the shift is safer

A method-centered paper invites the lethal question: *"if DART does not improve
independent utility metrics, what is it useful for?"* — which turns the negative
results (exp09, exp12/exp13) into weaknesses. The evaluation-centered framing makes
those same negatives the **central evidence**: they are the demonstration that
objective-aligned metrics overstate gains. The liability becomes the contribution.

---

## 3. Positioning: old → new

| | v1 | v2 |
|---|---|---|
| what DART *is* | reliability-aware decision framework | distributional retrieval **probe** for evaluation sensitivity |
| headline | information-conditioned advantage | metric-dependent gains / evaluation circularity |
| negatives | "honest boundary" (defensive) | central falsification result (offensive) |
| prior work | mean/signature is the collapsed limit | + field-level audit: objective-aligned evaluation is a field-wide default |
| target venue | (methods) | Cell Reports Methods / PLOS Comp Biol / Bioinformatics — NOT Nature Methods |

---

## 4. Revised contribution list (6)

1. **Unified retrieval spectrum** — mean/CMap-cosine retrieval is the
   zero-variance collapsed member of the distributional family (positive
   theoretical anchor, metric-independent).
2. **Objective-aligned evaluation can inflate apparent distributional gains** —
   large Class A gains (energy proxy: +0.119 regret, p = 4.3 × 10⁻⁵⁶, 72% of 621
   queries), explicitly labeled as an energy-based proxy objective.
3. **Oracle-independent metrics collapse the apparent gains** — the central
   falsification: MoA-nDCG −0.013, minority coverage negligible, 0/37 real tasks
   DART-dominant, recommended vs non-recommended proxy gain +0.119 vs +0.122.
4. **Information condition explains when distributional scores have usable
   signal** — exp09 predictor collapse (subpop_var_ratio real 0.046 vs predicted
   0.009; diversity 0.158 vs 0.057; isotropy 0.959 vs 0.998).
5. **HIR-Bench as a controlled stress test, not a biological oracle** —
   observed/predicted_mean/predicted_structure regimes, analytical boundary
   α* = B/(A+B), FULL 13,440-cell grid, predictability AUC 0.645 (moderate).
6. **Exploratory biological signal** — response-divergent minority states enriched
   for resistance-associated melanoma programs (AXL/mesenchymal p = 0.003,
   IFN-response p = 1.9 × 10⁻⁶, antigen-presentation p = 0.04); explicitly
   hypothesis-generating, no survival/timecourse validation.

---

## 5. Result reorder (v2)

1. Mean-signature retrieval is a collapsed special case (unification; positive
   anchor independent of utility metrics).
2. Objective-aligned evaluation produces large apparent distributional gains
   (Class A positive; sets up the circularity question).
3. **Oracle-independent metrics collapse the apparent gains** (central
   methodological contribution — moved to the structural center of the paper).
4. Information condition explains why gains appear or disappear (mechanism).
5. HIR-Bench formalizes failure regimes but real-domain transfer is limited
   (controlled framework + honest limitation).
6. Exploratory resistance-associated divergence (future direction).

The key structural change from v1: Result 3 (the null) is now the **pivot** of the
paper, not a caveat appended after the positive.

---

## 6. Evidence updates folded in from the exp16/17 gate audit

After v1 was drafted, a dedicated gate audit (exp16 gate diagnosis + exp17
true-divergence subset, re-running exp12 FULL with a non-destructively added
`true_divergence` column) refined Claim 4. v2 uses these refined numbers:

- **Verdict changed:** v1 "conditional-go (metric-dependent)" → v2 **"B(−):
  statistically real but negligible."** In the highest-divergence stratum DART
  significantly exceeds mean retrieval on a non-circular metric, but the effect
  size is negligible (below a small-effect floor).
- **New, quotable finding:** the gate's `structure_reliability` axis is
  **anti-correlated** with true response divergence (Spearman ρ = −0.21,
  p = 3.8 × 10⁻⁹) — it moves opposite to the quantity it should track. The
  `preference_conflict` axis is only weakly aligned (ρ = +0.18, p = 3.7 × 10⁻⁷),
  and the binary recommendation label does not separate high- from low-divergence
  queries (Mann–Whitney p = 0.090). This is stronger, more specific evidence for
  the "current gates do not establish utility" claim than v1 had.
- **Lesion localization:** the deficit is in the data/task layer, not only the
  gate — stratifying directly by true divergence (bypassing the gate) still yields
  no material Class B advantage. The minority-coverage effect is real and
  divergence-monotone (median gap Q1 +0.0009 → Q4 +0.0018, all q ≈ 0) but
  practically negligible; MoA-nDCG is null at every stratum (Q4 q = 0.57, power
  0.06).

---

## 7. Language and structure guardrails applied in v2

- **HIR-Bench** described as constructive/synthetic with expected-by-design
  boundary; gate described as experimental and limited (never "diagnoses when DART
  should be used").
- **Gate** language: "correctly identifies mean-collapsed predicted responses as
  no-DART, but does not yet isolate oracle-independent DART gains in
  partial-observed real data."
- **DART** language: "exposes evaluation sensitivity," "probe for when
  distributional information is trustworthy," "improves objective-aligned retrieval
  metrics under response-available conditions," "does not yet establish
  oracle-independent therapeutic utility." No "improves drug ranking / better
  recommendations / predicts resistance / solves inverse design / universal."
- **Negative-claims box** embedded in the main text (Results, next to the central
  null), not the supplement.
- **exp09 and exp12/exp13 nulls in the main text**, adjacent to the energy-proxy
  positives — never report +0.119 without −0.013.
- **exp15 exploratory throughout**, always with the no-timecourse limitation.
- **Abstract** rewritten from the evaluation trap, ≤4 numeric anchors.
- **Methods** gains an explicit "Evaluation metric taxonomy and circularity audit"
  subsection.

---

## 8. Files produced by this writing phase

- `evaluation_circularity_audit.md`, `evaluation_metric_taxonomy.md`,
  `related_work_metric_audit_table.csv` — the mandatory field-level audit.
- `negative_claims_box.md` — the 7-item guardrail box (also in main text).
- `revised_title_options_metric_circularity.md` — 10 titles.
- `manuscript_CRM_draft_v2_metric_circularity.md` — the repositioned draft.
- `manuscript_claim_map_v2.md` — claim → evidence → wording map (updated numbers).
- `manuscript_repositioning_notes.md` — this file.
