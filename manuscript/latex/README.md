# EvalShift manuscript, build guide

**Title:** Objective-aligned evaluation inflates distributional gains in single-cell drug
retrieval.

**Running title:** Objective--utility mismatch in single-cell drug retrieval.

**Positioning:** an audit of how distribution-aware single-cell drug retrieval is *evaluated*,
not a proposal for a better retrieval method. The population-to-population scores released as
EvalShift are the instrument: one fixed set of rankings is re-graded under criteria of increasing
independence, so the rankings, the scorer and the queries hold still and only the evaluation
shifts. See `../reference/competitive_landscape_positioning.md` and `../reference/naming.md`.

## Build

```bash
make            # manuscript: pdflatex, bibtex, pdflatex x2  -> EvalShift_manuscript.pdf
make si         # supplementary: pdflatex x2                 -> EvalShift_SI.pdf
make clean      # aux, bbl, blg, log, out, toc
```

Both targets must finish with **zero** `LaTeX Warning: Reference ... undefined` and zero
`Citation ... undefined`. The SI has `natbib` loaded but **no bibliography**, so a `\cite{}`
there renders as `[?]`; SI references are written as plain author-year text on purpose.

## Files here

| File | Role |
|------|------|
| `EvalShift_manuscript.tex` | the manuscript. Single source for every number, via macros defined in the preamble |
| `EvalShift_SI.tex` | supplementary information: notes, supplementary tables, Extended Data captions |
| `references.bib` | bibliography for the manuscript only |
| `Makefile` | the build above |
| `EvalShift_manuscript.bbl` | committed on purpose: the one artifact a reader without `bibtex` still needs |
| `EvalShift_manuscript.md`, `introduction_EN.md`, `introduction_zh.md` | superseded prose drafts, kept for provenance. **Not** the source of the PDF |
| `RESULTS_SPINE.md` | the Results-section outline the `.tex` follows |
| `figures/` | the PDFs the documents `\includegraphics`. Written by the figure build, not by hand |

## Figures are generated, never edited here

`figures/fig{1..6}.pdf` are **copied in by the figure build** and must not be edited in place:

```bash
python figures/build_all.py            # dry run: typography gate only
python figures/build_all.py --write    # rebuild, then sync to manuscript/latex/figures/
```

`build_all.py` owns one canonical stem per figure (`fig1_problem`, `fig2_collapse`,
`fig3_temptation`, `fig4_collapse`, `fig5_benchmarks`, `fig6_two_gate`) and refuses to build if a
`figN_assemble.py` declares a different one. It also fails the build if any rendered text would
print below the 5 pt floor at this document's actual text width.

Extended Data is **outside** `build_all.py` and is copied manually:

| target | built by |
|---|---|
| `figures/edfig1.pdf` .. `edfig4.pdf` | `python figures/edfigs/ed_panels.py` (stems `ed1_reproducibility`, `ed2_classB_robustness`, `ed3_identifiability`, `ed4_resistance_exploratory`) |
| `figures/edfig5.pdf` | `python figures/ed5/ed5.py` |
| `figures/edfig6.pdf` | `python figures/ed6/ed6.py` |
| `figures/edfig7.pdf` | `python figures/ed7/ed7_tahoe.py` (stem `ed7_tahoe`) |

Known outstanding issue, recorded in `figures/edfigs/README.md`: ED1 to ED4 are authored far wider
than the text block, so LaTeX scales them down and their type prints at roughly 2.8 to 3.5 pt,
below the 5 pt floor. The typography gate measures nominal size only and does not catch this.

## Numbers: this file quotes none, and neither should any other guide

Every headline number in the manuscript is a **LaTeX macro defined once** in the preamble of
`EvalShift_manuscript.tex`, so the text, a figure caption and the Methods cannot drift apart. New
prose must use the macro, never a literal.

The authorities, in order:

1. `../../CORRECTIONS.md` for what a number *was* and what it *is*. Read it before quoting
   anything from an older document in this repository.
2. `../reference/manuscript_evidence_table.md`, the locked-numbers table.
3. `../reference/PROJECT_DATA_INDEX.md`, navigation over the results tree.

An earlier version of this file carried its own "number provenance" cheat-sheet. It was deleted
because it had gone stale in exactly the way the manuscript argues against: it presented the
HIR-Bench predictability AUC of 0.640 as the authoritative headline, and that result is
**retracted** (CORRECTIONS.md, R11: the features and the label were both functions of the same
oracle). A guide that restates numbers becomes a second source for them. This one points instead.

## Manuscript folder map

- `latex/` this folder, canonical prose plus build
- `reference/` locked-number authorities, positioning, naming decisions
- `components/` related-work matrix, figure captions, negative-claims box (feed the prose)
- `submission_prep/` reviewer risk register, expected-reviewer responses, stats checklist
- `_archive/` superseded drafts, intros, figure plans, titles, audit notes, protocols. Nothing
  deleted, and deliberately **not** renamed when the project was: it is a historical record and
  still says DART throughout
