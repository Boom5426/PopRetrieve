"""PopRetrieve Figure 1: Distributional differences are visible, but their value depends on the evaluator.

Eight panels. a-f are schematic and set the tension; g and h are this figure's first two MEASURED
panels, and they were added when the Extended Data deck was retired (see below). Figure 1 still
reports no result from the analysis: no Fig-4 collapse numbers, no +0.119.

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

PANELS g AND h, ADDED WHEN THE EXTENDED DATA DECK WAS RETIRED
-------------------------------------------------------------
Both come from figures/edfigs/ed_panels.py, which drew them as ED1b and ED1c; before the Extended
Data consolidation they were main-text Fig. 2c and Fig. 2e. They land in Figure 1 rather than
anywhere else because each is the measured form of a claim this figure previously only drew:

  g  ed_panels.draw_ed1d, energy distance against the residual scale lambda. Panel a asserts that
     a mean signature and a population are two representations of ONE population; g is the limit
     that makes that literal, the measured energy distance falling onto the mean-to-mean distance
     at lambda = 0 (98.50 against 98.50). Mean-signature retrieval is therefore not a rival task
     to be beaten, it is the zero-variance corner of the task in panel a, and the rest of the
     paper is about what happens away from that corner.
  h  ed_panels.draw_ed1e, the subpopulation-coverage aggregate D_beta against temperature beta.
     Panel c scores one pair at two resolutions and leaves the two resolutions looking like two
     separate scores; h shows they are one score read at two temperatures, D_beta running from the
     arithmetic mean over subpopulations (0.7125) at beta -> 0 to the worst-matched subpopulation
     (1.300) at beta -> infinity.

Read together with a and c, they turn the framework panels from assertions into a parameterisation:
one axis (lambda) says where mean retrieval sits inside population retrieval, the other (beta) says
where mean aggregation sits inside coverage. Neither reports a PopRetrieve-versus-baseline outcome,
so deck rule 5 still holds for this figure.

The grid is now 4 x 12, with a and b sharing row 1. Three rows was a page-fit result, not a design
preference: while the caption shared the page with the graphic, a fourth row put the canvas at
7.9 in and pdflatex answered "Float too large for page by 147.66 pt", because the 681 pt text block
had to hold the figure AND a six-entry caption. Captions now set on a following page, so the
graphic owns 9.30 in by itself and the fourth row costs nothing that was not already free. What the
old constraint bought is kept rather than undone: a and b still share row 1, panel a still merges
the candidate library and the ranked list into one ranked column, and panel b still wraps its two
right-flank minority labels onto two lines.

Row 4 is inset, columns 1-6 and 7-12 rather than 0-6 and 6-12, and that is arithmetic rather than
composition. g and h are the only panels here that carry a y axis, and one y apparatus (the tick,
its pad, a three-character tick label and a rotated axis label) measures about 0.35 in, more than
the 0.31 in the left margin leaves. Columns 0-6 was built and measured rather than argued about:
the y label of g starts at x = -0.035 in, its panel letter at -0.165 in, and since pin_canvas makes
the exported page the union of canvas and ink, the PDF comes out 7.07 in wide. LaTeX then scales
that back to the 6.93 in text block at 0.98x, and a deck whose whole point is that nominal size is
printed size is off by 2 per cent everywhere.
Widening the left margin instead is worse: it narrows a, b, c, e and f by about 2 per cent each,
and panel b has no 2 per cent to give. Starting row 4 one column in costs nothing else. Its two
letters therefore sit with their own panels and do not line up with the letters of a, c and e,
which is correct: a letter marks the panel it belongs to, and at columns 0-6 it would have been
marking empty canvas.
"""
import os
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "edfigs")))

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

# g and h are drawn by the Extended Data panel library, not by a fig1*.py of their own. They stay
# there rather than being copied here: ed_panels.load() is the single reader of
# results/exp06_theory_limits/, and a second copy of these two draw functions would be a second
# place for the two endpoint numbers (98.50, 0.7125/1.300) to drift out of step with the results.
import ed_panels

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
    "g": "Mean retrieval is the zero-variance limit of population retrieval",
    "h": "One temperature spans mean aggregation and worst case",
}
#            row, col0, col1, panel-letter dx
SPANS = {
    "a": (0, 0, 6, -0.038),
    "b": (0, 6, 12, -0.055),
    "c": (1, 0, 7, -0.052),
    "d": (1, 7, 12, -0.090),
    "e": (2, 0, 5, -0.072),
    "f": (2, 5, 12, -0.032),
    # Row 4 letters clear a y apparatus the six schematics above do not have, so their dx is the
    # largest in the figure. It is one number for both because g and h are the same width.
    "g": (3, 1, 6, -0.150),
    "h": (3, 7, 12, -0.150),
}
FNS = {"a": draw_1a, "b": draw_1b, "c": draw_1c, "d": draw_1d, "e": draw_1e, "f": draw_1f}
# The Extended Data draw functions take (ax, D), where D is the table bundle ed_panels.load()
# returns. They are listed apart from FNS because D does not exist until build() runs, and loading
# it at import time would make importing this module read a dozen CSVs.
ED_FNS = {"g": ed_panels.draw_ed1d, "h": ed_panels.draw_ed1e}


def _adapt(fn, arg):
    """Wrap a draw function that wants a second argument so every panel is callable as fn(ax)."""
    return lambda ax: fn(ax, arg)


def build(apply_style, panel_letter):
    apply_style(sizes=(8, 7, 6))
    # 6.9 in is a hair under the 6.93 in text block, so LaTeX scales by 1.0 and the point sizes
    # below are the sizes that reach the page. Height used to be the binding constraint, because
    # the figure and its caption shared a 681 pt text block; the caption now sets on a following
    # page and the graphic's budget is 9.30 in. 7.14 in is what the four rows actually cost:
    # 5.91 in of axes, three inter-row gaps of 0.23 in, 0.12 in above and 0.42 in below. The
    # bottom margin is the one that is not cosmetic. Row 4 is the first row in this figure with an
    # x axis, and 0.42 in is what its ticks, tick labels and axis label need; the three schematic
    # rows above needed 0.06 in. 0.42 rather than the 0.38 the ink actually measures, because at
    # 0.38 the descender of the beta in panel h's axis label cleared the canvas edge by 0.014 in,
    # and a page whose width and height are the authored ones only by 0.014 in is one font-metric
    # difference away from not being.
    fig = plt.figure(figsize=(6.9, 7.14))
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
    # 6.9 x 7.14 in canvas with no global side effect, which is what the rest of the deck does.
    pin_canvas(fig)
    # With the bbox pinned to the canvas these margins are literal: they are chosen so the drawn
    # content sits inside each canvas edge (the left margin also has to clear the panel letters,
    # which hang outside their axes), and get_tightbbox is checked against the canvas to confirm
    # that nothing spills over (measured 0.117 left, 0.083 right, 0.054 bottom, 0.028 top). hspace
    # 0.1557, not 0.24, and top 0.9832, not 0.963: the space between rows used to hold an 8 pt
    # title plus 6 pt of pad above every panel. With the titles gone that space is empty, and the
    # panels take it back instead of the canvas keeping it.
    #
    # height_ratios ARE the four axes heights in inches. matplotlib does not normalise them, and
    # the canvas height above was picked so their sum, 5.91 in, is exactly what is left for axes
    # once the two margins and the three gaps come out, which makes the normalisation factor 1.0.
    # Writing them this way is not decoration: row heights are a pure fraction of figsize[1], so
    # growing the canvas for a fourth row stretches every existing row unless the ratios absorb it,
    # and 1.53 / 1.58 / 1.50 are the heights rows 1-3 were tuned at in the three-row layout,
    # reproduced here to within 0.003 in. The new row gets 1.30 in, which is less than the others
    # because it holds two single-axes line plots rather than a multi-part schematic.
    gs = fig.add_gridspec(4, 12, height_ratios=[1.53, 1.58, 1.50, 1.30], hspace=0.1557,
                          wspace=0.45, left=0.045, right=0.988, top=0.9832, bottom=0.0588)
    # Bound once for the whole figure, not once per panel: load() reads every Extended Data table,
    # so a call per panel would re-read the same CSVs for no reason.
    D = ed_panels.load()
    fns = dict(FNS, **{k: _adapt(fn, D) for k, fn in ED_FNS.items()})
    for key, (row, c0, c1, dx) in SPANS.items():
        ax = fig.add_subplot(gs[row, c0:c1])
        fns[key](ax)
        panel_letter(ax, key, dx=dx, case="lower")

    # Nature panels carry no titles; the eight claims in TITLES are the caption's eight entries.
    return strip_titles(soften_axes(fig))


if __name__ == "__main__":
    # The standalone path writes through figstyle.save(), which enforces the 5 pt floor before it
    # writes anything: build() must not export by itself, or this file could be shipped from the
    # command line without ever meeting the gate that build_all.py applies.
    from figstyle import apply_style, panel_letter, save
    save(build(apply_style, panel_letter),
         os.path.join(os.path.dirname(os.path.abspath(__file__)), STEM))
    print("wrote fig1 composite")
