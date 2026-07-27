"""EvalShift Figure 4: the apparent gains do not survive independent evaluation.

Nine panels, one argument, read row by row. This is the metric-class ladder and the paper's
central figure.

  Row 1 (a-d)  Class A -> Class B. One scorer, one query set: the only thing that changes is
               the class of metric doing the judging. A Class-A gain of +0.129 becomes a
               Class-B loss of -0.037, and the gate meant to concentrate the advantage does
               not concentrate it.
  Row 2 (e-g)  Why the gate cannot rescue it, and what the real data actually show. The
               gate's own reliability axis is anti-correlated with true response divergence,
               and across 239 real-data tasks the coverage advantage is statistically real,
               practically negligible, and confined to the mixtures we constructed. Panel g
               plots the DISTRIBUTION, not a count of "dominant" tasks: the threshold sits
               inside the noise band and the seed is not a replicate.
  Row 3 (h-i)  Class C, an independent functional oracle: drug-drug functional similarity from
               GDSC2 dose-response AUC profiles, with the three SciPlex3 lines held out. Energy
               retrieval BEATS the correctly specified mean incumbent here (+0.276 vs +0.083),
               the one such win in the study, but a query-dependent scalar that compares no
               distributions reaches +0.232 and partialling it out leaves energy +0.097.

TITLES ARE CLAIMS, AND THEY WERE WRONG HERE
-------------------------------------------
Until 2026-07-26 this file still carried the row-3 titles of the WITHDRAWN potency framing:
"Class C: an external functional oracle (measured drug potency)", "similarity is anti-aligned
with potency", "a scalar that ignores the query wins every query". The panels below them had
already been rebuilt on the functional-similarity oracle and showed the opposite: energy leads
(+0.276) and wins 62 of 103 queries against a scalar that is itself query-DEPENDENT. A title that
contradicts its own axes is the exact failure this paper is about, so all three now state what
the plotted numbers show, and match Fig. 4's caption in the manuscript.

AUTHORED AT PRINT SIZE (2026-07-26 re-cut)
------------------------------------------
The manuscript's text block is 6.93 in wide and every figure enters with
\\includegraphics[width=\\textwidth]. This figure used to be authored 11.4 in wide, so LaTeX
shrank it by 0.605x on the page and its 5.6-8 pt source text printed at 3.4-4.8 pt: below the
5 pt floor Nature Portfolio enforces at FINAL PRINTED SIZE. The build-time gate in figstyle.py
measures NOMINAL size, so it reported the figure clean while the printed page failed.

The canvas is therefore 6.90 in wide, the width it is printed at, and the scale factor is 1.0:
nominal point size IS printed point size. Panel geometry is set in INCHES here rather than
through gridspec ratios, because at 1:1 the space a y-axis label or a panel letter needs is a
fixed physical quantity (about 0.5 in and 0.34 in) and does not scale with the panel it belongs
to; expressing it as a fraction of a 12-column grid is what produced the uneven gutters and the
collisions in the 11.4 in version.

The canvas is 0.605x its old width, so annotation that used to be shrunk by LaTeX now competes
with the panels for real space. Every panel and every panel letter is kept. What was cut is
on-panel prose that the Fig. 4 caption already carries verbatim: panel g's second x-label line,
panel h's two-line gloss on the dotted remainder, and panel i's "the scalar is better here".
Nothing was rescued by shrinking type below the floor.

Rebuild: python fig4_assemble.py
"""
import os
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# The one canonical output stem for this figure; must equal build_all.STEMS[4], which build_all
# asserts, because that is the name copied to manuscript/latex/figures/fig4.pdf.
STEM = "fig4_collapse"

from fig4a import draw_4a
from fig4b import draw_4b
from fig4c import draw_4c
from fig4d import draw_4d
from fig4e import draw_4e
from fig4f import draw_4f
from fig4g import draw_4g
from fig4h import draw_4h, TITLE_4H
from fig4i import draw_4i, TITLE_4I

TITLES = {
    "a": "Same queries,\nopposite verdicts",
    "b": "MoA-nDCG gain\ncenters on zero",
    "c": "Minority-coverage\ngain is negligible",
    "d": "Non-recommended\nqueries gain as much",
    "e": "The gate axis points\nthe wrong way",
    "f": "Recommendation cannot\nsort by divergence",
    "g": "Real, negligible, confined to mixtures",
    "h": TITLE_4H,
    "i": TITLE_4I,
}

ROW_LABELS = [
    "Class A $\\rightarrow$ Class B: the same rankings, judged by a metric that does not share "
    "their objective",
    "Why the gate cannot rescue it, and what 239 real-data tasks show",
    "Class C: an independent functional oracle (drug$-$drug functional similarity, GDSC2 "
    "dose-response)",
]

# ------------------------------------------------------------------------------------------
# Geometry, in inches on the printed page
# ------------------------------------------------------------------------------------------
FIGW = 6.90                 # the width the figure is printed at; text block is 6.93 in

PAD_TOP = 0.02              # trimmed away by savefig's tight bbox; kept so nothing touches an edge
PAD_BOT = 0.02
BANNER_H = 0.072            # ink height of one line of 6.8 pt bold row-banner text
BANNER_GAP = 0.055          # banner baseline -> top of the row's tallest panel title
TITLE_BLOCK = 0.293         # title pad (4 pt) + two 8 pt lines; every row has a two-line title
ROW_GAP = 0.09              # bottom of one row's x-label -> top of the next row's banner

# Per panel: (key, left pad, axes width). The left pad is the physical room the panel's y-axis
# apparatus and its bold letter need, which is why it is a constant and not a share of the row.
# ``below`` is the room the row's x tick labels and x label need under the deepest axes in it.
#
# RESIDUAL PASS (2026-07-26). Three numbers here changed, all of them clearances measured on the
# rendered page rather than judged by eye. Row widths are unchanged panel by panel where they
# matter, so the exported PDF is the same width as before and LaTeX still prints it at 1:1.
#   * row 1 axh 0.78 -> 1.05. Panel a's two summary blocks sat on the Class-A violin's real
#     kernel tail. The fix needs a data-free band above the plotted view (see fig4a.py), and
#     0.27 in more height is what buys that band WITHOUT flattening the violins.
#   * panel c pad 0.50 -> 0.59, width 1.08 -> 0.99. Panel b's three-line note cleared panel c's
#     rotated y label by 1.2 pt, the tightest text-to-text gap in the deck. The two changes
#     cancel, so panel c's right edge, panel d and the row's right edge do not move; panel c's
#     y-axis apparatus moves 0.09 in right, for a measured 7.7 pt gap. Note the direction: the
#     first attempt narrowed panel b instead, which does open the same gap, but panel b's note
#     is anchored at 0.97 of ITS axes and there is only 0.575 in of free zone right of that
#     panel's dashed zero line, so moving the note left put it 0.8 pt off the zero line. The
#     free space has to come from panel c, which has it.
#   * panel h pad 1.05 -> 1.51, width 4.03 -> 3.57. Its five category labels are one line each
#     now instead of two (see fig4h.py) and the longest is 1.38 in, so the label column has to
#     be 1.51 in wide to hold them without reaching further left than the labels already did.
#     The 0.46 in comes out of the axes, whose right 40% is data-free.
ROWS = [
    dict(banner=0, axh=1.05, below=0.39,
         panels=[("a", 0.50, 1.44), ("b", 0.46, 1.24), ("c", 0.59, 0.99), ("d", 0.50, 1.12)]),
    dict(banner=1, axh=1.05, below=0.38,
         panels=[("e", 0.50, 1.55), ("f", 0.50, 1.48), ("g", 0.38, 2.43)]),
    dict(banner=2, axh=1.00, below=0.28,
         panels=[("h", 1.51, 3.57), ("i", 0.46, 1.30)]),
]

FNS = {"a": draw_4a, "b": draw_4b, "c": draw_4c, "d": draw_4d, "e": draw_4e,
       "f": draw_4f, "g": draw_4g, "h": draw_4h, "i": draw_4i}

GUTTER_LEAD = 0.16          # inches from the previous panel's right edge to the letter's left edge


def _layout():
    """Resolve the inch geometry into (figure height, per-panel rect, per-panel letter x, banner y).

    ``rects[key]`` is (axes left, axes top from the figure top, width, height) in inches and
    ``letters[key]`` is the letter's left edge, one GUTTER_LEAD in from where the panel to its
    left ends. Aligning the letters on the gutter rather than on a fixed offset from their own
    axes is what puts a, e and h in one column: panel h reserves 1.51 in for its categorical y
    labels and a fixed -0.34 in offset left its letter floating over them.
    """
    rects, letters, banners = {}, {}, []
    y = PAD_TOP
    for row in ROWS:
        y += BANNER_H
        banners.append(y)                                   # banner baseline, from the top
        ax_top = y + BANNER_GAP + TITLE_BLOCK
        x = 0.0
        for key, pad, w in row["panels"]:
            letters[key] = x + GUTTER_LEAD
            x += pad
            rects[key] = (x, ax_top, w, row["axh"])
            x += w
        y = ax_top + row["axh"] + row["below"] + ROW_GAP
    figh = y - ROW_GAP + PAD_BOT
    return figh, rects, letters, banners


FIGH, RECTS, LETTER_X, BANNER_Y = _layout()
FIGSIZE = (FIGW, FIGH)


def build(apply_style, panel_letter):
    apply_style(sizes=(8, 7, 6))
    fig = plt.figure(figsize=FIGSIZE)

    axes = {}
    for key, (x, top, w, h) in RECTS.items():
        ax = fig.add_axes([x / FIGW, 1.0 - (top + h) / FIGH, w / FIGW, h / FIGH])
        FNS[key](ax)
        ax.set_title(TITLES[key], loc="left", pad=4.0)
        axes[key] = ax

    # Panel letters in the gutter to the left of each panel, on one baseline per row. A fixed
    # axes-fraction offset (the old dx=-0.11) placed the letter twice as far out on a double-width
    # panel as on a narrow one, so the row never lined up.
    for key, ax in axes.items():
        x_in, _top, w_in, h_in = RECTS[key]
        panel_letter(ax, key, dx=(LETTER_X[key] - x_in) / w_in,
                     dy=1.0 + TITLE_BLOCK / h_in, case="lower")

    for row, y_in in zip(ROWS, BANNER_Y):
        fig.text(GUTTER_LEAD / FIGW, 1.0 - y_in / FIGH, ROW_LABELS[row["banner"]],
                 fontsize=6.8, fontweight="bold", color="#1A1A1A", ha="left", va="baseline")

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
    print(f"wrote fig4 composite (9 panels, 3 rows) at {FIGW:.2f} x {FIGH:.2f} in")
