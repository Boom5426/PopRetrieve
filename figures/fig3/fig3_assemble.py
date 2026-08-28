"""PopRetrieve Figure 3: under objective-aligned metrics, distributional retrieval looks decisively stronger.

Six panels in two rows. The top row carries the claim (a, the Hit@1 ladder), its counterexample
(b, Frangieh) and its per-query distribution (c); the bottom row holds the three supporting controls
(d gate, e alpha sweep, f metric robustness).

Geometry note (why the numbers below are in inches, not gridspec units)
----------------------------------------------------------------------
The manuscript text block is 6.93 in wide and the figure enters with
``\\includegraphics[width=\\textwidth]``. This composite used to be authored 11.0 in wide, so LaTeX
shrank it by 0.63x and the 6 pt panel annotations printed at 3.8 pt, under the 5 pt Nature Portfolio
floor. The build-time gate in ``figstyle.save`` only sees NOMINAL sizes, so it reported CLEAN while
the printed page failed. The fix is to author at final print width: the canvas is 6.9 in, the scale
factor is 1.0, and nominal point size == printed point size.

At 1:1 the horizontal budget is real, so the layout is specified as an explicit inch ledger rather
than a uniform 12-column grid: panels a and f are horizontal bar charts whose category labels
("coverage-worst") need ~0.62 in of clearance, which a uniform column gutter cannot give them
without starving the other four panels. Each row is a 5-cell gridspec of
``[panel, gutter, panel, gutter, panel]`` with ``wspace=0``, so every width below is literally
inches on the printed page.

This gain is objective-aligned (Class A); it is NOT independent validation, which is Figure 4.
"""
import os, sys, matplotlib.pyplot as plt

# ONE canonical output stem per figure. This file used to write fig3_apparent_gains.* while
# build_all.py wrote the same figure as fig3_temptation.*, so the composite existed on disk twice
# under two names and nothing said which was current. build_all's STEMS entry is the one that is
# copied to manuscript/latex/figures/fig3.pdf, so that is the name kept here; build_all checks
# this constant against its own STEMS dict and fails the build if the two ever drift apart again.
STEM = "fig3_temptation"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fig3a import draw_3a
from fig3b import draw_3b
from fig3c import draw_3c
from fig3d import draw_3d
from fig3e import draw_3e
from fig3f import draw_3f

DRAW = {"a": draw_3a, "b": draw_3b, "c": draw_3c,
        "d": draw_3d, "e": draw_3e, "f": draw_3f}

# ---- the inch ledger -----------------------------------------------------------------------
FIG_W, FIG_H = 6.9, 5.8            # 6.9 in <= 6.93 in text block: printed 1:1
M_LEFT = 0.70                      # holds panel a "coverage-worst" y tick labels
M_RIGHT = 0.06
M_TOP = 0.42                       # two-line panel titles + panel letters
M_BOT = 0.60                       # two-line x labels (c, e, f) and three-line x ticks (d)
ROW_GAP = 0.95                     # row-1 x labels + row-2 titles and letters
USABLE = FIG_W - M_LEFT - M_RIGHT  # 6.14 in of drawable width per row

# [panel, gutter, panel, gutter, panel]; gutters sized by what the RIGHT neighbour needs
ROW1 = [1.757, 0.42, 1.757, 0.45, 1.756]      # a | b | c
ROW2 = [1.450, 0.50, 1.830, 0.74, 1.620]      # d | e | f   (0.74 = f's long category labels)
assert abs(sum(ROW1) - USABLE) < 1e-6, sum(ROW1)
assert abs(sum(ROW2) - USABLE) < 1e-6, sum(ROW2)

ROW_H = (FIG_H - M_TOP - M_BOT - ROW_GAP) / 2.0
LETTER_OFFSET_IN = 0.22            # panel letters sit a constant 0.22 in left of their axes


def build(apply_style, panel_letter):
    apply_style(sizes=(8, 7, 6))   # 8 pt titles, matching figs 1, 2, 4 and 6
    fig = plt.figure(figsize=(FIG_W, FIG_H))

    left, right = M_LEFT / FIG_W, 1.0 - M_RIGHT / FIG_W
    r1_top = 1.0 - M_TOP / FIG_H
    r1_bot = r1_top - ROW_H / FIG_H
    r2_top = r1_bot - ROW_GAP / FIG_H
    r2_bot = r2_top - ROW_H / FIG_H

    gs1 = fig.add_gridspec(1, 5, width_ratios=ROW1, wspace=0,
                           left=left, right=right, top=r1_top, bottom=r1_bot)
    gs2 = fig.add_gridspec(1, 5, width_ratios=ROW2, wspace=0,
                           left=left, right=right, top=r2_top, bottom=r2_bot)

    # panel -> (gridspec, cell index, axes width in inches)
    PLACE = {"a": (gs1, 0, ROW1[0]), "b": (gs1, 2, ROW1[2]), "c": (gs1, 4, ROW1[4]),
             "d": (gs2, 0, ROW2[0]), "e": (gs2, 2, ROW2[2]), "f": (gs2, 4, ROW2[4])}

    for k, (gs, col, w_in) in PLACE.items():
        ax = fig.add_subplot(gs[0, col])
        DRAW[k](ax)
        panel_letter(ax, k, dx=-LETTER_OFFSET_IN / w_in, dy=1.19, case="lower")

    out = os.path.dirname(os.path.abspath(__file__))
    return fig


if __name__ == "__main__":
    # build() must NOT export. It used to call fig.savefig() here, which meant two things:
    # `python figures/build_all.py` without --write, documented as a report-only dry run,
    # silently overwrote four tracked composites; and it wrote them BEFORE
    # assert_min_fontsize ran, so a figure that then FAILED the gate had already been
    # deployed to disk. Every export now goes through figstyle.save(), which applies the
    # 5 pt floor first. (Audited 2026-07-27; fig1 and fig5 already worked this way.)
    from figstyle import apply_style, panel_letter, save
    save(build(apply_style, panel_letter),
         os.path.join(os.path.dirname(os.path.abspath(__file__)), STEM))
    print("wrote fig3 composite")
