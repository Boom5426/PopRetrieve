"""DART Figure 2: mean-signature retrieval is the zero-variance limit of distribution-aware retrieval.

Assembles panels a-f into fig2_collapse.{png,pdf}. Reproducible entry point; the build harness
(figures/build_all.py) calls build() and additionally enforces the 5 pt typography floor.

Layout logic. The claim runs left to right and top to bottom: a defines the generative model and
shows that the population score becomes the mean-to-mean score, b isolates lambda as the only thing
that moves, c measures that collapse on data, e shows the same collapse along the beta axis, and f
is the synthesis. a/c/e therefore hold the wide (7/12) column and b/d/f the narrow (5/12) one, and
the schematic first row is shorter than the two data rows. A 12-column grid gives that unequal
split while keeping a single vertical alignment seam between the two columns.
"""
import os, sys, matplotlib.pyplot as plt

# ONE canonical output stem per figure. This file used to write fig2_unification.* while
# build_all.py wrote the same figure as fig2_collapse.*, so the composite existed on disk twice
# under two names and nothing said which was current. build_all's STEMS entry is the one that is
# copied to manuscript/latex/figures/fig2.pdf, so that is the name kept here; build_all checks
# this constant against its own STEMS dict and fails the build if the two ever drift apart again.
STEM = "fig2_collapse"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from figstyle import pin_canvas
from fig2a import draw_2a
from fig2b import draw_2b
from fig2c import draw_2c
from fig2d import draw_2d
from fig2e import draw_2e
from fig2f import draw_2f

# EXPORT GEOMETRY. The canvas is the authored print width and the tight bbox is pinned to it, so
# the exported page is 6.92 x 5.80 in (canvas + savefig.pad_inches on each side) BY CONSTRUCTION.
# It used to be a 7.09 x 5.95 in canvas whose exported width was whatever savefig's tight crop
# happened to leave, which landed at 6.890 in: 0.035 in of slack to the 6.93 in text block, held by
# nothing. Any later annotation reaching further right would have pushed the page past the text
# block, LaTeX would have scaled the figure DOWN, and the deck's 5 pt floor would have been breached
# again at printed size with the build still reporting CLEAN (the gate measures nominal sizes only).
#
# The panels did not move. The canvas was cropped to what the ink needs, and the gridspec span was
# translated by the same amount, so every panel keeps its absolute position and size to <0.001 in;
# only the empty margin the old crop discarded is gone.
#
# The span below is positioned so the ink is CENTRED in what is left: this figure's ink is 6.870 in
# wide (measured off the rendered PDF, not off the Agg tight bbox, whose text metrics run ~0.013 in
# narrower), so a 6.90 in canvas leaves 0.030 in of total slack and the ink clears each side edge by
# 0.015 in. With the bbox pinned that clearance is the safety margin that matters: an overhang no
# longer gets absorbed by the crop, it enlarges the exported page. Re-measure it after any change
# that adds ink near an edge, by rasterising the deployed PDF and locating the first non-white
# column, rather than by trusting get_tightbbox.
FIG_W, FIG_H = 6.90, 5.78
GS_LEFT_IN, GS_RIGHT_IN = 0.39408, 6.88852      # was 0.51048, 7.00492 on the 7.09 in canvas
GS_TOP_IN, GS_BOTTOM_IN = 5.53775, 0.36125      # was 5.62275, 0.44625 on the 5.95 in canvas

# (row, col-slice, letter, draw fn, panel-letter x offset)
PANELS = [
    (0, slice(0, 7), "a", draw_2a, -0.030),
    (0, slice(7, 12), "b", draw_2b, -0.185),
    (1, slice(0, 7), "c", draw_2c, -0.098),
    (1, slice(7, 12), "d", draw_2d, -0.085),
    (2, slice(0, 7), "e", draw_2e, -0.098),
    (2, slice(7, 12), "f", draw_2f, -0.085),
]


def build(apply_style, panel_letter):
    apply_style(sizes=(8, 7, 6))
    fig = plt.figure(figsize=(FIG_W, FIG_H))
    # Pin the tight bbox to the authored canvas (see EXPORT GEOMETRY in the module docstring).
    pin_canvas(fig)
    # The gridspec span is given in inches and converted, because what has to stay fixed under the
    # canvas change is the ABSOLUTE panel geometry, not the fractions.
    gs = fig.add_gridspec(3, 12, height_ratios=[0.90, 1.0, 1.0],
                          hspace=0.66, wspace=0.60,
                          left=GS_LEFT_IN / FIG_W, right=GS_RIGHT_IN / FIG_W,
                          top=GS_TOP_IN / FIG_H, bottom=GS_BOTTOM_IN / FIG_H)
    for r, cs, k, fn, dx in PANELS:
        ax = fig.add_subplot(gs[r, cs])
        fn(ax)
        panel_letter(ax, k, dx=dx, dy=1.20, case="lower")
    out = os.path.dirname(os.path.abspath(__file__))
    fig.savefig(os.path.join(out, STEM + ".png"), dpi=300, bbox_inches="tight")
    fig.savefig(os.path.join(out, STEM + ".pdf"), bbox_inches="tight")
    return fig


if __name__ == "__main__":
    from figstyle import apply_style, panel_letter
    build(apply_style, panel_letter)
    print("wrote fig2 composite")
