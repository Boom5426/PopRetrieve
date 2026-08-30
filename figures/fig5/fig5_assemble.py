"""PopRetrieve Figure 5: Structure preservation and identifiability constrain distribution-aware retrieval.
14-panel two-gate mechanism figure. Assembles a-n into fig5_two_gate.{pdf,svg,png}.

WHAT PANELS h-n ARE AND WHY THEY ARE HERE, 2026-08-30
----------------------------------------------------
The Extended Data deck is retired and its panels move into the main figures. Seven of them land
here because Figure 5 is the figure that states the three requirements (differential response,
recoverability, decision relevance), and these seven measure those same three requirements on
material the figure did not previously cover.

  h  ed_panels.draw_ed3a   median ARI against the true two-source labels for nine unsupervised
                           clustering configurations, best 0.106 against the 0.5 reliability line.
  i  ed_panels.draw_ed3b   per-population silhouette under a raw k=2 partition, SciPlex3 (n=529)
                           and Frangieh (n=231).
  j  ed_panels.draw_ed3d   the seed-averaged ARI heatmap over separation scale by cells per source.

Panels e and f already measure recoverability on the constructed mixture, e as a supervised
ceiling and f as the positive control that licenses reading e. h, i and j measure the same thing
three further ways: across clusterers rather than one (h), in the raw geometry the clusterers see
rather than through an accuracy score (i), and across the whole separation-by-budget grid rather
than along f's single separation ladder (j). A reader who doubts e is answered by the row below
it, not by a different document.

  k  ed7_tahoe.draw_a      histogram of the induced response cosine between subpopulations over
                           3,630 Tahoe-100M conditions, median 0.739.
  l  ed7_tahoe.draw_b      Tahoe supervised ceiling against best unsupervised over 960 drug pairs
                           and 48 cell lines, median gap 0.157.
  m  ed7_tahoe.draw_c      disjoint state-ordering Spearman under two partitions, medians 0.841
                           and 0.778.
  n  ed7_tahoe.draw_d      per-cell-line differential response against state-ordering agreement.

k, l, m and n are the three requirements measured again on Tahoe-100M, 4,158,278 cells of
heterogeneity nobody constructed: k is requirement one, l is requirement two, m is requirement
three, and n checks that m is not requirement one restated. That is the paper's answer to the
obvious objection, namely that a negative result on mixtures the authors built is a fact about the
authors' mixtures. The answer has to sit in the same figure as the claim it defends, because a
reader who accepts the objection stops reading before the Extended Data. Panel m carries a second
job: panel a marks decision relevance as proposed rather than measured, and m at n=44 and n=45
contexts is the closest the paper comes to measuring it, so the qualifier in a and the measurement
in m are now on one page where a reader can hold them against each other.

GEOMETRY, 2026-07-26, RE-CUT 2026-08-30 WHEN THE CAPTION MOVED OFF THE PAGE
---------------------------------------------------------------------------
The manuscript text block is 6.95 in (500.5 pt, letterpaper with 2 cm margins) and every figure
enters with ``\\includegraphics[width=\\textwidth]``. This figure used to be authored 11.4 in wide,
so LaTeX shrank it by 0.61x and its 5.4-6 pt source type printed at 3.3-3.7 pt. Nature Portfolio
rejects text below 5 pt AT FINAL PRINTED SIZE, so the deck's build-time floor (which measures the
NOMINAL size only) reported CLEAN while the printed page failed.

The canvas is now 6.90 in wide, i.e. nominal size == printed size and the scale factor is 1.00.
Two consequences drove every other change here:

  1. Seven panels no longer fit in two rows. Four panels across 6.9 in leaves each about 1.2 in of
     data area, which is narrower than panel c's four x-tick labels and panel e's seven. The grid
     was three rows, 3 + 2 + 2, with the two width-hungry panels (e, seven methods; f and g) given
     the wide slots and the schematic given the narrow one. It is now five rows, 3 + 2 + 2 + 3 + 4;
     the four-across row is the one row whose panels were AUTHORED four-across, in ed7_tahoe.py at
     this same 6.90 in width, so their labels are known to fit that slot.
  2. Panel geometry is specified in INCHES via ``add_axes`` rather than as gridspec ratios. At this
     size the binding constraints are absolute (a tick label is 0.5 in wide whatever the canvas is),
     so the gutters are sized to the label that has to fit in them: 0.62 in between a and b for
     panel b's wrapped predictor names, 0.50 in for a rotated y label plus its ticks, and a 0.52 in
     right margin in row 0 alone for panel c's second y axis.

``figstyle.save`` writes with ``bbox_inches="tight"``, which would crop the canvas back to the ink
and hand LaTeX a figure narrower than 6.9 in to scale UP again. A transparent full-canvas anchor
patch pins the tight bbox to the authored width, so the exported media box is 6.92 x 9.22 in
(6.90 x 9.20 plus the 0.01 in savefig pad) and the printed scale factor is 1.00 by construction.
The patch is a floor, not a ceiling: it cannot pull ink back inside, so anything that hangs over
an edge still widens the page. That is what sizes the right margins in rows 3 and 4 below.
"""
import os, re, sys, matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# The panel modules for h-n live in two sibling figure directories, so the search path is
# extended the same way the two local imports below always extended it, just over a list.
_HERE = os.path.dirname(os.path.abspath(__file__))
_FIGROOT = os.path.abspath(os.path.join(_HERE, ".."))
for _p in (_HERE, _FIGROOT, os.path.join(_FIGROOT, "edfigs"), os.path.join(_FIGROOT, "ed7")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# The one canonical output stem for this figure; must equal build_all.STEMS[6], which build_all
# asserts, because that is the name copied to manuscript/latex/figures/fig5.pdf.
STEM = "fig5_two_gate"

from fig5a import draw_5a
from fig5b import draw_5b
from fig5c import draw_5c
from fig5d import draw_5d
from fig5e import draw_5e
from fig5f import draw_5f
from fig5g import draw_5g

import ed_panels                    # noqa: E402  draw_ed3a/b/d(ax, D), D from ed_panels.load()
import ed7_tahoe as _ed7            # noqa: E402  draw_a..draw_d(ax)

# Panel b's title used to read "No predictor gives a positive gain". The deck's own source
# data (source_data/fig5b_predictor_gaps.csv) falsifies it: the latent-linear predictor's
# nDCG@10 gain is +0.027. The panel only looked consistent because a reindex key typo
# dropped that predictor. The honest summary is that the gain is small and its SIGN is not
# consistent across predictors, which is a weaker claim than the old title and a true one.
# Panel titles are claims, and each must be true of the CURRENT manuscript.
#   a  was "Retrieval limited by the predictor": panel a is the design schematic and shows no
#      such result. It now states what the caption says it is.
#   f  was "More cells cannot fix low separability": FALSE OF THE PANEL. The cell-budget axis
#      was removed when the ARI phase diagram was replaced by the separation ladder, so the panel
#      has no cell axis at all. Its x-axis is source separation and its job, per the caption, is
#      the positive control that licenses reading panel e. The cell-budget axis is back in the
#      figure as panel j, which is where that claim may now be read.
#   e  was "No method recovers subpopulations". The manuscript now states that the low-ceiling
#      reading is superseded (in patient tumour the same protocol gives ceiling 0.923 against
#      0.777 unsupervised, so the limit there is algorithmic). The title is therefore scoped to
#      the constructed mixture this panel actually measures.
# The line breaks are geometry, not wording: at 6.9 in the narrow row-0 panels are 1.4-1.9 in
# wide and an 8 pt single-line title of 36-39 characters runs 2.0-2.2 in, i.e. straight off the
# panel and into its neighbour. Every title below is the same claim it was, wrapped.
#   h-n keep the claims their source figures declared, with one scope repair: k's old title,
#      "the mixtures are the outlier", named the constructed mixtures without saying against what,
#      which reads as a claim about mixtures in general rather than about this distribution.
TITLES={"a":"Predict-then-rank,\nand three conditions",
        "b":"Gain is small and\nsign-inconsistent",
        "c":"Structure survives;\ndivergence does not",
        "d":"No predictor collapses structure",
        "e":"In this mixture, even the ceiling is only 0.692",
        "f":"The probe pulls away when structure is there",
        "g":"Where theory predicts gain, there is none",
        "h":"No clustering configuration\nreaches reliable ARI",
        "i":"Raw k=2 barely separates\nthe two sources",
        "j":"More cells do not rescue\nlow separation",
        "k":"Against 3,630 Tahoe conditions,\nthe mixtures are the outlier",
        "l":"Recoverable in principle,\nout of reach in practice",
        "m":"State ordering mostly agrees,\nnot always",
        "n":"Ordering agreement is not\ndifferential response restated"}
#   g  was "No positive effect at any divergence". The highest-divergence quartile's mean is
#      +0.003 (not significant, median exactly 0), so a reader can point at a positive bar and
#      call the title false. The replacement is the caption's own sentence, "Where the theory
#      predicts the largest gain there is none", which is exactly what the panel shows.

from figstyle import soften_axes, strip_titles  # noqa: E402

FIG_W, FIG_H = 6.90, 9.20          # inches; the manuscript text block is 6.93 x 9.43 in
# 9.20 in, not 5.14. Height was capped near 5 in only because the caption shared the page with the
# graphic; captions now set on the following page, so the graphic's budget is the text block less
# the float separation, which is 9.30 in. The seven new panels need two more rows, and two rows at
# the heights below cost 4.06 in, so the canvas grows by exactly that and every pre-existing y0
# moves up by 4.06 in unchanged. Nothing in rows 0-2 was re-plotted or re-proportioned.
# 9.20 rather than the full 9.30: the 0.10 in that is left is the margin the anchor patch cannot
# provide, since a panel letter sits 0.06 of an axes height ABOVE its axes and row 0's letters
# already reach 9.125 in.
# History of the number, kept because it explains the row heights that were NOT changed: at 6.85 in
# LaTeX reported "Float too large for page by 83.7pt" when the caption still shared the page, and
# rows and panels were tightened by ~15% rather than moving a panel out, since every panel letter
# is cited in the caption. Those tightened heights are the ones rows 0-2 still carry.

# Panel rectangles in INCHES, (x0, y0, width, height), origin bottom-left of the canvas.
# Rows are stacked bottom-up with 0.36-0.48 in reserved under each row for two-line x tick labels
# plus an x axis label, and 0.22-0.32 in above each row for its title and panel letter.
#   row 0 (top)    y0 7.62  h 1.42   a | b | c      c's second y axis owns the 0.52 in right margin
#   row 1          y0 6.00  h 1.32   d | e          e needs 7 tick label slots, so it takes 3.63 in
#   row 2          y0 4.44  h 1.26   f | g
#   row 3          y0 2.37  h 1.55   h | i | j      the constructed mixture, three more ways
#   row 4 (bottom) y0 0.52  h 1.30   k | l | m | n  Tahoe-100M, all three requirements
# Row 4 ends at 6.78 in, a 0.12 in right margin rather than rows 0-2's 0.52 in. That is not
# carelessness: panel n has nothing in its right gutter (its y label and its rho/R2 block are both
# on the left) and its rightmost x tick label is a three-character number, so 0.12 in is more than
# the half-label that can overhang. The exported media box is the check, and it reads 6.92 in.
# The two new rows are taller than rows 0-2 (1.55 and 1.30 against 1.26-1.42) for opposite
# reasons. Row 3 is set by panel h, which stacks NINE categorical rows: at row 2's 1.26 in the
# bars are 0.10 in apart and the 5 pt labels between them touch. Row 4 is set by nothing on the
# canvas; 1.30 in is 0.10 in more than ed7_tahoe.py gave the same four panels, spent because the
# row was going to be the bottom one and a squat bottom row reads as an afterthought.
BOXES = {
    # a is 0.07 in narrower than b so the a|b gutter is 0.62 in rather than 0.55: panel b's
    # widest y tick label, "(scGen-fam.)", measures 0.56 in at 6 pt and at 0.55 in of gutter it
    # came within 0.02 in of panel a's gate boxes.
    "a": (0.62, 7.62, 1.33, 1.42),
    "b": (2.57, 7.62, 1.43, 1.42),
    "c": (4.50, 7.62, 1.88, 1.42),
    "d": (0.62, 6.00, 1.85, 1.32),
    "e": (2.99, 6.00, 3.63, 1.32),
    "f": (0.62, 4.44, 2.74, 1.26),
    "g": (3.89, 4.44, 2.73, 1.26),
    # h takes a 1.25 in left pad, five times the deck's usual one, because its nine y tick labels
    # are method names rather than numbers: the longest, "k-means k=2 (response)", is 22 characters
    # at 5 pt and measures 0.76 in, and the panel letter still has to sit outside that.
    "h": (1.25, 2.37, 1.50, 1.55),
    "i": (3.28, 2.37, 1.22, 1.55),
    # j stops at 6.26 in and leaves 0.64 in of canvas unclaimed. Its colorbar is drawn with
    # fig.colorbar(..., ax=ax), which splits the colorbar out of the axes rectangle but puts the
    # "ARI" label and the tick labels OUTSIDE it; measured on the Extended Data build, that
    # overhang is 0.32 in. Anything less than that here and the overhang, not the anchor patch,
    # would set the exported page width.
    "j": (5.02, 2.37, 1.24, 1.55),
    # Row 4 carries ed7_tahoe.py's own x0 and widths across UNCHANGED. They are not arbitrary:
    # every one of these four panels hand-places annotations in data coordinates (l's three
    # reference diamonds and its median label, m's two left-margin notes, k's four rotated
    # anchors), and text is absolute while data coordinates are not, so narrowing a panel by
    # 0.10 in drags those labels together. A first cut here took 0.06-0.10 in off each to buy a
    # wider right margin and l's "Tahoe median gap 0.157" closed on "constructed, drug vs drug"
    # until they read as one line. The margin was bought back from the row above instead.
    "k": (0.52, 0.52, 1.30, 1.30),
    "l": (2.28, 0.52, 1.24, 1.30),
    "m": (4.02, 0.52, 1.18, 1.30),
    "n": (5.72, 0.52, 1.06, 1.30),
}
# How far LEFT of its own axes each panel letter sits, in inches: far enough to clear whatever
# that panel puts in its left gutter (nothing for the schematic, a rotated y label plus ticks
# elsewhere), and never so far that the letter leaves the canvas. h and k are large because they
# open their rows on the same 0.16 in left column as d, f and the rest, while their axes start
# 1.25 in and 0.55 in in.
LETTER_DX_IN = {"a": 0.16, "b": 0.52, "c": 0.46, "d": 0.44, "e": 0.46, "f": 0.46, "g": 0.46,
                "h": 1.09, "i": 0.50, "j": 0.48,
                "k": 0.36, "l": 0.42, "m": 0.46, "n": 0.48}
# One baseline for every letter now that no panel carries a title to align with.
LETTER_DY = {}




def _adapt(fn, arg):
    """Wrap a two-argument draw function so every panel is callable as fn(ax).

    ed_panels' draw functions take (ax, D) because D is the whole Extended Data table set and
    reading it per panel would read the same nine CSVs three times. ed_consolidated.py binds them
    the same way.
    """
    return lambda ax: fn(ax, arg)


def build(apply_style, panel_letter):
    apply_style(sizes=(8,7,6))
    fig=plt.figure(figsize=(FIG_W,FIG_H))
    # Pin the tight bbox to the authored canvas (see module docstring). Transparent, zero-width,
    # behind everything: it contributes extent and no ink.
    fig.patches.append(mpatches.Rectangle((0,0),1,1,transform=fig.transFigure,
                                          fill=False,ec="none",lw=0,zorder=-10))
    # ONE read of the Extended Data tables, here, for h, i and j together.
    D = ed_panels.load()
    fns={"a":draw_5a,"b":draw_5b,"c":draw_5c,"d":draw_5d,"e":draw_5e,"f":draw_5f,"g":draw_5g,
         "h":_adapt(ed_panels.draw_ed3a,D),
         "i":_adapt(ed_panels.draw_ed3b,D),
         "j":_adapt(ed_panels.draw_ed3d,D),
         "k":_ed7.draw_a,"l":_ed7.draw_b,"m":_ed7.draw_c,"n":_ed7.draw_d}
    for k,(x0,y0,w,h) in BOXES.items():
        ax=fig.add_axes([x0/FIG_W, y0/FIG_H, w/FIG_W, h/FIG_H])
        fns[k](ax)
        panel_letter(ax,k,case="lower",dx=-LETTER_DX_IN[k]/w,dy=LETTER_DY.get(k,1.06))
    # Nature panels carry no titles; the fourteen claims in TITLES are the caption's fourteen
    # entries.
    return strip_titles(soften_axes(fig))


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
    print("wrote fig5_two_gate.{png,pdf}")
