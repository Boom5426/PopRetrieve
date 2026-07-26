"""DART Figure 5: The benchmark decides the answer.

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

HIR-Bench is also cut from six panels to two, which is the right size for it. Its phase boundary is
designed in and its transfer to real data fails, so it earns main-text space only for the analytic
condition and for the circularity measurement, which is the one place in this paper where
circularity is quantified rather than asserted. The generative schematic (old 6a), the Hit@1 grid
(6c), the regret decomposition (6d) and the sanity checks (6e) move to Extended Data.

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
"""
import os
import sys

import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "fig7")))

# The one canonical output stem for this figure; must equal build_all.STEMS[5], which build_all
# asserts, because that is the name copied to manuscript/latex/figures/fig5.pdf. The legacy
# fig5_hir_bench.* files in this directory are the SUPERSEDED six-panel HIR-Bench figure, not
# another copy of this one.
STEM = "fig5_benchmarks"

from figstyle import pin_canvas
from fig5b import draw_5b                        # analytic flip boundary
from fig5f import draw_5f                        # 2x2: observable vs oracle-derived x CV unit
from fig5_shape import draw_shape                # the oracle's SHAPE picks the winner (real data)
from fig5_gate2 import draw_gate2                # Gate 2, same construct in both settings
from fig5_nat import draw_nat_gate1, draw_nat_premise   # natural-tissue arm, retuned for 6.9 in

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
    "b": "Circularity, measured",
    "c": "The oracle's shape picks the winner",
    # scoped to the tumour on purpose: the constructed arms in this same panel show a gap of
    # +0.007 and -0.002 (fixed pairs), i.e. there the limit is NOT algorithmic. An unscoped title
    # would contradict two of its own three bar groups.
    "d": "Gate 2 in a tumour: an algorithmic limit",
    "e": "Gate 1: divergence overstated",
    "f": "The mean ranks most of it",
}
ROW_LABELS = [
    "From the inside: analytically, inside a synthetic benchmark, and between two real oracles",
    "From the outside: our constructed benchmark, checked against tissue nobody assembled",
]

# LAYOUT, in inches on a 6.9 x 3.58 in canvas.
#   x0, y0 measured from the bottom-left corner; w, h are the AXES box (titles, tick labels, axis
#   labels and panel letters live outside it, in the gutters).
# Panel widths are deliberately unequal: c (the swap between two real external oracles) and d (the
# one constructive finding in the paper, and the panel the Results text sends readers to for the
# robustness numbers) carry the two rows and are the two widest panels; a, e and f are supporting.
# The gutters are sized by the text that has to fit in them, not by a uniform wspace:
#   1.91 -> 2.46  b's two-line row labels ("observable / at query time")
#   3.82 -> 4.78  b's colour-bar label, then c's two-line y-axis label
#   3.05 -> 3.38  e's y-axis label;   5.02 -> 5.45  f's two-line y-axis label
# Vertically, the two rows are packed against their own text: 0.30 in below row 1 for tick labels
# and a's axis label, then the row-2 banner, then row 2's titles.
#
# The canvas was 3.50 in tall with row 2 at y0 = 0.36, which left row 2 too little room underneath:
# panel f's x-axis label hung 4.2 pt (0.059 in) BELOW the bottom edge of the canvas. The export was
# correct only because savefig's tight bbox grew downwards to absorb the overhang, i.e. the exported
# height was set by a collision rather than authored, and the same accident would have silently
# absorbed a wider overhang later. Row 2 is now at y0 = 0.44 on a 3.58 in canvas: the canvas gained
# 0.08 in at the BOTTOM and every panel and banner moved up with it, so nothing changed relative to
# anything else, and the label now sits 0.021 in inside the canvas.
#
# With the overhang gone the tight bbox is pinned to the canvas (see pin_canvas), so the exported
# page is 6.92 x 3.60 in by construction: LaTeX scales it by 6.93/6.92 = 1.001 and the nominal sizes
# below are the printed sizes. It used to export 6.81 x 3.54 in and be scaled UP by 1.018, which was
# harmless for the floor but meant the printed size of every glyph depended on which annotation
# happened to stick out furthest. The typeset float height is unchanged at 3.60 in.
W, H = 6.9, 3.58
RECTS = {                     # x0,   y0,   w,    h     (inches)
    "a": (0.45, 2.23, 1.46, 1.02),
    "b": (2.46, 2.23, 1.36, 1.02),   # includes the colour bar, which is stolen from this box
    "c": (4.78, 2.23, 2.07, 1.02),
    "d": (0.50, 0.44, 2.55, 1.18),
    "e": (3.38, 0.44, 1.64, 1.18),
    "f": (5.45, 0.44, 1.27, 1.18),
}
BANNER_Y = {0: 3.56, 1: 1.93}        # inches from the bottom, va="top"
# the panel letter must clear its own panel's y-axis furniture, which differs a lot between a bare
# strip (e) and a heat map with two-line row labels (b); given here in inches to the LEFT of the
# axes box and converted to the axes-fraction dx that panel_letter() wants
LETTER_IN = {"a": 0.21, "b": 0.56, "c": 0.36, "d": 0.42, "e": 0.30, "f": 0.44}


def build(apply_style, panel_letter):
    apply_style(sizes=(8, 7, 6))
    fig = plt.figure(figsize=(W, H))
    # Pin the tight bbox to the authored canvas, so the exported page size is authored rather than
    # emergent (see the height note above the RECTS table).
    pin_canvas(fig)
    fns = {"a": draw_5b, "b": draw_5f, "c": draw_shape,
           "d": draw_gate2, "e": draw_nat_gate1, "f": draw_nat_premise}

    for k, (x0, y0, w, h) in RECTS.items():
        ax = fig.add_axes([x0 / W, y0 / H, w / W, h / H])
        fns[k](ax)
        ax.set_title(TITLES[k], loc="left", fontsize=8, pad=3.0)   # deck-wide 8 pt titles
        panel_letter(ax, k, dx=-LETTER_IN[k] / w, dy=1.13, case="lower")

    for rr, txt in enumerate(ROW_LABELS):
        fig.text(0.012, BANNER_Y[rr] / H, txt, fontsize=7.0, fontweight="bold", color="#1A1A1A",
                 va="top")

    return fig


if __name__ == "__main__":
    # build() must not write the composite itself. It used to call fig.savefig() for
    # fig5_benchmarks.{png,pdf} at the end, i.e. the standalone `python fig5_assemble.py` shipped
    # the figure that build_all.py deploys WITHOUT ever running figstyle.save()'s 5 pt typography
    # gate: the one export path that skipped the check wrote to exactly the stem that is copied to
    # manuscript/latex/figures/fig5.pdf. Writing only through save() means every path that can
    # produce that file also has to pass the floor.
    from figstyle import apply_style, panel_letter, save
    save(build(apply_style, panel_letter), os.path.join(HERE, STEM))
    print(f"wrote {STEM}.pdf / .svg / .png")
