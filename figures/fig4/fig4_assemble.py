"""PopRetrieve Figure 4: The benchmark decides the answer.

ARCHETYPE: quantitative grid, three rows of two.

WHY THESE TWO THINGS ARE NOW ONE FIGURE
---------------------------------------
This used to be HIR-Bench alone (six panels), with the natural-heterogeneity test as a separate
Figure 7 (three panels). They are the same argument approached from opposite ends, and splitting
them hid that:

  ROW 1, FROM THE INSIDE. In a synthetic benchmark the latent utility oracle is known, so
  circularity stops being something one argues about and becomes something one measures: every
  feature can be labelled oracle-derived or observable and the inflation read off a dial.

  ROW 2, FROM THE OUTSIDE. Take a benchmark we constructed (cell-line mixtures) and check it
  against tissue nobody assembled (patient glioblastoma). It misled us in BOTH directions at once,
  and both distortions happened to flatter our own premise.

HIR-Bench led the main text with two panels, a and b, and its other four sat in Extended Data. Its
phase boundary is designed in and its transfer to real data fails, so the main-text argument is
still carried by the analytic condition and by the circularity measurement, which is the one place
in this paper where circularity is quantified rather than asserted. Three of the four demoted
panels are back below them as g, h and i (see the 2026-08-30 note). Only the generative schematic
(old 6a) stays deleted, because it read no result file and drew no data: panel a and Supplementary
Note 1 carry what it stated.

Earlier titles for 6c/6d/6f described panels other than the ones drawn; a title that contradicts
its own axes is the same class of error this paper is about, and they were fixed on 2026-07-12.

GEOMETRY, 2026-07-26: AUTHORED AT FINAL PRINT WIDTH
---------------------------------------------------
This figure used to be authored 11.6 in wide and entered the manuscript through
``\\includegraphics[width=\\textwidth]`` into a 6.93 in text block, i.e. LaTeX shrank it by 0.60x.
Every point size in it therefore reached the page at 60% of its nominal value: the 6 pt tick labels
printed at 3.6 pt, well under the 5 pt Nature Portfolio production floor, while the build-time gate
in ``figstyle.py`` measured only the NOMINAL sizes and reported the figure clean.

The canvas is now 6.9 in wide, a hair under the text block, so the scale factor is 1.0 and the
nominal sizes below ARE the printed sizes. Nothing about what the panels plot changed. What changed
is that the annotation load had to come down to match the real area available: at 0.6x the old
width every on-panel sentence was suddenly full size against a panel half as wide, so the
interpretive glosses were cut and the numbers the Results text sends readers to were kept. The
caption carries what was cut.

Panel rectangles are given in INCHES rather than as gridspec ratios. At this size the binding
constraints are the widths of specific pieces of text (b's two-line row labels, c's y-axis label,
d's robustness block), and inches are the units those constraints are actually measured in.

2026-08-30: THE EXTENDED DATA DECK IS RETIRED, AND SEVEN PANELS COME BACK AS g-m
--------------------------------------------------------------------------------
Captions now set on the page FOLLOWING the figure, so the graphic no longer shares a text block
with 250 words of caption and may run to 9.30 in tall instead of about 5 in. That is what makes
this possible; it is not a reason on its own, so each of the seven is placed under the panel it
verifies rather than appended where there was room. The mapping is one to one.

  ROW 3, g-i: HIR-BENCH CHECKING ITSELF. It is the whole of row 1's benchmark half audited, and
  the columns line up with what each panel audits: g sits under a, h sits under b, and i, which
  audits the construction rather than any single claim, takes the remaining slot under c.
    g  ed6_panel_c.draw_ed6b  energy minus mean Hit@1 over the 9 x 4 conflict-lambda by
                              minority-fraction grid. Panel a states the flip condition
                              analytically, two rows up; g is that same boundary MEASURED, cell by
                              cell, so the claim in a is checkable against the benchmark rather
                              than only against its own algebra.
    h  ed6_panel_d.draw_ed6c  best decision regret, observed against predicted-mean, under mean
                              welfare (0.11 -> 0.45) and worst welfare (0.29 -> 0.96). Panel b
                              measures how much of an evaluator is oracle-derived; h prices that
                              same loss of structure as a decision cost, in the same benchmark.
                              The minority-sensitive welfare is where the price is highest, which
                              is the whole reason the mean is not a safe default.
    i  ed6_panel_e.draw_ed6d  the three sanity checks against their thresholds: no-conflict flip
                              rate 0.000, median boundary margin 0.272, predicted-mean equality
                              0.056. A benchmark whose answer is designed in owes the reader
                              evidence that it behaves as specified, and this is that evidence.
                              Reading a and b without it means taking the construction on trust.

  ROW 4, j-m: THE COMPARTMENT CALLS THAT d, e AND f REST ON, in the row directly below them and
  in their columns: j and k under d, l under e, m under f. All four come from one module,
  ed4_zhao_robustness, over one sweep of ZhaoSims2021, which is why they read as one block.
    j  draw_a  marker-set mean expression for malignant, myeloid and oligodendrocyte cells. Every
               number in d, e and f is computed WITHIN these three compartments, so if the calls
               are wrong the three panels above are measuring nothing. j is the diagonal test.
    k  draw_b  cells retained and cells left unassigned as the marker floor and the margin move
               together from 0.10 to 0.50. The primary setting keeps 60 per cent of the tissue;
               k is where a reader sees what the other 40 per cent cost.
    l  draw_c  malignant-versus-myeloid differential-response cosine over the same sweep, range
               0.54 to 0.59. Panel e reports one such cosine and argues divergence is overstated;
               l shows that reading does not depend on where the threshold was put.
    m  draw_d  supervised ceiling against best unsupervised recovery over the same sweep. Panel d
               is this figure's one constructive claim, that the tumour gap is algorithmic rather
               than informational, and m is the check that the gap is not a threshold artefact.

The three ed6 modules are named for the panel letters of the RETIRED Extended Data Fig. 6, and
those letters are off by one from their own function names: ed6_panel_c defines draw_ed6b,
ed6_panel_d defines draw_ed6c, ed6_panel_e defines draw_ed6d. The imports below are written out
one per line so that mismatch is visible rather than something to rediscover.
"""
import os
import re
import sys

import matplotlib.pyplot as plt
import matplotlib.text as mtext

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "fig7")))
# g-m are drawn by the modules that used to be Extended Data Fig. 6 and Fig. 4. The panel code is
# imported, not copied: a second copy of a draw function is a second thing to keep in step with the
# result files, and the Extended Data deck being retired is not a reason to fork its panels.
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "ed4")))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "ed6")))

# The one canonical output stem for this figure; must equal build_all.STEMS[5], which build_all
# asserts, because that is the name copied to manuscript/figures/fig4.pdf. The legacy
# fig4_hir_bench.* files in this directory are the SUPERSEDED six-panel HIR-Bench figure, not
# another copy of this one.
STEM = "fig4_benchmarks"

from figstyle import pin_canvas, soften_axes, strip_titles
from fig4_style import PT_ANNOT, PT_FLOOR, PT_LETTER, PT_TICK, PT_TITLE, TEXT
from fig4_design import draw_design              # a: what is held fixed across b's two columns
from fig4_shape import draw_shape                # b: the evaluator's FORM picks the winner
from fig4_residual import draw_residual          # c: energy's lead over the magnitude control
# fig4_tissue.draw_tissue drew the tumour-cohort schematic and LEFT ON 2026-09-05. It carried no
# data: it restated in a flowchart the design that the Results sentence citing it already states in
# full ("each tumour was split by cell identity into disjoint malignant and myeloid compartments
# that share no cells and received the same drug and matched control"), and the caption states it
# again. It was also what made this figure 2-3-2, so its row could never be filled by the two
# aspect-locked panels below it. The module is kept on disk; nothing imports it.
from fig4b import draw_4b                        # d: the analytic existence proof
from fig4_gate2 import draw_gate2                # e: recoverability, constructed against natural
from fig4_nat import draw_nat_premise            # f: disjoint-compartment ordering
#
# THE PANEL ORDER CHANGED ON 2026-09-05, AND CITATION ORDER IS WHY. The analytic boundary was
# the last panel in the figure and the fourth thing the Results cites: the text runs design,
# reversal, magnitude control, THEN the boundary as the bridge into the tumour section ("that
# boundary does not transfer reliably to the real datasets analysed here"), then the two tumour
# panels. So the reader met a on page one and was sent to g before d. Nature asks for panels in
# citation order and the same defect was fixed in Figure 3 on 2026-09-04, so the boundary moves
# from last to fourth and the two tumour panels keep the letters they already had. Only one
# letter changes in the manuscript, g to d, on top of dropping the citation to the schematic
# that left on 2026-09-05.
#
# FIVE PANELS LEFT THIS FIGURE ON 2026-09-03, and none of them left the paper.
#
#   the old b, draw_4f            the honest-versus-leaky classifier AUC matrix
#   the old e, draw_nat_gate1     induced response cosine, 17 patient-drug pairs
#   the old g, draw_ed6b          the empirical energy-minus-mean phase grid
#   the old h, draw_ed6c          decision regret by information condition
#   the old i, draw_ed6d          the three HIR-Bench sanity checks
#
# Four of the five were HIR-Bench, which left this figure carrying five synthetic panels against
# four real ones while a real transition-to-intervention benchmark now exists elsewhere in the
# paper. HIR-Bench keeps exactly one panel here, g, and it keeps the one that is an EXISTENCE
# PROOF rather than a measurement: the analytic boundary, which shows constructively that
# within-population structure can change the preferred candidate. Everything the other four
# showed is prose in Supplementary Note 1, which already carried most of it.
#
# The fifth, the induced response cosine, was cut for a different reason. A cosine between two
# response directions is confounded with effect size and signal-to-noise, so it cannot support
# the quantitative reading the main text gave it, that compartment pharmacology differs strongly.
# It is described in Supplementary Note 4 as a descriptive alignment and is explicitly not used
# as a measure of differential-response strength.
#
# THE SUPPLEMENTARY INFORMATION HOLDS NO FIGURES AND STILL HOLDS NONE. It has never contained a
# float, no script can build one, and two sentences in the manuscript assert that there are no
# Extended Data figures. Every demotion here is therefore a move of CONTENT into an existing
# Supplementary Note, not a new supplementary figure, and those two sentences stay true.

TITLES = {
    # Every title is a claim that must survive being read against its own panel. The 2026-07-12
    # audit found three in this figure that described panels other than the ones drawn, and by
    # 2026-09-05 the dict had drifted again: it still carried the thirteen-panel deck's letters,
    # so "a" named the analytic boundary while panel a had been the design schematic for two
    # revisions. It is rewritten here against the six panels that exist. Nothing draws these;
    # strip_titles() removes any title from the composite and the caption is what a reader sees.
    # They are kept because the caption has to be checkable against a written statement of what
    # each panel argues.
    "a": "One experiment, two evaluator forms",
    "b": "The evaluator's shape picks the winner",
    "c": "The magnitude control carries most of the lead",
    "d": r"The mean suffices below $\alpha^*$",
    # scoped to the tumour on purpose: the constructed arm in this same panel shows a gap of
    # +0.007, i.e. there the limit is NOT algorithmic. An unscoped title would contradict one of
    # its own two bar groups.
    "e": "Recoverability in a tumour: an algorithmic limit",
    "f": "Divergence is overstated",
}
ROW_LABELS = [
    # Three rows since 2026-09-05, and they are not three arguments. Rows 1 and 2 are one
    # argument in two halves, and row 3 is the same question asked of tissue nobody assembled.
    "The external protein evaluator: what is held fixed, and what changes when only its form does",
    "How much of that reversal needs no distribution, and where structure can change a decision at all",
    "Naturally heterogeneous tissue: what is recoverable in it, and whether it reorders anything",
]

# LAYOUT, in inches on a 6.90 x 5.48 in canvas.
#   x0, y0 measured from the bottom-left corner; w, h are the AXES box (tick labels, axis labels
#   and panel letters live outside it, in the gutters).
#
# 5.48 IN, NOT 6.35, SINCE 2026-09-05, and the width is why the height could move.
# The 2026-09-04 cut left six panels in three rows of two on a 6.35 in canvas, and measured on
# the render the two lower rows carried 0.82 and 0.87 in of dead gutter between their columns
# while every row's own panels sat at their authored heights. Two panels per row cannot fill
# 6.90 in here, because two of the six are aspect-locked squares: fig4_nat sets
# set_aspect("equal") so its box collapses to a square of side equal to the ROW HEIGHT, and the
# boundary panel is a unit square in all but name. A square of side h contributes h of width, so
# the wide panel beside it has to run to about 5.5 - h inches to reach the page edge, and at
# these heights that is a 4 in bar chart. The gutter is therefore structural, and the way to
# stop the figure reading as loose is to take the height out, not to stretch the panels.
#
# Each row now stands at what its own tightest panel was MEASURED to need, by bisecting the
# panel alone on a canvas until either its own draw-time assertions or figures/check_overlaps.py
# fired, and then stepping back:
#   row 1  1.66 in   a, the design schematic. Its two evaluator boxes put their titles into
#                    their own two-line bodies at 1.65. b needs 1.39 and follows the row.
#   row 2  1.05 in   neither binds; c holds four rows of markers and clears at 0.88, and the
#                    boundary panel is two washes and a line. 1.05 is chosen rather than
#                    measured, to keep the boundary nearer 45 degrees than the row above it.
#   row 3  1.25 in   e, the recoverability panel, floor 1.17 after its in-bar labels were set on
#                    two lines (see fig4_gate2). At one line that floor was 1.59 in and this was
#                    the tallest row in the figure's lower half.
# Corridors between rows are 0.07 and 0.05 in of clear space, last ink to first ink, measured on
# the render; the page margins are 0.08 left, 0.07 right, 0.06 top and 0.06 bottom. Nothing was
# resized, no annotation was cut, and no panel moved to a different scale.
#
# Panel widths are deliberately unequal, and the gutters are sized by the text that has to fit in
# them rather than by a uniform wspace:
#   3.32 -> 3.77  b's two-line y-axis label and its tick labels
#   4.33 -> 4.78  the boundary panel's y-axis label and tick labels
#   4.41 -> 4.89  f's y-axis label and tick labels
W, H = 6.9, 5.48
Y1, Y2, Y3 = 3.66, 2.18, 0.38     # row baselines, bottom of the axes box
RECTS = {                     # x0,   y0,   w,    h     (inches, from the bottom left)
    # Row 1 is the external evaluator: what is held fixed (a), and what changes when only the
    # evaluator's form does (b). a is a schematic and needs width rather than furniture, so it
    # starts at the page margin; b gains 0.57 in over the 2026-09-04 cut, which its six bars and
    # their rotated value labels absorb.
    "a": (0.22, Y1, 3.10, 1.66),
    "b": (4.33, Y1, 2.50, 1.66),
    # Row 2 is the magnitude control (c) and the analytic boundary (d). c is a dot plot on four
    # rows and takes the width; d is given 1.50 in against a 1.05 in row so its boundary prints
    # at 35 degrees rather than the 32 it printed at on the previous canvas. It is not 45: that
    # would cost the row 0.45 in of width for one panel, and both half-planes are washed, so the
    # partition reads from the fill rather than from the angle.
    "c": (0.68, Y2, 3.65, 1.05),
    "d": (5.15, Y2, 1.50, 1.05),
    # Row 3 is the tumour. f is squared by set_aspect upstream and can use no more than the row
    # height whatever box it is given, so its box IS the square and e takes the rest of the row.
    "e": (0.56, Y3, 3.85, 1.25),
    "f": (5.30, Y3, 1.25, 1.25),
}
# The panel letter must clear its own panel's y-axis furniture, which differs a lot between a
# schematic with the axis off (a, where only the letter itself sits left of the box) and a dot
# plot whose categories ARE its two-line row labels (c). Given here in inches to the LEFT of the
# axes box and converted to the axes-fraction dx that the letter call wants.
LETTER_IN = {"a": 0.14, "b": 0.56, "c": 0.60, "d": 0.37, "e": 0.48, "f": 0.27}


_SUBSUP = re.compile(r"\$[^$]*[\^_][^$]*\$")


def _assert_floor(fig, floor=PT_FLOOR):
    """Refuse to return a figure carrying text below THIS figure's floor.

    figstyle.save() enforces the deck's 5 pt production limit. This is stricter and runs earlier,
    because 5 pt is what production rejects and 6.5 pt is what a reader can take in at 183 mm.
    Mathtext is measured at its effective size, a sub/superscript printing at 0.7x nominal.

    When this fires the fix is to CUT the annotation into the caption. It is not to lower the size:
    that is how this figure came to hold 336 artists under the floor in the first place.
    """
    bad = []
    for t in fig.findobj(mtext.Text):
        s = str(t.get_text())
        if not s.strip() or not t.get_visible():
            continue
        eff = t.get_fontsize() * (0.7 if _SUBSUP.search(s) else 1.0)
        if eff < floor - 1e-6:
            bad.append((round(eff, 2), s.replace("\n", "/")[:40]))
    assert not bad, (
        f"Figure 4 sets its own {floor} pt floor and {len(bad)} artists are under it: "
        f"{sorted(bad)[:8]}. Cut the annotation into the caption; do not lower the size.")
    return fig


def _assert_no_titles(fig, cap=PT_ANNOT):
    """Refuse to return a figure in which any PANEL draws text above ``cap``.

    The panels carry evidence and the caption carries the argument. This figure's panels have
    never stated their own conclusions, unlike Figures 1 to 3 before their 2026-08-31 pass, so
    this gate is here to keep it that way rather than to enforce a change. Panel letters are
    exempt: fig4_assemble draws them, and they are navigation rather than claims.
    """
    letters = {t for ax in fig.axes for t in ax.texts
               if len(str(t.get_text())) == 1 and str(t.get_text()) in RECTS}
    bad = []
    for t in fig.findobj(mtext.Text):
        if t in letters or not str(t.get_text()).strip() or not t.get_visible():
            continue
        if t.get_fontsize() > cap + 1e-6:
            bad.append((round(t.get_fontsize(), 2), str(t.get_text()).replace("\n", "/")[:40]))
    assert not bad, (
        f"Figure 4 caps panel text at {cap} pt and these are above it: {sorted(bad)[:8]}. "
        f"A panel states no conclusion; move the sentence to the caption.")
    return fig



def build(apply_style, panel_letter):
    # This figure's ladder, one step above the deck's (8, 7, 6), matching Figures 1 to 3.
    # The tick size alone lifts 97 rc-driven labels from 6.0 to 6.8 pt for free.
    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    fig = plt.figure(figsize=(W, H))
    # Pin the tight bbox to the authored canvas, so the exported page size is authored rather than
    # emergent (see the height note above the RECTS table).
    pin_canvas(fig)
    fns = {"a": draw_design, "b": draw_shape, "c": draw_residual,
           "d": draw_4b, "e": draw_gate2, "f": draw_nat_premise}
    assert set(fns) == set(RECTS), "every panel needs a rectangle and a draw function"

    for k, (x0, y0, w, h) in RECTS.items():
        ax = fig.add_axes([x0 / W, y0 / H, w / W, h / H])
        fns[k](ax)
        ax.text(-LETTER_IN[k] / w, 1.06, k, transform=ax.transAxes, fontsize=PT_LETTER,
                fontweight="bold", va="top", ha="left", color=TEXT)

    # Nature panels carry no titles and Nature figures carry no row banners; both are in the
    # caption. TITLES and ROW_LABELS are kept as the statement of what each panel and each row
    # argues, because the caption has to be checkable against them.
    return _assert_no_titles(_assert_floor(strip_titles(soften_axes(fig))))


if __name__ == "__main__":
    # build() must not write the composite itself. It used to call fig.savefig() for
    # fig4_benchmarks.{png,pdf} at the end, i.e. the standalone `python fig4_assemble.py` shipped
    # the figure that build_all.py deploys WITHOUT ever running figstyle.save()'s 5 pt typography
    # gate: the one export path that skipped the check wrote to exactly the stem that is copied to
    # manuscript/figures/fig4.pdf. Writing only through save() means every path that can
    # produce that file also has to pass the floor.
    from figstyle import apply_style, panel_letter, save
    save(build(apply_style, panel_letter), os.path.join(HERE, STEM))
    print(f"wrote {STEM}.pdf / .svg / .png")
