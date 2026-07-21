# DART manuscript, assembly guide

**Working title:** When is distributional information trustworthy? Auditing evaluation
circularity in single-cell drug retrieval.

**One-line message:** distributional single-cell drug retrieval looks strong only under
metrics aligned with its own objective; under oracle-independent criteria the advantage
collapses, and we give the field a probe, a named failure mode (evaluation circularity),
and a two-gate criterion for when single-cell resolution can pay off.

**Positioning:** audit lens over a crowded distributional-perturbation subfield, NOT a
"first / better retrieval method". See reference/competitive_landscape_positioning.md.

## Files here

| File | Role |
|------|------|
| DART_manuscript.md | canonical full draft (v2 metric-circularity, gated with two-gate Result 4). Locked-numbers authority: reference/manuscript_evidence_table.md |
| introduction_EN.md | canonical English introduction (v5 audit-lens, 7 paragraphs). Splice target for the intro section of DART_manuscript.md |
| introduction_zh.md | Chinese discussion draft the EN intro was rendered from |
| references.bib | TODO, not yet built |
| Makefile | TODO, LaTeX build once prose is converted from MD |

## Number provenance (STRICT)

Every headline number traces through reference/manuscript_evidence_table.md (locked-numbers
authority) and reference/PROJECT_DATA_INDEX.md (navigation over it). Do not cite from memory.
Known reconciliation traps recorded in PROJECT_DATA_INDEX:
- HIR-Bench predictability AUC = **0.640** (FULL 13,440-cell run), NOT the on-disk QUICK
  144-cell reproduction (AUC 0.5).
- +0.119 headline = DART_coverage_worst MEDIAN regret reduction on the recommended subset
  (n=621, p=4.26e-56), NOT DART_energy mean.
- non-recommended +0.122 = mean_or_no_call subset only (n=133), excludes mean_sufficient (n=11).

## Figure deck

Six-figure Nature-style arc (see ../../figures/FIGURE_DECK_PLAN.md). Fig1 concept (AI 1A);
Fig2 unification C1/R1 (absorbs exp06 theory); Fig3 apparent gains C2/R2; Fig4 collapse
C3/R3 (the knife, 4 panels); Fig5 two-gate C4/R4; Fig6 HIR-Bench C5/R5 + resistance coda
C6/R6. NOTE renumbering: current rendered figs (fig2_class_a_gains, fig3_metric_collapse,
fig4_information_condition) map to deck Fig3/Fig4/Fig5; manuscript figure-refs to follow
once the deck is built.

## Manuscript folder map

- latex/          this folder, canonical prose + build
- reference/      locked-number authorities + landscape positioning
- components/     related-work matrix, figure captions, negative-claims box (feed the prose)
- submission_prep/ reviewer risk register, expected-reviewer responses, stats checklist
- _archive/       superseded drafts, intros, figure plans, titles, audit notes, protocols
                  (nothing deleted; recoverable)
