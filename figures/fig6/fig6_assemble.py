"""PopRetrieve Figure 6: Structure preservation and identifiability constrain distribution-aware retrieval.
7-panel two-gate mechanism figure. Assembles a-g into fig6_two_gate.{png,pdf}.

GEOMETRY, 2026-07-26: authored at the FINAL PRINTED WIDTH.
------------------------------------------------------------
The manuscript text block is 6.95 in (500.5 pt, letterpaper with 2 cm margins) and every figure
enters with ``\\includegraphics[width=\\textwidth]``. This figure used to be authored 11.4 in wide,
so LaTeX shrank it by 0.61x and its 5.4-6 pt source type printed at 3.3-3.7 pt. Nature Portfolio
rejects text below 5 pt AT FINAL PRINTED SIZE, so the deck's build-time floor (which measures the
NOMINAL size only) reported CLEAN while the printed page failed.

The canvas is now 6.90 in wide, i.e. nominal size == printed size and the scale factor is 1.00.
Two consequences drove every other change here:

  1. Seven panels no longer fit in two rows. Four panels across 6.9 in leaves each about 1.2 in of
     data area, which is narrower than panel c's four x-tick labels and panel e's seven. The grid
     is now three rows, 3 + 2 + 2, with the two width-hungry panels (e, seven methods; f and g) given
     the wide slots and the schematic given the narrow one.
  2. Panel geometry is specified in INCHES via ``add_axes`` rather than as gridspec ratios. At this
     size the binding constraints are absolute (a tick label is 0.5 in wide whatever the canvas is),
     so the gutters are sized to the label that has to fit in them: 0.62 in between a and b for
     panel b's wrapped predictor names, 0.50 in for a rotated y label plus its ticks, and a 0.52 in
     right margin in row 0 alone for panel c's second y axis.

``figstyle.save`` writes with ``bbox_inches="tight"``, which would crop the canvas back to the ink
and hand LaTeX a figure narrower than 6.9 in to scale UP again. A transparent full-canvas anchor
patch pins the tight bbox to the authored width, so the exported media box is 6.92 x 6.87 in
(6.90 x 6.85 plus the 0.01 in savefig pad) and the printed scale factor is 1.00 by construction.
"""
import os, sys, matplotlib.pyplot as plt
import matplotlib.patches as mpatches

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# The one canonical output stem for this figure; must equal build_all.STEMS[6], which build_all
# asserts, because that is the name copied to manuscript/latex/figures/fig6.pdf.
STEM = "fig6_two_gate"

from fig6a import draw_6a
from fig6b import draw_6b
from fig6c import draw_6c
from fig6d import draw_6d
from fig6e import draw_6e
from fig6f import draw_6f
from fig6g import draw_6g

# Panel b's title used to read "No predictor gives a positive gain". The deck's own source
# data (source_data/fig6b_predictor_gaps.csv) falsifies it: the latent-linear predictor's
# nDCG@10 gain is +0.027. The panel only looked consistent because a reindex key typo
# dropped that predictor. The honest summary is that the gain is small and its SIGN is not
# consistent across predictors, which is a weaker claim than the old title and a true one.
# Panel titles are claims, and each must be true of the CURRENT manuscript.
#   a  was "Retrieval limited by the predictor": panel a is the design schematic and shows no
#      such result. It now states what the caption says it is.
#   f  was "More cells cannot fix low separability": FALSE OF THE PANEL. The cell-budget axis
#      was removed when the ARI phase diagram was replaced by the separation ladder (it is in
#      Extended Data), so the panel has no cell axis at all. Its x-axis is source separation
#      and its job, per the caption, is the positive control that licenses reading panel e.
#   e  was "No method recovers subpopulations". The manuscript now states that the low-ceiling
#      reading is superseded (in patient tumour the same protocol gives ceiling 0.923 against
#      0.777 unsupervised, so the limit there is algorithmic). The title is therefore scoped to
#      the constructed mixture this panel actually measures.
# The line breaks are geometry, not wording: at 6.9 in the narrow row-0 panels are 1.4-1.9 in
# wide and an 8 pt single-line title of 36-39 characters runs 2.0-2.2 in, i.e. straight off the
# panel and into its neighbour. Every title below is the same claim it was, wrapped.
TITLES={"a":"Predict-then-rank,\nand three conditions",
        "b":"Gain is small and\nsign-inconsistent",
        "c":"Structure survives;\ndivergence does not",
        "d":"No predictor collapses structure",
        "e":"In this mixture, even the ceiling is only 0.692",
        "f":"The probe pulls away when structure is there",
        "g":"Where theory predicts gain, there is none"}
#   g  was "No positive effect at any divergence". The highest-divergence quartile's mean is
#      +0.003 (not significant, median exactly 0), so a reader can point at a positive bar and
#      call the title false. The replacement is the caption's own sentence, "Where the theory
#      predicts the largest gain there is none", which is exactly what the panel shows.

FIG_W, FIG_H = 6.90, 5.60          # inches; the manuscript text block is 6.93 x 9.43 in
# Height was 6.85 in, which placed the figure at 73% of the text block and made LaTeX report
# "Float too large for page by 83.7pt": the legend no longer fitted under it. Rows and panels
# were tightened by ~15% rather than moving a panel out, since every panel letter is cited in
# the caption.

# Panel rectangles in INCHES, (x0, y0, width, height), origin bottom-left of the canvas.
# Rows are stacked bottom-up with 0.36 in reserved under each row for two-line x tick labels
# plus an x axis label, and 0.22-0.32 in above each row for its title and panel letter.
#   row 0 (top)    y0 4.70  h 1.80   a | b | c      c's second y axis owns the 0.52 in right margin
#   row 1          y0 2.50  h 1.62   d | e          e needs 7 tick label slots, so it takes 3.63 in
#   row 2 (bottom) y0 0.44  h 1.48   f | g
BOXES = {
    # a is 0.07 in narrower than b so the a|b gutter is 0.62 in rather than 0.55: panel b's
    # widest y tick label, "(scGen-fam.)", measures 0.56 in at 6 pt and at 0.55 in of gutter it
    # came within 0.02 in of panel a's gate boxes.
    "a": (0.62, 3.88, 1.33, 1.42),
    "b": (2.57, 3.88, 1.43, 1.42),
    "c": (4.50, 3.88, 1.88, 1.42),
    "d": (0.62, 2.10, 1.85, 1.32),
    "e": (2.99, 2.10, 3.63, 1.32),
    "f": (0.62, 0.38, 2.74, 1.26),
    "g": (3.89, 0.38, 2.73, 1.26),
}
# How far LEFT of its own axes each panel letter sits, in inches: far enough to clear whatever
# that panel puts in its left gutter (nothing for the schematic, a rotated y label plus ticks
# elsewhere), and never so far that the letter leaves the canvas.
LETTER_DX_IN = {"a": 0.16, "b": 0.52, "c": 0.46, "d": 0.44, "e": 0.46, "f": 0.46, "g": 0.46}
# Panel letters align with the TOP of their title. a, b and c carry two-line titles, whose top
# is a further line-height above the axes, so those three letters are raised to match.
LETTER_DY = {"a": 1.17, "b": 1.17, "c": 1.17}


def build(apply_style, panel_letter):
    apply_style(sizes=(8,7,6))
    fig=plt.figure(figsize=(FIG_W,FIG_H))
    # Pin the tight bbox to the authored canvas (see module docstring). Transparent, zero-width,
    # behind everything: it contributes extent and no ink.
    fig.patches.append(mpatches.Rectangle((0,0),1,1,transform=fig.transFigure,
                                          fill=False,ec="none",lw=0,zorder=-10))
    fns={"a":draw_6a,"b":draw_6b,"c":draw_6c,"d":draw_6d,"e":draw_6e,"f":draw_6f,"g":draw_6g}
    for k,(x0,y0,w,h) in BOXES.items():
        ax=fig.add_axes([x0/FIG_W, y0/FIG_H, w/FIG_W, h/FIG_H])
        fns[k](ax); ax.set_title(TITLES[k],loc="left")
        panel_letter(ax,k,case="lower",dx=-LETTER_DX_IN[k]/w,dy=LETTER_DY.get(k,1.06))
    out=os.path.dirname(os.path.abspath(__file__))
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
    print("wrote fig6_two_gate.{png,pdf}")
