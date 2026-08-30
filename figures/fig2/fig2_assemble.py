"""PopRetrieve Figure 2: under objective-aligned metrics, distributional retrieval looks decisively stronger.

Seven panels in three rows. The top row carries the claim (a, the Hit@1 ladder), its counterexample
(b, Frangieh) and its per-query distribution (c); the middle row holds the three supporting controls
(d gate, e alpha sweep, f metric robustness); the bottom row carries the score-to-score correlation
matrix (g) that the first two rows argue from without ever showing.

Panel g, moved here when the Extended Data deck was retired
-----------------------------------------------------------
g was ED1a of edfigs/ed_consolidated.py and is still drawn by edfigs/ed_panels.draw_ed1c: it is
IMPORTED, not re-plotted, so the matrix printed here is the one the Extended Data deck printed,
over the same 54,180 query-candidate scores (1,260 queries against 43 candidates each). It covers
six of the eight scorers on a's ladder; the two PCA baselines are absent from the correlation
export and the panel does not invent them.

It earns main-deck space for two reasons, and both are about a and b rather than about g itself.

First, a's headline is that energy reaches Hit@1 0.837 against 0.388 for mean cosine and for the
numerically identical CMap-style cosine baseline, and b spends that identity again when it draws
the pair as one marker. g is where the word "identical" is measured: Spearman rho = 1.000 at every
one of the 54,180 pairs, not an agreement between the two macro-means a happens to plot. Until this
row existed, the evidence for a load-bearing word in this figure's caption lived in another float.

Second, g shows energy and the two coverage scores agreeing with each other (rho 0.72 to 0.97) and
not with mean cosine (|rho| <= 0.08), so the population-sensitive scores form a block that the
mean-shaped ones are close to orthogonal to. That is what makes a-f a comparison between two
FAMILIES of score rather than a ranking of eight scorers that happen to have been run: the family
colouring in a is a claim about score algebra, and this is the panel that measures it.

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
without starving the other four panels. Rows 1 and 2 are each a 5-cell gridspec of
``[panel, gutter, panel, gutter, panel]`` with ``wspace=0``, so every width below is literally
inches on the printed page.

Row 3 is the same ledger with three cells, ``[margin, panel, margin]``, because it carries one
panel. g is a 6x6 matrix drawn with ``aspect="equal"``, so matplotlib re-fits its axes box to a
square at draw time whatever cell it is handed. Run to the full 6.14 in row the matrix is still
1.905 in, the row height being what limits it there, and ``colorbar(ax=ax)`` then anchors the
matrix EAST inside its own cell and parks the pair at x 4.41 to 6.65 with 3.7 in of blank to their
left. A full-width cell therefore buys no ink at all and hands the placement to ``make_axes``; a
2.080 in cell keeps it in the ledger, where this file keeps every other placement. The two margins
are unequal because what is centred on the page is the ink and not the cell: g hangs 0.50 in of y
tick labels past the left edge of its cell and 0.39 in of colorbar tick labels and "Spearman rho"
past the right. Centring the cell instead would print the panel visibly off-centre; as written the
blank canvas measures 1.963 in on the left and 1.964 in on the right.

This file also pins the canvas now, which it did not before, for one old reason and one that
arrives with row 3. Unpinned, ``bbox_inches="tight"`` cropped to the ink and exported 6.85 in
rather than 6.90, so ``width=\\textwidth`` magnified the composite by 1.2 per cent and printed
point size stopped being nominal point size, which is the drift the 1:1 authoring above exists to
remove; worse, that width was an emergent property of whichever annotation sat furthest out, so any
later edit could move it. And g is centred on the 6.9 in CANVAS, which is only centred on the
printed page if the canvas IS the page: a tight crop keeps 1.952 in of blank left of g and 1.904 in
right of it, two margins that differ by 0.05 in, and centring is the one thing this row's ledger
was written to buy.

This gain is objective-aligned (Class A); it is NOT independent validation, which is Figure 3.
"""
import os, sys, matplotlib.pyplot as plt

# ONE canonical output stem per figure. This file used to write fig2_apparent_gains.* while
# build_all.py wrote the same figure as fig2_temptation.*, so the composite existed on disk twice
# under two names and nothing said which was current. build_all's STEMS entry is the one that is
# copied to manuscript/latex/figures/fig2.pdf, so that is the name kept here; build_all checks
# this constant against its own STEMS dict and fails the build if the two ever drift apart again.
STEM = "fig2_temptation"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# The Extended Data panel library, for g. Same path idiom as the two lines above; edfigs is not a
# package, and ed_consolidated.py reaches its own imports the same way.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "edfigs")))
from fig2a import draw_2a
from fig2b import draw_2b
from fig2c import draw_2c
from fig2d import draw_2d
from fig2e import draw_2e
from fig2f import draw_2f

import ed_panels                                    # noqa: E402  draw_edNx(ax, D)
from figstyle import pin_canvas, strip_titles       # noqa: E402

DRAW = {"a": draw_2a, "b": draw_2b, "c": draw_2c,
        "d": draw_2d, "e": draw_2e, "f": draw_2f}

# ---- the inch ledger -----------------------------------------------------------------------
FIG_W, FIG_H = 6.9, 8.055          # 6.9 in <= 6.93 in text block: printed 1:1
M_LEFT = 0.70                      # holds panel a "coverage-worst" y tick labels
M_RIGHT = 0.06
M_TOP = 0.38                       # panel letters only; the titles are in the caption
M_BOT = 0.52                       # g's x tick labels: its y labels stood upright cost 0.50 in
                                   # (was 0.44, for row 2, which now hangs into ROW_GAP instead)
ROW_GAP = 0.72                     # row-N x labels + row-(N+1) letters (was 0.95, with titles)
N_ROWS = 3                         # a b c | d e f | g
USABLE = FIG_W - M_LEFT - M_RIGHT  # 6.14 in of drawable width per row

# [panel, gutter, panel, gutter, panel]; gutters sized by what the RIGHT neighbour needs
ROW1 = [1.757, 0.42, 1.757, 0.45, 1.756]      # a | b | c
ROW2 = [1.450, 0.50, 1.830, 0.74, 1.620]      # d | e | f   (0.74 = f's long category labels)
# [margin, panel, margin]. 2.080 is the widest cell that still leaves g square inside ROW_H, and
# the two margins are what centres g's INK, not its cell, on the 6.9 in page (see above).
ROW3 = [1.762, 2.080, 2.298]                  # (empty) | g | (empty; g's colorbar lands here)
assert abs(sum(ROW1) - USABLE) < 1e-6, sum(ROW1)
assert abs(sum(ROW2) - USABLE) < 1e-6, sum(ROW2)
assert abs(sum(ROW3) - USABLE) < 1e-6, sum(ROW3)

ROW_H = (FIG_H - M_TOP - M_BOT - ROW_GAP * (N_ROWS - 1)) / N_ROWS
LETTER_OFFSET_IN = 0.22            # panel letters sit a constant 0.22 in left of their axes
# g's letter is measured against the PRINTED square, not against its 2.080 in cell. Because
# ``transAxes`` resolves to the box ``aspect="equal"`` leaves behind, dividing 0.22 in by the cell
# would print the letter 0.20 in out and break the letter column. Derived rather than typed as
# 1.901 so that re-tuning ROW3 cannot silently desynchronise the two.
CBAR_TAKE = 0.046 + 0.04           # fraction + pad, exactly as ed_panels.draw_ed1c passes them
G_AXES_W = ROW3[1] * (1.0 - CBAR_TAKE)        # 1.901 in against a 1.905 in row: width-limited
assert G_AXES_W <= ROW_H + 1e-9, f"g would be height-limited: {G_AXES_W:.3f} > {ROW_H:.3f}"


def _adapt(fn, arg):
    """Wrap a draw function that wants a second argument so every panel is callable as fn(ax)."""
    return lambda ax: fn(ax, arg)


def build(apply_style, panel_letter):
    apply_style(sizes=(8, 7, 6))   # deck-wide type ladder; no titles are drawn
    fig = plt.figure(figsize=(FIG_W, FIG_H))

    # ed_panels.load() opens every table the Extended Data library needs, so it is called ONCE
    # here and bound to the one panel that uses it, the way ed_consolidated._build_specs does.
    draw = dict(DRAW, g=_adapt(ed_panels.draw_ed1c, ed_panels.load()))

    left, right = M_LEFT / FIG_W, 1.0 - M_RIGHT / FIG_W
    r1_top = 1.0 - M_TOP / FIG_H
    r1_bot = r1_top - ROW_H / FIG_H
    r2_top = r1_bot - ROW_GAP / FIG_H
    r2_bot = r2_top - ROW_H / FIG_H
    r3_top = r2_bot - ROW_GAP / FIG_H
    r3_bot = r3_top - ROW_H / FIG_H

    gs1 = fig.add_gridspec(1, 5, width_ratios=ROW1, wspace=0,
                           left=left, right=right, top=r1_top, bottom=r1_bot)
    gs2 = fig.add_gridspec(1, 5, width_ratios=ROW2, wspace=0,
                           left=left, right=right, top=r2_top, bottom=r2_bot)
    gs3 = fig.add_gridspec(1, 3, width_ratios=ROW3, wspace=0,
                           left=left, right=right, top=r3_top, bottom=r3_bot)

    # panel -> (gridspec, cell index, axes width in inches)
    PLACE = {"a": (gs1, 0, ROW1[0]), "b": (gs1, 2, ROW1[2]), "c": (gs1, 4, ROW1[4]),
             "d": (gs2, 0, ROW2[0]), "e": (gs2, 2, ROW2[2]), "f": (gs2, 4, ROW2[4]),
             "g": (gs3, 1, G_AXES_W)}

    for k, (gs, col, w_in) in PLACE.items():
        ax = fig.add_subplot(gs[0, col])
        draw[k](ax)
        panel_letter(ax, k, dx=-LETTER_OFFSET_IN / w_in, dy=1.19, case="lower")

    # Nature panels carry no titles: the seven claims each panel used to state over itself are
    # now the seven entries of this figure's caption. Panel scripts keep their set_title calls
    # so a standalone preview still labels itself; the composite strips them.
    return pin_canvas(strip_titles(fig))


if __name__ == "__main__":
    # build() must NOT export. It used to call fig.savefig() here, which meant two things:
    # `python figures/build_all.py` without --write, documented as a report-only dry run,
    # silently overwrote four tracked composites; and it wrote them BEFORE
    # assert_min_fontsize ran, so a figure that then FAILED the gate had already been
    # deployed to disk. Every export now goes through figstyle.save(), which applies the
    # 5 pt floor first. (Audited 2026-07-27; fig1 and fig4 already worked this way.)
    from figstyle import apply_style, panel_letter, save
    save(build(apply_style, panel_letter),
         os.path.join(os.path.dirname(os.path.abspath(__file__)), STEM))
    print("wrote fig2 composite")
