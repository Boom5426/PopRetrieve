# PopRetrieve manuscript, build guide

**Title:** Objective-aligned evaluation inflates distributional gains in single-cell drug
retrieval.

**Running title:** Objective--utility mismatch in single-cell drug retrieval.

**Positioning:** an audit of how distribution-aware single-cell drug retrieval is *evaluated*,
not a proposal for a better retrieval method. The population-to-population scores released as
PopRetrieve are the instrument: one fixed set of rankings is re-graded under criteria of increasing
independence, so the rankings, the scorer and the queries hold still and only the evaluation
shifts. See `../reference/competitive_landscape_positioning.md` and `../reference/naming.md`.

## Build

```bash
make            # manuscript: pdflatex, bibtex, pdflatex x2  -> PopRetrieve_manuscript.pdf
make si         # supplementary: pdflatex x2                 -> PopRetrieve_SI.pdf
make clean      # aux, bbl, blg, log, out, toc
```

Both targets must finish with **zero** `LaTeX Warning: Reference ... undefined` and zero
`Citation ... undefined`. The SI has `natbib` loaded but **no bibliography**, so a `\cite{}`
there renders as `[?]`; SI references are written as plain author-year text on purpose.

## Files here

| File | Role |
|------|------|
| `PopRetrieve_manuscript.tex` | the manuscript. Single source for every number, via macros defined in the preamble |
| `PopRetrieve_SI.tex` | supplementary information: notes, supplementary tables, Extended Data captions |
| `references.bib` | bibliography for the manuscript only |
| `Makefile` | the build above |
| `PopRetrieve_manuscript.bbl` | committed on purpose: the one artifact a reader without `bibtex` still needs |
| `PopRetrieve_manuscript.md`, `introduction_EN.md`, `introduction_zh.md` | superseded prose drafts, kept for provenance. **Not** the source of the PDF |
| `RESULTS_SPINE.md` | superseded outline of an earlier six-figure deck, kept for provenance. Several of its panel specs are written in terms of retracted numbers; it carries its own banner |
| `figures/` | the PDFs the documents `\includegraphics`. Written by the figure build, not by hand |

## Figures are generated, never edited here

`figures/fig{1..5}.pdf` are **copied in by the figure build** and must not be edited in place:

```bash
python figures/build_all.py            # dry run: typography gate only
python figures/build_all.py --write    # rebuild, then sync to manuscript/latex/figures/
```

`build_all.py` owns one canonical stem per figure (`fig1_problem`, `fig2_temptation`,
`fig3_collapse`, `fig4_benchmarks`, `fig5_two_gate`) and refuses to build if a
`figN_assemble.py` declares a different one. It also fails the build if any text is **authored**
below 5 pt. It does **not** know this document's text width: the check reads nominal point
sizes, so a figure authored wider than the text block is scaled down by
`\includegraphics[width=\textwidth]` and can print below 5 pt while the gate reports CLEAN. The
five main figures are authored at 6.90 in, i.e. the printed width, so their scale factor is 1.00
and nominal equals printed.

The five figures are 7.98 to 9.22 in tall on the page and their captions run 460 to 731 words, so
graphic and caption cannot share a page and are two floats each: a `[p]` float holding only the
`\includegraphics`, then a `[p]` float holding only the `\caption` and `\label`. The figure
counter advances on `\caption`, not on `\begin{figure}`, so the graphic float leaves the number
alone and the caption float takes it.

Three of the five now sit at 9.22 in against a float budget of 9.238 in (the 9.461 in text block
less about 16/72 in of float overhead), i.e. 0.018 in of margin. Growing any authored canvas means
re-checking `Float too large` in the build log, not assuming it still fits.

Extended Data no longer exists. It had its own driver because copying it by hand did not work: on
2026-07-27 all seven shipped Extended Data PDFs were stale renders, and three printed numbers this
project has retracted, each contradicting its own caption on the same page. On 2026-08-29 the
seven became three, and on 2026-08-30 the deck was retired: five panels that a main figure or a
Supplementary Table already carried in full were deleted, and the surviving 21 moved into the five
main figures. `figures/build_all.py` is now the only figure driver.

| target | built by |
|---|---|
| `figures/edfig1.pdf` .. `edfig4.pdf` | `figures/edfigs/ed_panels.py` (stems `ed1_reproducibility`, `ed2_classB_robustness`, `ed3_identifiability`, `ed4_resistance_exploratory`) |
| `figures/edfig5.pdf` | `figures/ed5/ed5.py` |
| `figures/edfig6.pdf` | `figures/ed6/ed6.py` (panels in `ed6/ed6_panel_{a,c,d,e}.py`) |
| `figures/edfig7.pdf` | `figures/ed7/ed7_tahoe.py` (stem `ed7_tahoe`) |

Known outstanding issue, recorded in `figures/edfigs/README.md`: ED1 to ED4 are authored far wider
than the text block, so LaTeX scales them down and their type prints at roughly 2.8 to 3.5 pt,
below the 5 pt floor. The typography gate measures nominal size only and does not catch this.

## Numbers: this file quotes none, and neither should any other guide

Every headline number in the manuscript is a **LaTeX macro defined once** in the preamble of
`PopRetrieve_manuscript.tex`, so the text, a figure caption and the Methods cannot drift apart. New
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
