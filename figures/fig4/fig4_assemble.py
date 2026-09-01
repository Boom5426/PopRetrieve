"""PopRetrieve Figure 4: The benchmark decides the answer.

ARCHETYPE: quantitative grid, three rows of three.

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
# asserts, because that is the name copied to manuscript/latex/figures/fig4.pdf. The legacy
# fig4_hir_bench.* files in this directory are the SUPERSEDED six-panel HIR-Bench figure, not
# another copy of this one.
STEM = "fig4_benchmarks"

from figstyle import pin_canvas, soften_axes, strip_titles
from fig4_style import PT_ANNOT, PT_FLOOR, PT_LETTER, PT_TICK, PT_TITLE, TEXT
from fig4b import draw_4b                        # analytic flip boundary
from fig4f import draw_4f                        # 2x2: observable vs oracle-derived x CV unit
from fig4_shape import draw_shape                # the oracle's SHAPE picks the winner (real data)
from fig4_gate2 import draw_gate2                # Gate 2, same construct in both settings
from fig4_nat import draw_nat_gate1, draw_nat_premise   # natural-tissue arm, retuned for 6.9 in
from ed6_panel_c import draw_ed6b               # g: energy - mean Hit@1 phase grid  (old ED6c)
from ed6_panel_d import draw_ed6c               # h: decision regret by information condition (ED6d)
from ed6_panel_e import draw_ed6d               # i: the three benchmark sanity checks  (old ED6e)

TITLES = {
    # Every title is a claim that must survive being read against its own panel. The 2026-07-12
    # audit found three in this figure that described panels other than the ones drawn; the risk
    # is highest for d, where the same axes carry a constructed arm and a natural one that reach
    # opposite conclusions, so d names the setting its claim holds in.
    #
    # 2026-07-26: the titles are shorter because the panels are now 1.3-2.5 in wide rather than
    # 2-4 in, and an 8 pt title that overruns its own panel lands on the next panel's letter. Each
    # one is still a claim its own data supports; nothing was broadened, and no earlier title was
    # restored.
    "a": r"The mean suffices below $\alpha^*$",
    "b": "Objective alignment, measured",
    "c": "The evaluator's shape picks the winner",
    # scoped to the tumour on purpose: the constructed arms in this same panel show a gap of
    # +0.007 and -0.002 (fixed pairs), i.e. there the limit is NOT algorithmic. An unscoped title
    # would contradict two of its own three bar groups.
    "d": "Recoverability in a tumour: an algorithmic limit",
    "e": "Divergence is overstated",
    "f": "The mean ranks most of it",
    # g-m, added 2026-08-30. Each is the claim the panel's own draw function used to set as its
    # standalone title, restated to hold at this size; strip_titles() still removes all of them
    # from the composite, and the caption is what a reader sees.
    "g": "The advantage is regime-dependent",
    "h": "Losing structure inflates regret",
    "i": "The benchmark behaves as specified",
    "j": "The compartment calls match their markers",
    # k, l and m are all the SAME sweep, so each says which quantity it follows across it; a title
    # of "threshold-robust" on three panels would be one claim printed three times.
    "k": "Retention falls with the threshold",
    "l": "Divergence is threshold-stable",
    "m": "The recoverability gap persists",
}
ROW_LABELS = [
    "From the inside: analytically, inside a synthetic benchmark, and between two real evaluators",
    "From the outside: our constructed benchmark, checked against tissue nobody assembled",
    # Rows 3 and 4 are not a third and fourth argument. Each is the audit of the row two above it,
    # which is why they are worded as verification and not as findings.
    "Row 1 audited: the boundary measured, the cost of losing structure, and the benchmark's own QC",
    "Row 2 audited: are the compartments row 2 is computed within real, and does the threshold matter",
]

# LAYOUT, in inches on a 6.90 x 8.09 in canvas.
#   x0, y0 measured from the bottom-left corner; w, h are the AXES box (titles, tick labels, axis
#   labels and panel letters live outside it, in the gutters).
# Panel widths are deliberately unequal: c (the swap between two real external oracles) and d (the
# one constructive finding in the paper, and the panel the Results text sends readers to for the
# robustness numbers) carry the two argument rows and are the two widest panels; a, e and f are
# supporting. The gutters are sized by the text that has to fit in them, not by a uniform wspace:
#   1.91 -> 2.46  b's two-line row labels ("observable / at query time")
#   3.82 -> 4.78  b's colour-bar label, then c's two-line y-axis label
#   3.05 -> 3.38  e's y-axis label;   5.02 -> 5.45  f's two-line y-axis label
#   2.02 -> 2.94  g's colour bar, which make_axes carves out of g's own box and then hangs a
#                 two-line "energy - mean Hit@1" label and its tick labels to the right of; 0.92 in
#                 is what that apparatus measures, and it is the widest gutter in the figure
#   4.50 -> 5.35  i's three two-line row labels. The widest, "pred-mean: / distributional=mean",
#                 measures 0.67 in and starts at 4.60, so the pad is 0.85 and not the 0.83 the
#                 Extended Data version used: at 0.83 the label would clear h by 0.08 in
#   5.21 -> 5.76  m's two-line y-axis label
# Rows 3 and 4 keep the pad-and-width pairs the retired Extended Data figures had measured for
# these exact draw functions at this exact canvas width, so they are re-used rather than re-derived;
# only the last panel in each row is pulled in by 0.07-0.08 in, because there the row used to end
# flush with the canvas and here the tight bbox is pinned to the canvas (see pin_canvas) and a
# right-hand tick label hanging over the edge would widen the exported page.
#
# VERTICAL LEDGER, bottom-up, in inches. y0 is measured from the BOTTOM, so putting two rows in
# UNDERNEATH moves every number in the table; they are all recomputed here rather than patched,
# because a partial recompute is exactly how a row ends up 0.02 in inside its neighbour's gutter.
#
#   0.15  above row 1      the letters, set with va="top" above their own axes
#   1.46  row 1  a b c     y0 = 6.48
#   0.46  gap              row 1's tick labels and x-labels, then row 2's letters
#   1.56  row 2  d e f     y0 = 4.46
#   0.48  gap
#   1.46  row 3  g h i     y0 = 2.52
#   0.50  gap              g's colour-bar ticks and i's x-label sit lower than most
#   1.56  row 4  j k l m   y0 = 0.46
#   0.46  below row 4      row 4's tick labels and its four "marker floor = margin" x-labels
#   ----
#   8.09  canvas, against a 9.30 in ceiling
#
# ROWS 1 AND 2 ARE TALLER THAN THEY WERE (1.18 -> 1.46 and 1.34 -> 1.56). The note above records
# that they were "the shortest row in the deck" and that this is what forced panel d to give up its
# robustness block; that constraint came from a ~5 in ceiling that the caption move has removed.
# Nothing they plot changed and no type was resized, so the whole effect is that the same
# annotations now have 24 and 16 per cent more vertical room than they were tuned in.
#
# THE TWO ROW HEIGHTS ARE 1.46 AND 1.56 FOR REASONS, NOT TO FILL THE PAGE.
#   1.46 is panel a's own WIDTH, so a is exactly square. a is a phase diagram on two 0-1 axes whose
#   content is the boundary alpha* = B/(A+B), i.e. the identity line: off-square it prints at some
#   angle other than 45 degrees and the panel misdraws the one thing it exists to state. Row 3 is
#   1.46 as well, because g is the measured version of exactly that boundary.
#   1.56 is the tallest row 2 can be before f, a scatter carrying an identity line of its own, is
#   stretched more than a quarter past square (1.56 / 1.27 = 1.23). d wants every inch it can get
#   and would take more; f is what stops it. Row 4 matches row 2 for the same reason rows 1 and 3
#   match: they are the outside argument and its audit, and equal heights say so.
# The remaining 1.21 in of the 9.30 in ceiling is left unclaimed on purpose. A figure authored
# flush against a hard page limit has to be re-laid-out the first time any label grows, and the
# panels above do not get more legible from being stretched away from their own aspect ratios.
# 7.97 in, not 8.09: nine panels instead of thirteen, each taller. See the RECTS note.
W, H = 6.9, 7.09
RECTS = {                     # x0,   y0,   w,    h     (inches, from the bottom left)
    # NINE PANELS SINCE 2026-08-31, and every axes is taller. j to m, the four marker-floor
    # robustness sweeps, left the page for Supplementary Note 4, which already carried all of
    # their content in prose. That freed a whole row, and the height went back into the nine
    # panels that remain rather than off the page: each axes grows from 1.46 or 1.56 in to
    # 1.75 in, which is what pays for this figure's move to a 6.5 pt floor.
    #
    # The x geometry is close to what it was, because it has no slack: the gaps between panels
    # are not margins, they are furniture. In row 1 the 0.60 in after a holds b's two-line row
    # labels and the 0.80 in after b holds b's colour bar and c's y axis; in row 3 the 0.88 in
    # after h holds i's category labels, which are its only y furniture. Those three numbers
    # grew with the type, which is why b, c and i each moved right.
    # THE THREE ROW ORIGINS DROPPED ON 2026-09-01 and the panels did not move relative to each
    # other. Measured against ink rather than against this table, the corridor between two rows
    # was 0.48 and 0.53 in, the second loosest in the deck; Figure 3 runs 0.21 to 0.32 and
    # Figure 1 runs 0.04. Each row carries 0.29 to 0.33 in of x apparatus below its axes and
    # 0.11 in of letter above, so the rows were placed 0.92 in apart to hold 0.40 in of
    # furniture. They are now placed to leave a 0.22 in corridor, bottom-anchored at a 0.06 in
    # page margin, which is what sets H:
    #   0.06  below row 3     (was 0.30)
    #   1.75  row 3  g h i    y0 = 0.39   (was 0.63)
    #   0.22  corridor        (was 0.53)
    #   1.75  row 2  d e f    y0 = 2.76   (was 3.30)
    #   0.22  corridor        (was 0.48)
    #   1.75  row 1  a b c    y0 = 5.17   (was 5.97)
    #   0.06  above row 1     (was 0.14)
    # NO AXES CHANGED HEIGHT. All nine are still 1.75 in, so nothing was re-tuned and the 6.5 pt
    # floor this figure was raised to is untouched; 0.88 in of white left the page.
    "a": (0.55, 5.17, 1.55, 1.75),
    "b": (2.70, 5.17, 1.40, 1.75),   # includes the colour bar, which is stolen from this box
    "c": (4.90, 5.17, 1.93, 1.75),
    "d": (0.58, 2.76, 2.28, 1.75),
    "e": (3.22, 2.76, 1.70, 1.75),
    "f": (5.40, 2.76, 1.43, 1.75),
    "g": (0.60, 0.39, 1.58, 1.75),   # colour bar drawn OUTSIDE to the right, into the gutter
    # h starts 0.20 in further left and is 0.20 in wider. Row 3's two corridors were 0.51 and
    # 0.11 in, the most uneven pair in the figure; this makes them 0.31 and 0.11 and the 0.20 in
    # goes into h's axes, since the row already spans 0.18 to 6.88 and has no slack to reclaim.
    "h": (2.85, 0.39, 1.82, 1.75),
    "i": (5.55, 0.39, 1.28, 1.75),   # its category labels ARE its y furniture, 0.88 in of them
}
# BANNER_Y was here until 2026-09-01: three row-banner positions, referenced nowhere in this
# file or any other, left behind when the row headings moved into the caption. It also still
# held the pre-2026-08-31 canvas height, so a reader checking the geometry against it would
# have been reading a number two revisions stale.
# the panel letter must clear its own panel's y-axis furniture, which differs a lot between a bare
# strip (e) and a heat map with two-line row labels (b); given here in inches to the LEFT of the
# axes box and converted to the axes-fraction dx that panel_letter() wants
# a: 0.32, not 0.21. With no title above the axes the letter sits on the top tick label's
# baseline, and 0.21 in put it on panel a's "1.0".
# g: 0.40, not 0.36. dx is a fraction of the axes box, and the colour bar shrinks g's axes to about
# 0.91 of the box RECTS gives it, so the offset that reaches the page is 0.91 of the number here.
# i: 0.75, which puts the letter on the left edge of the widest row label rather than on top of it.
# That is 4.60 in absolute, 0.10 in clear of h's right edge at 4.50, and it is the one letter in
# the figure positioned by a measured label rather than by the y-axis furniture, because i has no
# y-axis furniture: its categories ARE the labels.
LETTER_IN = {"a": 0.32, "b": 0.56, "c": 0.36, "d": 0.42, "e": 0.30, "f": 0.44,
             "g": 0.40, "h": 0.34, "i": 0.75}


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
    fns = {"a": draw_4b, "b": draw_4f, "c": draw_shape,
           "d": draw_gate2, "e": draw_nat_gate1, "f": draw_nat_premise,
           "g": draw_ed6b, "h": draw_ed6c, "i": draw_ed6d}
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
    # manuscript/latex/figures/fig4.pdf. Writing only through save() means every path that can
    # produce that file also has to pass the floor.
    from figstyle import apply_style, panel_letter, save
    save(build(apply_style, panel_letter), os.path.join(HERE, STEM))
    print(f"wrote {STEM}.pdf / .svg / .png")
