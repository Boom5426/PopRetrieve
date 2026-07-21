# Field-Level Evaluation-Circularity Audit

**Role.** This audit is a mandatory pre-writing deliverable for the repositioned
DART manuscript. Its job is to establish that *objective-aligned evaluation* is a
broad, structural risk across inverse retrieval and perturbation modeling — **not
a DART-specific artifact**. Without it, the manuscript's metric-circularity thesis
is open to the fatal reviewer objection:

> "This is not a field-level evaluation problem. It is just your own DART
> evaluation being circular."

The audit answers that objection with a survey (see
`related_work_metric_audit_table.csv`) organized by the metric taxonomy (see
`evaluation_metric_taxonomy.md`).

---

## 1. The claim this audit supports

> DART exposes a general evaluation risk: methods can perform strongly on metrics
> structurally aligned with their scoring objective, while independent utility
> criteria may not support the same conclusion.

This sentence is the bridge that converts DART's own metric dependence from a
liability into a field-level methodological contribution. The audit's purpose is
to make that sentence defensible, not to indict any prior work.

---

## 2. What the audit found

Across seven method families spanning three modalities — signature/connectivity
retrieval, expression prediction, and graph/target inverse design — the metrics
most commonly reported are **Class A (objective-aligned)** or **Class B
(task-proximal)**. Class C (oracle-independent utility) metrics are rare in
computational evaluations of these methods, because they require external
functional experiments (dose-response, survival, clone expansion) that are
outside the typical computational benchmark.

| modality | representative families (refs) | dominant reported metric class |
|---|---|---|
| signature / connectivity retrieval | CMap/L1000 (Lamb 2006; Subramanian 2017), single-cell signature / scPerturb E-distance (Peidli 2024) | A (connectivity/cosine/E-distance), some B (DEG) |
| distributional retrieval | DART (this work) | A (energy proxy), reported here also against B |
| expression prediction | scGen (Lotfollahi 2019), CPA (Lotfollahi 2023), chemCPA (Hetzel 2022), virtual-cell FMs (Cui 2024; Hao 2024; Theodoris 2023) | A (reconstruction), some B (DEG) |
| graph / target inverse design | network-proximity (Guney 2016), GEARS (Roohani 2024), PDGrapher (Gonzalez 2025) | A (graph proximity / target overlap) |

Full citations with verified DOIs are in `related_work_metric_audit_references.md`;
the per-family metric-class assignments are itemized in
`related_work_metric_audit_table.csv`.

The pattern is consistent and modality-independent: **the headline metric is
usually a restatement of the method's own objective.** This is entirely legitimate
for testing objective fidelity — for instance, the scPerturb framework (Peidli et
al. 2024) formalizes the energy distance (E-distance) precisely as a principled
population-level effect metric, and DART's own energy score belongs to the same
family. It becomes a problem only when a strong Class A score is *read as*
independent therapeutic or biological utility — a reading the metric does not
license.

---

## 3. Why this is a fidelity-vs-utility distinction, not an accusation

The audit deliberately does **not** claim any prior method is wrong, invalid, or
"doing circular evaluation." The correct framing, used throughout the manuscript:

- Objective-aligned metrics **answer a narrower question**: does the method
  compute its objective faithfully, and is that objective discriminative on the
  data?
- They **test objective fidelity, not independent utility.**
- DART **makes this distinction explicit** by reporting a Class A positive and a
  Class B null side by side, rather than reporting either alone.

Prohibited framings (never used): "prior work is invalid," "these methods are
wrong," "everyone is doing circular evaluation." Required framing: "these metrics
answer a narrower question; they test objective fidelity, not independent utility;
DART makes this distinction explicit."

---

## 4. DART as the instrument that exposes the risk

DART is uniquely suited to make the field-level point concrete because it can be
scored *both* ways on the same tasks:

1. **Class A (its own objective).** On observed heterogeneous populations,
   distributional energy retrieval reaches Hit@1 0.837 versus 0.389 for
   mean/CMap; in the partial-observed audit its energy-welfare regret reduction is
   +0.119 (paired Wilcoxon p = 4.3 × 10⁻⁵⁶, 72% of 621 recommended queries). By
   the standard of a Class A metric, this is a large, highly significant gain.

2. **Class B (task-proximal, near-independent).** On the *same* recommended
   queries, mechanism-of-action recovery nDCG is −0.013 (DART slightly *loses*),
   minority-state coverage gain is negligible (median +0.0009 → +0.0018 across
   true-divergence strata, statistically significant but far below any practical
   effect floor), and projecting real datasets onto the regime plane yields 0 of
   37 tasks DART-dominant under the non-circular criterion.

3. **The gate does not rescue the gap.** A diagnostic gate built to concentrate
   the advantage does not: median regret reduction is +0.119 on the recommended
   subset versus +0.122 on the non-recommended subset. A direct audit of the gate
   (exp16/17) shows its structure-reliability axis is in fact *anti-correlated*
   with true response divergence (Spearman ρ = −0.21, p = 3.8 × 10⁻⁹) — it moves
   opposite to the quantity it should track — while the preference-conflict axis
   is only weakly aligned (ρ = +0.18, p = 3.7 × 10⁻⁷). Even stratifying directly
   by true divergence and bypassing the gate, the highest-divergence stratum shows
   no *material* Class B advantage.

The A-vs-B contrast is the entire point. The same method, on the same data, is
"far ahead" or "no better" depending only on which metric class judges it. That is
the evaluation risk, demonstrated rather than asserted.

---

## 5. Independent corroboration in the recent literature

The audit's central claims are not unique to DART; each is independently
documented in the recent benchmarking literature, which is what makes this a
field-level risk rather than a DART-specific artifact.

- **Objective-aligned gains do not survive fair baselines.** Ahlmann-Eltze, Huber
  & Anders (2025, *Nature Methods*) compared five foundation models and two other
  deep-learning models against deliberately simple baselines for single- and
  double-perturbation prediction and found that **none outperformed the
  baselines** — a peer-reviewed, independent reproduction of the same
  structure-collapse effect DART's predict-then-rank experiments show (Result 4).
  Kedzierska et al. (2025, *Genome Biology*) reach a parallel conclusion for
  single-cell foundation models under zero-shot evaluation.

- **The choice of metric can decide the winner.** A recent analysis (*The Metric
  Picks the Winner*, arXiv 2026, preprint) documents that the evaluation metric
  flips model rankings for drug-response prediction in unseen chemistry — the same
  same-method-different-verdict phenomenon the A-vs-B contrast above demonstrates.

- **The distributional metrics themselves have failure modes — including DART's.**
  A metric-focused evaluation (*Evaluating Single-Cell Perturbation Response Models
  Is Far from Straightforward*, bioRxiv 2026, preprint) shows that common
  distributional distances are strongly influenced by scale, sparsity, and
  dimensionality: the Wasserstein distance fails in high-dimensional expression
  space under variance scaling, and **the energy distance can overlook disruptions
  in gene–gene dependencies.** We cite this against ourselves: it bounds DART's own
  Class A energy and coverage scores, and reinforces that a strong distributional
  score is a statement about objective fidelity, not independent utility.

- **The field already evaluates with this metric class.** Large benchmarks such as
  scPerturBench (Wei et al. 2026, *Nature Methods*) score generalizable
  perturbation prediction with population-level distances (E-distance, Wasserstein)
  — the same Class A family — confirming both that the metric class is standard and
  that generalization under it is hard.

Verified citations with DOIs are in `related_work_metric_audit_references.md`
(Tier 2). Together these establish that objective-fidelity-versus-independent-utility
is a documented, cross-group concern, and that DART's contribution is to make the gap
measurable on a single task set rather than to discover it in isolation.

---

## 6. What this licenses the manuscript to say

- **Supported (Class A):** distributional retrieval carries real signal on
  response-available heterogeneous populations, and mean/signature retrieval is
  its zero-variance special case.
- **Supported (A→B transition):** that Class A signal does not transfer to
  task-proximal independent metrics, and current diagnostics do not reliably
  isolate a transferable advantage.
- **Not claimed (Class C):** any therapeutic-utility improvement — no Class C
  metric exists in this study, so the paper stops at "signal exists, independent
  utility not established."

## 7. One-line summary

> The audit shows objective-aligned evaluation is a field-wide default across
> signature, predictive, and graph-based inverse methods; DART is the instrument
> that makes the resulting objective-fidelity-versus-independent-utility gap
> measurable on a single task set.
