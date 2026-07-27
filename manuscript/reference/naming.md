# Paper title and abbreviation: decision record

No em dashes.

> **Sections 1 to 3 below are the 2026-07-12 record and are SUPERSEDED.** Neither the title nor
> the name they decide is the one the manuscript now carries. They are kept because they document
> why DrugDiT was rejected and why an audit-flavoured name was wanted at all, and both arguments
> still govern. The current decisions are in "2026-07-27: EvalShift" at the end of this file.

## 1. Title (2026-07-12, SUPERSEDED)

**When is distributional information trustworthy? Auditing evaluation circularity in
single-cell drug retrieval.**

Rationale: main clause is a question hook (translates the paper from "warning" to "we
answer a question the field is asking"); subtitle puts the citable knowledge kernel
("evaluation circularity") in the title. Matches the audit-lens positioning; does not
imply a retrieval method is being sold.

## 2. Abbreviation (2026-07-12, SUPERSEDED)

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

## 3. Options that fit the audit-lens positioning (2026-07-12)

If an acronym is wanted, it should name the INSTRUMENT or the PHENOMENON, not a model:

- Keep **DART**, shift expansion to audit flavor: **D**istributional **A**uditing of
  **R**etrieval **T**ransfer. Zero cost (figures/code already say DART), and "transfer"
  encodes the core finding (gains do not transfer). Agent's leading option.
- **CIRCE** = **C**ircularity **I**n **R**etrieval, a **C**ircularity **E**valuation (probe).
  Names the phenomenon; memorable; low collision.
- **MIRAGE** = metric-induced retrieval advantage gauge for evaluation. Strong "looks real,
  is not" metaphor matching evaluation circularity; slightly dramatic.
- No acronym at all. A methodology/audit paper does not need one; the title carries it.

### Recommendation as of 2026-07-12

Keep DART with the audit-flavored expansion, OR drop the acronym entirely. Avoid DrugDiT.
Decision pending user.

---

## 4. 2026-07-27: EvalShift (CURRENT)

### Title (user-approved 2026-07-27)

**Objective-aligned evaluation inflates distributional gains in single-cell drug retrieval.**

Three candidates were put to the author. The two that led with the tool name were both rejected,
for the reason section 2 of this file already gives: the whole repositioning is "not a method, an
audit lens", and a title of the form "<Tool> shows that ..." pulls a reviewer straight back to
reading it as a tool paper. The chosen title carries the finding and its direction (what is
inflated, and by what), and never names the instrument. This is the title the manuscript already
carried, changed only from "the distributional gain" to "distributional gains".

Rejected, with the reason each was rejected:

- *EvalShift shows that objective-aligned evaluation inflates distributional gains in single-cell
  drug retrieval.* Complete, but 15 words, and the "<Tool> shows that" frame is in tension with the
  Introduction's own "used here as a probe rather than offered as a method".
- *EvalShift reveals objective--utility mismatch in single-cell drug retrieval.* Shortest, but
  "mismatch" states that there is a discrepancy without stating its direction, so the paper's
  actual result (objective-aligned evaluation inflates, rather than deflates) leaves the title. It
  also duplicates the running title.

### Name (user-decided 2026-07-27)

**EvalShift. Not an acronym.** The GitHub repository was renamed first and the sources follow.

The name states the study design rather than a property of the score: one fixed set of rankings is
re-graded under criteria of increasing independence, so the rankings, the scorer and the queries
hold still and the evaluation is the only thing that shifts. Both earlier names were acronyms
whose expansion asserted something about the instrument (DART = Distributional Auditing of
Retrieval Transfer; JUDGE = Judging Utility of Distributional Gains in Evaluation), and every such
expansion had to be maintained in the abstract, the Introduction, README.md and CITATION.cff, where
it kept going stale. Dropping the expansion removes that maintenance surface entirely.

JUDGE was used for one day (2026-07-26) and abandoned for a specific reason worth recording: the
manuscript's central sentence is "only the judge then changes", where *judge* means the evaluating
criterion. Naming the instrument JUDGE made that sentence collide with itself, and sixteen sites in
the manuscript and SI had to be reworded around the collision. Those rewordings are kept, because
referring to the instrument as "the distributional score" or "this framework" near the word *judge*
is better for the audit positioning regardless of what the tool is called.

### What is deliberately NOT renamed

The `DART_` prefix on method keys in `results/` and `src/` (`DART_energy`,
`DART_coverage_worst`, ...) and the regime label `no_DART`. These are the keys under which every
published number was computed and stored. See the "A note on the name" section of README.md.
