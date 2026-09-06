"""PopRetrieve Figure 3: the population advantage weakens, and can change direction, once the
judge stops sharing the retrieval objective.

ARCHETYPE: quantitative grid with two hero panels (a and h). Eleven panels, five rows,
one argument. Four numbers are its skeleton, and everything else on the
page exists to support or to qualify one of them:

    +0.028   response matching: population retrieval wins, narrowly          (a)
     0.000   mechanism recovery, the SAME rankings: the advantage is gone    (a, b)
    +0.265   external functional similarity: a real population signal        (h)
    +0.105   after the response-magnitude channel is partialled out          (h, i)

  Row 1  a | b   The collapse, and that it is distribution-wide rather than an outlier artifact.
  Row 2  c | g   The gain that does exist is graded by true response divergence, and it is small,
                 across 765 stratified queries and across 239 real-data tasks.
  Row 3  d | e | f   The same divergence axis under a judge that does not share the retrieval
                 objective (d), and then the two ways the pre-specified diagnostic fails to find
                 that axis: it does not enrich for the gain (e), and its reliability score runs
                 opposite to true divergence while its verdict inherits the inversion (f).
  Row 4  h | i   The external functional readout, in aggregate and per query.
  Row 5  j | k   What the endpoint choice does, and the channel that explains it.

THE 2026-09-03 RESTRUCTURE OF ROW 3
------------------------------------
Row 3 used to be three panels arguing that the pre-specified diagnostic fails. Two things made
that wrong. First, panel c reversed: with exp16's merge rebuilt from the U-arm exp12, true
response divergence DOES grade the minority-coverage gain (Spearman rho = +0.141, p = 1e-04,
against +0.050 and p = 0.165 before), so the figure could no longer say that neither the axis nor
the gate locates the gain. Second, two of the three panels drew the same x axis, true response
divergence, from the same file, and paid for it twice.

So the row now holds one panel about the AXIS and two about the GATE. The axis panel, d, is the
mechanism-recovery gain by the same divergence quartiles; it was Figure 5 panel g until Figure 5
was rebuilt around the intervention-retrieval benchmark, and beside c it is the control that stops
c's positive trend being read as a biological result. The two gate panels are the old d, unchanged
in content, and a merge of the old e and f onto their shared axis.

What the figure argues in row 3 is therefore one sentence rather than two: **the biological axis
does some work, and what failed is the surrogate we built to identify it.**

THE 2026-08-31 REBUILD
----------------------
Three things changed that are about the argument rather than the drawing.

  * COLOUR WAS ENCODING THE WRONG VARIABLE, in the figure's most important panel. Panel a draws
    two distributions of the SAME quantity, the population-minus-mean advantage on the same 480
    queries; only the judge differs. They were blue and orange, the deck's colours for population
    and mean retrieval, so the panel said the right-hand distribution was the mean method. Panel e
    coloured the gate's reliability axis orange and panels j and k coloured the MoA-nDCG evaluator
    orange, and none of the three is a mean-signature retriever. fig3_style now makes blue and
    orange a statement about SIGN, carried by half-planes behind a neutral distribution, and
    reserves them as object colours only where methods are genuinely compared.

  * PANEL c NO LONGER CLAIMS "NEGLIGIBLE", because that word depended on a chosen denominator.
    The largest quartile mean is 0.5 per cent of the nominal [0, 1] metric range and 43 per cent
    of the metric's own interquartile range. Picking the flattering denominator is the error this
    paper exists to criticise, so the panel draws point estimates with intervals and makes no size
    claim at all. What the data supported without a choice in August was that the gain did not
    grow with divergence; under the repaired estimator it does, and the panel and its assertions
    were rewritten on 2026-09-03 to state the pattern that replaced it.

  * PANEL g NO LONGER LETS A MEAN STAND FOR A SHIFT. The constructed cross-line mixtures have the
    largest dataset mean, +0.00426, and a median of exactly 0.000 with only 18 per cent of tasks
    above zero; the within-line tasks have 56 per cent above zero at a mean of +0.00038. The mean
    is a few large positives, not a broad advantage, and 102 of the 239 tasks select the same
    candidate under both methods. The panel now shows the tasks, not only their means.

THE POWER PANELS LEFT THE PAGE, 2026-08-31. Two panels used to sit between rows 4 and 5, showing
achieved power and the queries needed for 80 per cent power in the highest response-divergence
quartile. They answered the one objection this paper's central negative result invites, and they
answered it well, but they are third-tier diagnostics and they cost a whole row on a page whose
argument is rows 1 to 4. Their numbers moved to Supplementary Note 2 in full, so nothing is lost:
achieved power 1.00 for minority-state coverage against 0.06 for MoA-nDCG, and 45 queries needed
against 20,844, a difference driven by a twelvefold gap in standard deviation rather than by effect
size. The Results now cite that Note rather than the figure.

Removing them took the canvas from 9.20 to 7.96 in, a 13.5 per cent shorter page, and lifted panel
a from 15.6 to 17.5 per cent of panel area without changing any other panel's size. The surviving
l and m were relabelled j and k.

Panels j and k are re-authored from the retired Extended Data module ed5/ed5.py (draw_a and
draw_b), reading the same file, because that module sets 5.2 to 5.6 pt type and this figure has a
6.5 pt floor.

GEOMETRY, IN INCHES ON THE PRINTED PAGE
---------------------------------------
Authored at 6.90 in, the width it prints at, so nominal point size IS printed point size. The
float budget is the 9.461 in text block less about 16/72 in of float overhead, i.e. 9.238 in, so
the canvas is 9.20 in and exports at 9.22.

Thirteen panels on one page is genuinely tight, and the ledger says so honestly rather than
pretending otherwise: rows 5 and 6 give their panels under 0.65 in of axes height. That is the
budget, and the response to it is to cut annotation into the caption, never to shrink type. Row
widths are unequal inside a row because the panels are: g needs width for 239 tasks spread about
zero, h needs a label column for five method rows, and b, d and i do not.

Rebuild: python fig3_assemble.py
"""
import os
import re
import sys

import matplotlib.pyplot as plt
import matplotlib.text as mtext

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# The one canonical output stem; build_all.STEMS[3] holds the same string and the build fails if
# the two drift apart. This is the name copied to manuscript/latex/figures/fig3.pdf.
STEM = "fig3_collapse"

from figstyle import pin_canvas, strip_titles  # noqa: E402
from fig3_style import PT_ANNOT, PT_FLOOR, PT_LETTER, PT_TICK, PT_TITLE, TEXT  # noqa: E402

from fig3a import draw_3a  # noqa: E402
from fig3b import draw_3b  # noqa: E402
from fig3c import draw_3c  # noqa: E402
from fig3d import draw_3d  # noqa: E402
from fig3e import draw_3e  # noqa: E402
from fig3f import draw_3f  # noqa: E402
from fig3g import draw_3g  # noqa: E402
from fig3h import draw_3h  # noqa: E402
from fig3i import draw_3i  # noqa: E402
from fig3j import draw_3j  # noqa: E402
from fig3k import draw_3k  # noqa: E402

# ------------------------------------------------------------------------------------------
# The inch ledger
# ------------------------------------------------------------------------------------------
FIGW = 6.90

PAD_TOP, PAD_BOT = 0.05, 0.04
# The panel letter alone. It was 0.24 in while every panel also stated a bold conclusion phrase;
# removing those phrases (see fig3_style) returns 0.42 in to the six rows, which is most of what
# made rows 5 and 6 cramped. The height a figure spends on sentences is height it does not spend
# on evidence.
LETTER_BLOCK = 0.16
# 0.09, not 0.16, since 2026-09-04. The 2026-09-01 note below is still the right reading of this
# figure and is kept: the bottom pads have no slack (the smallest unused pad in a row runs -0.03
# to 0.05 in, i.e. the x apparatus fills them), so the only white here to reclaim is the gap
# itself. Re-measured on the render at 0.16: the four corridors between rows, from the last ink
# above to the first ink below, were 0.34, 0.31, 0.33 and 0.37 in, and the letter that has to sit
# in them is 0.09 in of ink. At 0.09 they are 0.27 to 0.30 in, which still leaves 0.09 to 0.12 in
# of white above each letter. The binding case is unchanged: the row 1 to row 2 boundary is set
# by c's x label, which already sits 0.01 in below its own box.
ROW_GAP = 0.09

# (row height in inches, [(key, box width in inches), ...]). Box widths sum to FIGW per row.
# TWO HERO ROWS, 2026-08-31. Row heights are not a taste decision: they were measured against
# this figure's own tiering and found inverted. The tier-3 diagnostics (e, f, j, k)
# averaged 6.6 per cent of panel area against 6.1 per cent for the four tier-2 panels, and k and
# m were drawn as large as i, a discovery panel. A page that gives its diagnostics discovery
# weight tells the reader the wrong thing before they read a single label.
#
# Rows 1 and 4 hold the four numbers that are this figure's skeleton, so they take the height,
# and the two diagnostic rows give it up. The total is unchanged at 6.95 in, so nothing outside
# these six numbers moves. Resulting area share: a 13.1 -> 15.6 per cent, h 11.0 -> 13.1,
# k 7.9 -> 5.9, m 7.7 -> 6.0; tier 1 averages 12.0 per cent against tier 3's 5.2.
# PANELS NOW READ IN THEIR OWN ORDER, 2026-09-04. The page ran a b c g d e f h i j k: g sat in
# the second half of row 1 and the reader met it fourth. The fix is a swap of position and not of
# content, so every panel keeps its letter and its draw function; only which box it is handed
# changes. g moves down one row into the second half of row 2, whose box is 2.75 to 6.90 in and
# therefore the SAME box it had in row 1, to the hundredth: g is redrawn at its own width and its
# x limit, its summary column and its two visibility assertions are untouched. c, d and e share
# row 1 and f takes the first half of row 2.
#
# Why not the narrow slot for g. Its summary column is absolute, not fractional: a 0.24 in
# task-split bar and a 0.38 in mean value at 6.8 pt, so it needs 0.66 in of column whatever the
# panel is worth, and it reserves 0.241 of its axes for them. In a 2.40 in box, after the 1.02 in
# of dataset names, that column would be 0.33 in and the values would have to shrink or overlap.
# f takes the wider half instead, which is the same swap read from the other side.
#
# ROW HEIGHTS. Rows 1 and 2 are re-cut around the new occupants and cost 0.01 in in total: c and
# d are the same drawing, four divergence quartiles with an interval each, and c has been running
# at 0.80 in of axes for them, so 0.90 in is not a squeeze; f's cloud gives up 0.10 in of height
# and gains 0.35 in of width. Rows 0, 3 and 4 are unchanged, because their panels fill them.
ROWS = [
    (1.52, [("a", 4.00), ("b", 2.90)]),
    # PANEL LETTERS RE-ASSIGNED 2026-09-05, and the reason is the Results, not the page.
    # The text runs a and b, then the 239-task minority-coverage result, then that result
    # STRATIFIED by divergence, then the two diagnostic panels. The figure ran the
    # stratification first and the result it stratifies fifth, so the reader met Fig. 3g third
    # and the base number after its own quartiles. Nature also asks for panels in citation
    # order, and Figure 4 was re-cut for the same reason a day earlier.
    #
    # WHAT MOVED. Only the letter-to-content assignment; every panel is redrawn by its own
    # unchanged draw function at a box it can take, and DRAW below is the one place the new
    # assignment is written down. The 239-task panel keeps the 4.15 in box it was measured for
    # (see the width note below), so its summary column is untouched to the hundredth; it is
    # now the FIRST panel of row 2 rather than the second.
    (1.42, [("c", 4.15), ("d", 2.75)]),
    # The two divergence quartile panels are now the last of row 2 and the first of row 3
    # rather than side by side. That is the one cost of the re-assignment and it is real: they
    # are the same drawing under two judges. It is unavoidable at this width, because the
    # 239-task panel needs 4.15 in and 4.15 + 2.45 + 2.45 does not fit 6.90 in.
    #
    # d gains 0.30 in of width over the box it had as c, and e and f keep theirs. g gives up
    # 0.30 in of width and 0.10 in of height against the box it had as f; its cloud and its
    # verdict strip were re-measured on the render at the new size and its own assertions and
    # figures/check_overlaps.py both pass.
    (1.32, [("e", 2.45), ("f", 2.00), ("g", 2.45)]),
    (1.46, [("h", 4.10), ("i", 2.80)]),
    # Row 5 is unchanged, and deliberately so. The text used to cite k before j; the figure's
    # order here is what the endpoint choice does and then the channel that explains it, which
    # is the right order, so the two sentences in the Results were exchanged instead.
    (0.92, [("j", 3.60), ("k", 3.30)]),
]

# (left, right, bottom) pad in inches inside the panel BOX. Top is always zero: the phrase is
# drawn at transAxes y = 1.0 and sits in the LETTER_BLOCK band. Left pads hold the panel's y
# apparatus plus 0.24 in reserved for the letter, and they differ because the apparatus does:
# h and l carry a column of method names, b c e f i j k m carry a rotated label plus numeric
# ticks, and a and d carry a rotated label only.
# LEFT PADS OF THE SECOND-COLUMN PANELS WERE CUT ON 2026-09-01 to a common rule: keep the
# measured furniture plus 0.14 in for the letter, and give the rest back as axes width. Measured
# unused left pad was b 0.24, e 0.25, i 0.19, k 0.49 in; k's alone made the j|k corridor 0.59 in,
# the widest in the deck. First-column pads are NOT cut: their slack is the page margin, which is
# already 0.01 in here, and cutting them would push ink off the left edge.
# EACH PAD BELONGS TO THE PANEL'S CONTENT, NOT TO ITS LETTER, so the 2026-09-05 re-assignment
# carried them along: the 1.02 in left pad measured for the 239-task panel's dataset names is now
# c's, and the 0.78 in measured for the first divergence quartile panel is now d's.
PADS = {"a": (0.74, 0.10, 0.42), "b": (0.60, 0.10, 0.44),
        "c": (1.02, 0.10, 0.42),                      # the 239-task panel, was g
        "d": (0.78, 0.10, 0.40),                      # divergence quartiles, objective-aligned, was c
        "e": (0.72, 0.10, 0.42), "f": (0.76, 0.10, 0.42),   # was d, was e
        "g": (0.74, 0.10, 0.42),                      # the diagnostic cloud and its strip, was f
        "h": (1.34, 0.10, 0.36), "i": (0.67, 0.10, 0.38),
        "j": (1.20, 0.10, 0.38), "k": (0.37, 0.10, 0.38)}


# Panel g is drawn on TWO axes that share one x range: a strip carrying the gate's thresholded
# verdict over a cloud carrying its continuous score. Figure 2 panel d uses the same construction
# and the same two constants. It was panel f until 2026-09-05; the constants keep their names
# because they name the STRIP, which did not move.
STRIP_LETTER = "g"
F_STRIP_H, F_STRIP_GAP = 0.32, 0.06


def _boxes():
    """Resolve the rows into per-panel axes rects, in inches, measured from the FIGURE TOP.

    Returns (FIGH, rects, letters, box_left). ``box_left`` is the inch coordinate of each panel
    BOX's left edge, which is not recoverable from its axes rect once a panel is not the leftmost
    of its row: fig3e places its row labels in the pad to the left of its axes and has to know
    where that pad starts. build() stamps it onto the axes.
    """
    rects, letters, box_left = {}, {}, {}
    y = PAD_TOP
    for row_h, panels in ROWS:
        assert abs(sum(w for _, w in panels) - FIGW) < 1e-9, panels
        y += LETTER_BLOCK
        x0 = 0.0
        for k, box_w in panels:
            letters[k] = (x0, y)
            box_left[k] = x0
            left, right, bottom = PADS[k]
            ax_x, ax_w = x0 + left, box_w - left - right
            if k == STRIP_LETTER:
                rects[f"{k}_top"] = (ax_x, y, ax_w, F_STRIP_H)
                rects[k] = (ax_x, y + F_STRIP_H + F_STRIP_GAP, ax_w,
                            row_h - F_STRIP_H - F_STRIP_GAP - bottom)
                box_left[f"{k}_top"] = x0
            else:
                rects[k] = (ax_x, y, ax_w, row_h - bottom)
            x0 += box_w
        y += row_h + ROW_GAP
    return y - ROW_GAP + PAD_BOT, rects, letters, box_left


FIGH, RECTS, LETTER_XY, BOX_LEFT = _boxes()


def _letter(fig, key):
    """Panel letters in the gutter, one baseline per row, at this figure's own 9.5 pt.

    Figure coordinates rather than a transAxes offset: this figure has eleven distinct axes
    widths, and a fixed dx would put the letter a different distance out on each of them.
    """
    x0, row_top = LETTER_XY[key]
    fig.text(x0 / FIGW, 1.0 - (row_top - 0.04) / FIGH, key,
             fontsize=PT_LETTER, fontweight="bold", va="bottom", ha="left", color=TEXT)


_SUBSUP = re.compile(r"\$[^$]*[\^_][^$]*\$")


def _assert_floor(fig, floor=PT_FLOOR):
    """Refuse to return a figure carrying text below THIS figure's floor.

    figstyle.save() enforces the deck's 5 pt production limit. This is stricter and runs earlier:
    5 pt is what production rejects, 6.5 pt is what a reader can take in at 183 mm. Mathtext is
    measured at its effective size, a sub/superscript printing at 0.7x nominal.

    Thirteen panels on one page makes this the deck's tightest figure, which is exactly why the
    gate is here. The fix when it fires is to CUT the annotation into the caption.
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
        f"Figure 3 sets its own {floor} pt floor and these are under it: {sorted(bad)[:8]}. "
        f"Cut the annotation into the caption; do not lower the size.")
    return fig


def _assert_no_titles(fig, cap=PT_ANNOT):
    """Refuse to return a figure in which any PANEL draws text above ``cap``.

    This is the mechanical form of the rule in fig3_style: the panels carry evidence and the
    caption carries the argument. A conclusion sentence set over a panel is always the largest
    text on it, so capping panel text at the annotation size is what stops one coming back. The
    panel letters are exempt because fig3_assemble draws them, not the panels, and they are the
    figure's navigation rather than its claims.

    It is deliberately a size gate and not a wording gate. Nothing here can tell a claim from a
    label, but a claim that has to fit at 7.2 pt beside the marks it describes is a caption
    sentence that has already lost the argument for being on the panel.
    """
    letters = {t for t in fig.texts}
    bad = []
    for t in fig.findobj(mtext.Text):
        if t in letters or not str(t.get_text()).strip() or not t.get_visible():
            continue
        if t.get_fontsize() > cap + 1e-6:
            bad.append((round(t.get_fontsize(), 2), str(t.get_text()).replace("\n", "/")[:44]))
    assert not bad, (
        f"Figure 3 caps panel text at {cap} pt and these are above it: {sorted(bad)[:8]}. "
        f"A panel states no conclusion; move the sentence to the caption.")
    return fig


# THE LETTER-TO-CONTENT MAP, and since 2026-09-05 the module names no longer match the letters.
# Five panels shifted (see the ROWS note) and the modules were NOT renamed with them, following
# fig4_assemble, which carries the same mismatch for the same reason: a module name is an internal
# identifier and a panel letter is a manuscript-facing label, and coupling them means every
# citation-order fix renames files and rewrites imports. The map is written out one per line so
# the mismatch is visible here rather than something to rediscover in a traceback.
DRAW = {"a": draw_3a,        # class A against class B, the two judges
        "b": draw_3b,        # the same per cell line
        "c": draw_3g,        # 239 tasks, minority-state coverage      <- was panel g
        "d": draw_3c,        # divergence quartiles, objective-aligned <- was panel c
        "e": draw_3d,        # divergence quartiles, mechanism recovery <- was panel d
        "f": draw_3e,        # recommended against declined            <- was panel e
        "g": draw_3f,        # the diagnostic's own reliability, with its verdict strip <- was f
        "h": draw_3h,
        "i": draw_3i,
        "j": draw_3j,
        "k": draw_3k}


def build(apply_style, panel_letter):
    # This figure's ladder sits one step above the deck's (8, 7, 6). panel_letter is accepted to
    # keep build_all's contract and deliberately not used: its size is fixed at 8 pt.
    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    fig = plt.figure(figsize=(FIGW, FIGH))
    pin_canvas(fig)

    def _axes(key):
        x, top, w, h = RECTS[key]
        ax = fig.add_axes([x / FIGW, 1.0 - (top + h) / FIGH, w / FIGW, h / FIGH])
        # Every panel is told where its own BOX starts, because a panel that draws in the pad to
        # the left of its axes cannot infer that once it is not the leftmost of its row.
        ax.panel_box_left_in = BOX_LEFT[key]
        return ax

    for key, fn in DRAW.items():
        if key == STRIP_LETTER:
            fn(_axes(key), _axes(f"{key}_top"))
        else:
            fn(_axes(key))
        _letter(fig, key)

    # strip_titles clears rc titles so a standalone preview can label itself without the composite
    # inheriting it. The one phrase each panel states over itself is drawn ink via fig3_style.title
    # and survives on purpose.
    return _assert_no_titles(_assert_floor(strip_titles(fig)))


if __name__ == "__main__":
    # build() must NOT export. Every export goes through figstyle.save(), which applies the
    # deck-wide 5 pt floor first; a savefig here would ship a figure that never met the gate.
    from figstyle import apply_style, panel_letter, save
    save(build(apply_style, panel_letter),
         os.path.join(os.path.dirname(os.path.abspath(__file__)), STEM))
    print(f"wrote {STEM}.pdf / .svg / .png  ({FIGW} x {FIGH:.2f} in)")
