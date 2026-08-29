"""PopRetrieve Figure 1: Distributional differences are visible, but their value depends on the evaluator.

Six panels, all drawn from code, all schematic: Figure 1 sets the tension and reports no result
from the analysis (no Fig-4 collapse numbers, no +0.119).

Layout note. The figure is authored at the FINAL PRINTED WIDTH. The manuscript text block is
6.93 in (letterpaper, 2 cm margins) and the figure enters with \\includegraphics[width=\\textwidth],
so a canvas wider than that is silently rescaled by LaTeX and every nominal point size shrinks with
it. The previous 11.0 in canvas printed at 0.63x, which turned 6 pt source text into 3.8 pt on the
page and put the figure below the 5 pt Nature Portfolio floor at final size. The canvas is now
6.9 in wide, so the printed scale factor is 1.0 and nominal size == printed size.

Panel a is new: the figure used to open on the premise panel, so a claim about hidden
subpopulations arrived before the reader had been told what the retrieval task IS. The pipeline
now comes first and the premise reads as a statement about that pipeline. Every later letter moves
back one place, and the panel modules were renamed with them so that fig1<letter>.py still draws
panel <letter>.

The grid stays 3 x 12, with a and b sharing row 1. Stacking them as two full-width rows was tried
and rejected on a measurement, not on taste: at four rows the canvas needs 7.9 in, and pdflatex
then reports "Float too large for page by 147.66 pt" for this float, because the 681 pt text block
has to hold the figure AND a six-entry caption. Three rows at 6.15 in is the geometry that fits.
Both panels of row 1 therefore lost about half their width, which cost each of them a redesign:
panel a merges the candidate library and the ranked list into one ranked column, and panel b wraps
its two right-flank minority labels onto two lines so they stop overrunning the canvas.
"""
import os
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from figstyle import pin_canvas, soften_axes, strip_titles

# The one canonical output stem for this figure; must equal build_all.STEMS[1], which build_all
# asserts, because that is the name copied to manuscript/latex/figures/fig1.pdf.
STEM = "fig1_problem"

from fig1a import draw_1a
from fig1b import draw_1b
from fig1c import draw_1c
from fig1d import draw_1d
from fig1e import draw_1e
from fig1f import draw_1f

# TITLES ARE NO LONGER DRAWN. Every claim below is now the opening sentence of its own entry in
# the Figure 1 caption, which is where a Nature-family figure puts explanation; strip_titles() at
# the end of build() removes them from the composite. The dict is kept because it is the shortest
# statement of what each panel is FOR, and because the caption must be checked against it: if a
# panel's claim changes, both this dict and the caption entry have to change together.
TITLES = {
    "a": "One population, two representations, one ranking",
    "b": "Same mean shift, opposite fate for a hidden minority",
    "c": "The same pair, scored at two resolutions",
    "d": "Means tie, distributions separate",
    "e": "Aligned evaluation can reward itself",
    "f": "All three evidence classes, reported here",
}
#            row, col0, col1, panel-letter dx
SPANS = {
    "a": (0, 0, 6, -0.038),
    "b": (0, 6, 12, -0.055),
    "c": (1, 0, 7, -0.052),
    "d": (1, 7, 12, -0.090),
    "e": (2, 0, 5, -0.072),
    "f": (2, 5, 12, -0.032),
}
FNS = {"a": draw_1a, "b": draw_1b, "c": draw_1c, "d": draw_1d, "e": draw_1e, "f": draw_1f}


def build(apply_style, panel_letter):
    apply_style(sizes=(8, 7, 6))
    # 6.9 in is a hair under the 6.93 in text block, so LaTeX scales by 1.0 and the point sizes
    # below are the sizes that reach the page. Height is NOT free: the figure and its caption share
    # a 681 pt text block, and pdflatex reports "Float too large for page" the moment their sum
    # exceeds it. 6.15 in is the height that fits alongside the six-entry caption; the number is
    # checked by compiling the manuscript, not by eye.
    fig = plt.figure(figsize=(6.9, 5.25))
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
    # 6.9 x 6.15 in canvas with no global side effect, which is what the rest of the deck does.
    pin_canvas(fig)
    # With the bbox pinned to the canvas these margins are literal: they are chosen so the drawn
    # content sits ~0.08 in inside each canvas edge (the left margin also has to clear the panel
    # letters, which hang outside their axes), and get_tightbbox is checked against the canvas to
    # confirm that nothing spills over (measured 0.076-0.117 in of clearance on all four sides).
    # hspace 0.15, not 0.24, and top 0.985, not 0.963: the space between rows used to hold an 8 pt
    # title plus 6 pt of pad above every panel. With the titles gone that space is empty, and the
    # panels take it back instead of the canvas keeping it. The canvas also loses 0.55 in of
    # height, which the six-entry caption needs, since removing the titles moves 6 claims into it.
    gs = fig.add_gridspec(3, 12, height_ratios=[1.06, 1.10, 1.04], hspace=0.15, wspace=0.45,
                          left=0.045, right=0.988, top=0.978, bottom=0.012)
    for key, (row, c0, c1, dx) in SPANS.items():
        ax = fig.add_subplot(gs[row, c0:c1])
        FNS[key](ax)
        panel_letter(ax, key, dx=dx, case="lower")

    # Nature panels carry no titles; the six claims in TITLES are the caption's six entries.
    return strip_titles(soften_axes(fig))


if __name__ == "__main__":
    # The standalone path writes through figstyle.save(), which enforces the 5 pt floor before it
    # writes anything: build() must not export by itself, or this file could be shipped from the
    # command line without ever meeting the gate that build_all.py applies.
    from figstyle import apply_style, panel_letter, save
    save(build(apply_style, panel_letter),
         os.path.join(os.path.dirname(os.path.abspath(__file__)), STEM))
    print("wrote fig1 composite")
