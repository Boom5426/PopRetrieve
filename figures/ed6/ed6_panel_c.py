"""PopRetrieve Figure 4, panel g: the distributional advantage across the synthetic grid.

Source data: results/exp11_synthetic_phase_diagram/dart_advantage_grid.csv
Run standalone: python3 ed6_panel_c.py

WHAT THE PANEL SHOWS
--------------------
A 9 x 4 field of energy-minus-mean Hit@1 over the conflict (lambda) by minority-fraction (alpha)
grid: one cell per (lambda, alpha) pair, read straight from the source file at draw time. No value
in this module is typed. Blue is where population-level (energy) retrieval wins, orange is where
mean-signature retrieval wins, which is the figure-wide colour contract in fig4_style, carried here
by figstyle's DIVMAP_SOFT: it is built from those same two hues, so the map is imported rather than
rebuilt and a recolour of the deck moves this panel with it.

The colour limits are +-1 and they are not a display choice made to look good: the quantity is a
difference of two Hit@1 rates, so it is bounded on [-1, 1] by construction. The scale therefore
shows the reader the whole space the statistic could have occupied, and the field's own extremes go
in the caption.

2026-08-31 TYPOGRAPHY PASS: THE 6.5 pt FLOOR
--------------------------------------------
This panel was joint worst in the figure, with 23 artists under 6.5 pt and the only text in Figure 4
at exactly 5.0 pt, which is the hard production limit rather than a size a reader can take in at
183 mm. All 23 were raised, none by shrinking anything else to pay for it:

  * the nine colour-bar tick labels, 5.0 pt, the worst text in the figure. They are now set at
    PT_TICK (6.8) and there are five of them rather than nine: the locator is derived from the
    colour limit, not typed, and five labels on a 1.75 in bar leave 0.44 in between baselines
    instead of 0.22 in. Nothing was lost with the four that went; they were intermediate gradations
    of a scale whose ends and centre are still labelled.
  * the nine y (lambda) tick labels, 5.5 pt, and the four x (alpha) tick labels, 6.0 pt. Both local
    sizes are deleted, so the house ladder applies (PT_TICK, 6.8), which is what the other eight
    panels of this figure use.
  * the colour-bar label, 5.5 pt -> PT_SMALL (6.5).

No label in this panel contains a mathtext sub/superscript, so none of them needed the hand-composed
two-artist treatment that fig1a.py uses: alpha, lambda and the minus sign print at their nominal
size, and the minus is a real U+2212 rather than a mathtext "$-$", which in this face measures 90
per cent of an em dash.

WHAT WAS CUT, AND WHERE IT GOES
-------------------------------
  * The standalone title "Distributional advantage is regime-dependent" is deleted. It is a
    conclusion, this figure's panels state none, and fig4_assemble._assert_no_titles enforces that.
    The sentence belongs in the caption.
  * The colour-bar label was two lines, "energy - mean" over "Hit@1". At 6.5 pt, rotated, two lines
    cost 0.11 in more of the right-hand gutter than the panel can spend without crowding panel h.
    It is one line now, "Hit@1: energy - mean", which is also the less ambiguous reading of the two:
    the difference is between two Hit@1 rates, not between an energy and a mean Hit@1.
  * The four intermediate colour-bar ticks, as above.

PER-CELL NUMBERS: NOT ADDED
---------------------------
The 36 cells carry no printed value and none was added. Colour is the field here, the bar states the
scale, and the caption carries the extremes; 36 numbers at PT_SMALL would fit the 0.40 x 0.19 in
cells geometrically but would print a table over a phase diagram and bury the boundary the panel
exists to show. Neither was anything shrunk to make them fit: the choice is to have no numbers at
full size, never numbers below the floor.

THE NEW BOX
-----------
The axes is 1.58 x 1.75 in, up from 1.50 x 1.46 when four panels left this figure for Supplementary
Note 4 and the freed row went back into the nine that remain. Two things were re-tuned for it:

  * the colour bar no longer steals its width from the axes. It used to be placed with
    fraction=0.046, which shrank the heat map to about 0.91 of its rect; it is now an inset axes in
    the 0.87 in of gutter to the right, so all 1.58 in of the rect is field. Its pad and width are
    given in INCHES and re-converted on EVERY DRAW by _cb_locator, so the bar is the same physical
    width in this figure, in Extended Data Fig. 6 and in the standalone preview. Converting them
    once, when the panel is drawn, was not enough: see the note on _cb_locator.
  * the bar's furniture (bar, tick labels, rotated label) now ends 0.475 in right of the axes,
    rightmost ink at page x = 2.655 in. That is 55 per cent of the 0.87 in gutter, which the harness
    hands to g and h jointly. Panel h's leftmost furniture, its "best decision regret" y label,
    starts at 2.691 in, so the two clear each other by 0.036 in. Measured in the composite, not
    budgeted: it is the tightest gap in this panel's layout, and it is the number to re-measure if
    either panel's furniture grows.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FuncFormatter
from matplotlib.transforms import Bbox

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(_HERE, "..")))
sys.path.insert(0, os.path.abspath(os.path.join(_HERE, "..", "fig4")))
# Colour and type come from the figure's frozen vocabulary; do NOT re-declare a hex value or type a
# point size here. One edit in fig4_style has to recolour and re-size the whole figure. The
# divergent map is imported for the same reason: two local copies of it once existed, and a
# recolour moved the figures that imported it while leaving those two behind.
from figstyle import DIVMAP_SOFT  # noqa: E402
from fig4_style import LW_HAIR, PT_SMALL, PT_TICK, TEXT  # noqa: E402

REPO = os.path.abspath(os.path.join(_HERE, "..", ".."))
S = os.path.join(REPO, "results", "exp11_synthetic_phase_diagram")

# The metric is a difference of two Hit@1 rates, so it is bounded on [-VLIM, VLIM] by construction.
# The colour scale is that bound, not the observed range, so the reader sees the whole space the
# statistic could have occupied. N_CB_TICKS is odd so the neutral centre is always labelled.
VLIM = 1.0
N_CB_TICKS = 5

# The colour bar lives in the gutter to the RIGHT of the axes, not in the axes' own width. Given in
# inches and re-converted against the parent's box on every draw by _cb_locator, so it is the same
# physical bar whatever box the parent hands this panel and wherever the parent later moves.
CB_PAD_IN = 0.055    # axes right edge -> bar
CB_W_IN = 0.075      # bar width
CB_TICK_PAD = 1.6    # bar -> its tick labels, in points
CB_LABEL_PAD = 2.0   # tick labels -> the rotated label, in points


def _cb_locator(parent):
    """Return a draw-time locator: the bar CB_PAD_IN right of ``parent``, CB_W_IN wide, full height.

    A locator rather than a fixed rect because inset_axes' own locator is parent-RELATIVE.
    Converting the pad and the width against the parent ONCE, when the panel is drawn, makes them
    the intended inches only until the parent next moves, and ed6.py moves it: it calls
    subplots_adjust() after the four panels are drawn, which narrows this parent from 2.431 to
    2.210 in and takes the bar down with it, to 0.068 in wide with a 0.050 in pad. This closes over
    the parent axes rather than over its width, and matplotlib calls it on every draw, so the bar is
    CB_W_IN wide on the page in the Figure 4 composite, in Extended Data Fig. 6 and in the
    standalone preview alike.
    """
    def locate(_cax, _renderer):
        p = parent.get_position()
        fig_w_in = float(parent.figure.get_size_inches()[0])
        return Bbox.from_bounds(p.x1 + CB_PAD_IN / fig_w_in, p.y0, CB_W_IN / fig_w_in, p.height)
    return locate


def draw_ed6b(ax):
    """Energy-minus-mean Hit@1 over the (conflict lambda, minority fraction alpha) grid."""
    dag = pd.read_csv(f"{S}/dart_advantage_grid.csv")
    grid = dag.pivot_table(index="lambda", columns="alpha", values="adv_energy_vs_mean")
    # one cell per (lambda, alpha) pair, or the field has a hole the colour map would render as
    # white, i.e. as a neutral advantage, which is a different claim from "not measured"
    assert not grid.isna().values.any(), "the (lambda, alpha) grid has missing cells"
    # and exactly one ROW per cell. pivot_table's default aggfunc is the mean, so a second row for
    # any (lambda, alpha) pair, a second cell line for instance, would be averaged in silently and
    # every cell of the field would change without the panel or this module saying anything. The
    # file carries 36 rows for 36 cells, all K562; if that ever stops being true it has to fail here
    # rather than redraw.
    assert len(dag) == grid.size, (
        f"{len(dag)} rows for {grid.size} (lambda, alpha) cells: pivot_table would average the "
        f"duplicates into the field silently")
    im = ax.imshow(grid.values, cmap=DIVMAP_SOFT, vmin=-VLIM, vmax=VLIM,
                   aspect="auto", origin="lower")

    ax.set_xticks(range(len(grid.columns)))
    ax.set_yticks(range(len(grid.index)))
    # sizes come from the house ladder (PT_TICK), never from a local fontsize
    ax.set_xticklabels([f"{a:g}" for a in grid.columns])
    ax.set_yticklabels([f"{l:g}" for l in grid.index])
    ax.set_xlabel(r"minority fraction $\alpha$")
    ax.set_ylabel(r"conflict $\lambda$")

    # the bounds here are a placeholder: _cb_locator recomputes them, in inches, on every draw
    cax = ax.inset_axes([1.0, 0.0, 1.0, 1.0])
    cax.set_axes_locator(_cb_locator(ax))
    cb = ax.figure.colorbar(im, cax=cax)
    cb.outline.set_linewidth(LW_HAIR)
    cb.outline.set_edgecolor(TEXT)
    # ticks derived from the colour limit, not typed, and a real U+2212 for the minus
    cb.locator = FixedLocator(np.linspace(-VLIM, VLIM, N_CB_TICKS))
    cb.formatter = FuncFormatter(lambda v, _pos: f"{v:g}".replace("-", "−"))
    cb.update_ticks()
    cb.ax.tick_params(labelsize=PT_TICK, length=1.8, width=0.5, pad=CB_TICK_PAD, color=TEXT)
    cb.set_label("Hit@1: energy − mean", fontsize=PT_SMALL, labelpad=CB_LABEL_PAD)


if __name__ == "__main__":
    from figstyle import apply_style, soften_axes  # noqa: E402
    from fig4_style import PT_ANNOT, PT_TITLE  # noqa: E402

    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    fig = plt.figure(figsize=(3.2, 2.6))
    ax = fig.add_axes([0.20, 0.16, 1.58 / 3.2, 1.75 / 2.6])
    draw_ed6b(ax)
    soften_axes(fig)
    fig.savefig(os.path.join(_HERE, "ed6b.png"), dpi=300)
    print("wrote ed6b.png")
