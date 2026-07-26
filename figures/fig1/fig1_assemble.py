"""DART Figure 1: Distributional differences are visible, but their value depends on the evaluator.

Five panels, all drawn from code, all schematic: Figure 1 sets the tension and reports no result
from the analysis (no Fig-4 collapse numbers, no +0.119).

Layout note. The figure is authored at the FINAL PRINTED WIDTH. The manuscript text block is
6.93 in (letterpaper, 2 cm margins) and the figure enters with \\includegraphics[width=\\textwidth],
so a canvas wider than that is silently rescaled by LaTeX and every nominal point size shrinks with
it. The previous 11.0 in canvas printed at 0.63x, which turned 6 pt source text into 3.8 pt on the
page and put the figure below the 5 pt Nature Portfolio floor at final size. The canvas is now
6.9 in wide, so the printed scale factor is 1.0 and nominal size == printed size.

Losing 4.1 in of width had to be paid for in height and in structure. The old 2 x 12 grid put a
and b side by side; at 6.9 in that leaves panel a about 3.7 in for a three-lane schematic with
side labels on both flanks, which is not enough. The figure is therefore three rows: a gets the
full width of row 1 (it is a horizontal diagram and reads better wide than tall), b and c share
row 2, and d and e share row 3, with the wider member of each pair given seven of the twelve
columns. Reading order a, b, c, d, e is unchanged and every panel letter is kept.
"""
import os
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from figstyle import pin_canvas

# The one canonical output stem for this figure; must equal build_all.STEMS[1], which build_all
# asserts, because that is the name copied to manuscript/latex/figures/fig1.pdf.
STEM = "fig1_problem"

from fig1a import draw_1a
from fig1b import draw_1b
from fig1c import draw_1c
from fig1d import draw_1d
from fig1e import draw_1e

# Every title states a claim the manuscript makes. In particular e must not say Class C is
# missing: the manuscript states "We report DART under all three classes", with the Class-C
# oracle imported and labelled semi-real.
TITLES = {
    "a": "Same mean shift, opposite fate for a hidden minority",
    "b": "One query, one library, two ways to score",
    "c": "Means tie, distributions separate",
    "d": "A score that grades itself cannot lose",
    "e": "All three evidence classes, reported here",
}
#            row, col0, col1, panel-letter dx
SPANS = {
    "a": (0, 0, 12, -0.021),
    "b": (1, 0, 7, -0.052),
    "c": (1, 7, 12, -0.090),
    "d": (2, 0, 5, -0.072),
    "e": (2, 5, 12, -0.032),
}
FNS = {"a": draw_1a, "b": draw_1b, "c": draw_1c, "d": draw_1d, "e": draw_1e}


def build(apply_style, panel_letter):
    apply_style(sizes=(8, 7, 6))
    # 6.9 in is a hair under the 6.93 in text block, so LaTeX scales by 1.0 and the point sizes
    # below are the sizes that reach the page. Height is free; 6.5 in leaves room for the caption.
    fig = plt.figure(figsize=(6.9, 6.5))
    # The house style saves with bbox_inches="tight", which crops the canvas back to the drawn
    # content and so hands LaTeX a PDF narrower than 6.9 in; \includegraphics then magnifies it
    # again and the authored point sizes are no longer the printed ones. Authoring at print width
    # only means anything if the saved page IS the authored page.
    #
    # This used to be enforced by setting plt.rcParams["savefig.bbox"] = None here, i.e. by
    # mutating global state from inside one figure's build(). It only worked because apply_style()
    # happens to run at the top of every other build() and restores "tight": the correctness of
    # figures 2-6 depended on the ORDER build_all imports them in, and a standalone
    # `python fig1_assemble.py` followed by any other build in the same process would have exported
    # the other figure uncropped. A full-canvas anchor patch pins the tight bbox to the authored
    # 6.9 x 6.5 in canvas with no global side effect, which is what the rest of the deck does.
    pin_canvas(fig)
    # With the bbox pinned to the canvas these margins are literal: they are chosen so the drawn
    # content sits ~0.08 in inside each canvas edge (the left margin also has to clear the panel
    # letters, which hang outside their axes), and get_tightbbox is checked against the canvas to
    # confirm that nothing spills over (measured 0.076-0.117 in of clearance on all four sides).
    gs = fig.add_gridspec(3, 12, height_ratios=[1.06, 1.10, 1.04], hspace=0.24, wspace=0.45,
                          left=0.045, right=0.988, top=0.963, bottom=0.012)
    for key, (row, c0, c1, dx) in SPANS.items():
        ax = fig.add_subplot(gs[row, c0:c1])
        FNS[key](ax)
        ax.set_title(TITLES[key], loc="left", pad=6)
        panel_letter(ax, key, dx=dx, case="lower")

    return fig


if __name__ == "__main__":
    # The standalone path writes through figstyle.save(), which enforces the 5 pt floor before it
    # writes anything: build() must not export by itself, or this file could be shipped from the
    # command line without ever meeting the gate that build_all.py applies.
    from figstyle import apply_style, panel_letter, save
    save(build(apply_style, panel_letter),
         os.path.join(os.path.dirname(os.path.abspath(__file__)), STEM))
    print("wrote fig1 composite")
