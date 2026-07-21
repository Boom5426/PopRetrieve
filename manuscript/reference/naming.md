# DART paper, title and abbreviation decision

Version 2026-07-12. No em dashes.

## Title (DECIDED, user-approved 2026-07-12)

**When is distributional information trustworthy? Auditing evaluation circularity in
single-cell drug retrieval.**

Rationale: main clause is a question hook (translates the paper from "warning" to "we
answer a question the field is asking"); subtitle puts the citable knowledge kernel
("evaluation circularity") in the title. Matches the audit-lens positioning; does not
imply a retrieval method is being sold.

## Abbreviation (DECIDED, user-approved 2026-07-12)

**DART = Distributional Auditing of Retrieval Transfer.**

Kept the DART acronym (zero migration cost, figures and code already say DART), shifted the
expansion from the old method-flavored "Distribution-Aware Retrieval for Therapeutic Ranking"
to the audit-flavored "Distributional Auditing of Retrieval Transfer" ("Transfer" encodes the
core finding that gains do not transfer). Applied in DART_manuscript.md abstract + intro.

DrugDiT was proposed and rejected; rationale retained below.

### Why not DrugDiT

User proposed: **DrugDiT**.

Agent recommendation: **do not use DrugDiT.** Two hard problems.

1. Name collision + wrong-genre signal. "DiT" reads as Diffusion Transformer, and the
   drug-perturbation diffusion-transformer niche is already occupied: a 2026 paper
   "Predicting drug-perturbed transcriptional responses using multi-conditional diffusion
   transformer" (Hu et al., Quantitative Biology 2026) is essentially a DrugDiT by another
   name; DrugDAGT (dual-attention graph transformer, 2024) is adjacent. A reader seeing
   "DrugDiT" will expect a generative diffusion-transformer model that predicts drug
   responses. Our paper is the opposite: an audit that argues distributional/generative
   scores are over-trusted. The acronym would advertise the exact genre we are critiquing.

2. It re-sells a method. The whole repositioning is "not a method, an audit lens." A
   catchy method-style acronym (DrugDiT) pulls straight back toward "here is our model,"
   undercutting the title we just chose.

## Options that fit the audit-lens positioning

If an acronym is wanted, it should name the INSTRUMENT or the PHENOMENON, not a model:

- Keep **DART**, shift expansion to audit flavor: **D**istributional **A**uditing of
  **R**etrieval **T**ransfer. Zero cost (figures/code already say DART), and "transfer"
  encodes the core finding (gains do not transfer). Agent's leading option.
- **CIRCE** = **C**ircularity **I**n **R**etrieval, a **C**ircularity **E**valuation (probe).
  Names the phenomenon; memorable; low collision.
- **MIRAGE** = metric-induced retrieval advantage gauge for evaluation. Strong "looks real,
  is not" metaphor matching evaluation circularity; slightly dramatic.
- No acronym at all. A methodology/audit paper does not need one; the title carries it.

## Recommendation

Keep DART with the audit-flavored expansion, OR drop the acronym entirely. Avoid DrugDiT.
Decision pending user.
