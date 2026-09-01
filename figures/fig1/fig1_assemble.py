"""PopRetrieve Figure 1: from perturbation signatures to population-to-population drug retrieval.

Figure 1 is the paper's visual thesis, and it is read in one order:

    WHAT IS POPULATION RETRIEVAL?
      a  Task                         one query, one candidate library, two representations
      b  Why averaging can fail       the same mean shift can hide opposite fates for a minority
      c  What mathematically changes  the same pair, scored at two resolutions
      d  How ranking can change       means tie, distributions separate, the preference flips

    HOW SHOULD WE EVALUATE AND FORMALIZE IT?
      e  Why evaluation can mislead   objective-aligned versus independent evaluation
      f  How this study evaluates it  the evidence ladder, and how far each body of work reports
      g  Mean retrieval is a limit    the population score\'s lambda -> 0 endpoint
      h  Population scoring is itself a continuum, from mean aggregation to worst-case emphasis

THE 2026-08-31 REBUILD, AND WHAT IT WAS FIXING
----------------------------------------------
The eight panels were each correct and did not read as one argument. Three faults, all visual:

  * b, c and d were three point clouds. They answer three different questions (biology, formalism,
    consequence) and looked like three views of one experiment, so the reader had to reconstruct
    the progression from the caption.
  * e and f carry the paper\'s conceptual contribution, the objective-utility mismatch and the
    evidence hierarchy, and were drawn at the weight of supporting notes.
  * g and h read as ordinary result curves, disconnected from the schematics above them.

The repair is layered, not additive. fig1_style.py freezes four colour roles and one type ladder
for the whole figure; every panel imports them and none redefines. Panel widths are no longer
equal, because the panels are not equal: e is the widest in row 2 because it states the question
the paper exists to answer.

TYPE
----
Authored at 6.90 in, the width it prints at, so nominal point size IS printed point size. This
figure sets its own floor at 6.5 pt rather than the deck\'s 5 pt (figstyle.MIN_PT): 5 pt is a
production limit, and Figure 1 is the figure an editor reads first. build() asserts the 6.5 pt
floor over every drawn Text artist, mathtext sub/superscripts included at their effective 0.7x
size, and refuses to return a figure that breaks it.

The panel letters are drawn here at 9.5 pt rather than through figstyle.panel_letter\'s fixed
8 pt, because this figure\'s whole ladder sits one step above the rest of the deck. A letter set
at the deck default would be the smallest heading on the page it labels.

Rebuild: python fig1_assemble.py
"""
import os
import re
import sys

import matplotlib.pyplot as plt
import matplotlib.text as mtext

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

STEM = "fig1_problem"

from figstyle import pin_canvas, soften_axes, strip_titles  # noqa: E402
from fig1_style import PT_ANNOT, PT_FLOOR, PT_LETTER, PT_TICK, PT_TITLE, TEXT  # noqa: E402

from fig1a import draw_1a  # noqa: E402
from fig1b import draw_1b  # noqa: E402
from fig1c import draw_1c  # noqa: E402
from fig1d import draw_1d  # noqa: E402
from fig1e import draw_1e  # noqa: E402
from fig1f import draw_1f  # noqa: E402
from fig1g import draw_1g  # noqa: E402
from fig1h import draw_1h  # noqa: E402

# ------------------------------------------------------------------------------------------
# Geometry, in inches on the printed page
# ------------------------------------------------------------------------------------------
# FOUR ROWS OF TWO, since 2026-08-31. The previous cut put four panels across a 6.90 in canvas,
# which left every panel 0.90 to 1.65 in wide and forced all eight into portrait. Their content is
# not portrait: a is a left-to-right pipeline, b is three horizontal lanes, c is two mirrored rows,
# e is two parallel lanes. Two per row makes every panel about 2 to 3.5 times wider and turns the
# aspect from 0.5 to 1.97 wide-to-tall, which is the shape the drawings actually wanted.
#
# The pairs are the ones that explain each other, so a reader compares across the gutter rather
# than down the page: a with b (the task and why it is hard), c with d (the definition and its
# consequence), e with f (the evaluation problem and how this study answers it), g with h (the two
# analytic continua). Row heights differ because the rows do: e and f are the conceptual centre and
# get the deepest row, g and h carry a cartoon strip above a curve.
FIGW = 6.90

PAD_TOP, PAD_BOT = 0.05, 0.10
# 0.17 and 0.22, matching Figures 2, 3 and 5, since 2026-09-01. They were 0.24 and 0.30 while
# every row also carried a bold conclusion phrase inside its panels and needed the separation to
# keep two phrases from reading as one block. With the phrases gone the band only has to hold a
# 9.5 pt letter, which is 0.13 in. The saving is 0.52 in over four rows and three gaps, and it is
# the whole of this figure's compaction: the panels themselves are schematics whose text is
# absolute while their layout is fractional, so shrinking a row compresses the drawing around type
# that does not shrink with it. Rows give back only the little each row's TIGHTEST panel has
# spare, measured rather than guessed: 0.025 in for b, 0.024 for d, 0.044 for f, 0.022 for g.
LETTER_BLOCK = 0.17
ROW_GAP = 0.22

LETTER_GUTTER = 0.24        # box left edge -> axes left edge, for a panel with no y axis
Y_FURNITURE = 0.46          # extra, for the two panels that have one
RIGHT_MARGIN = 0.06

ROWS = [(("a", "b"), 1.58),
        (("c", "d"), 1.58),
        (("e", "f"), 2.00),
        (("g", "h"), 1.95)]
COL_X = (0.0, FIGW / 2.0)

DATA_PANELS = ("g", "h")    # the only two with axes furniture
CARTOON_H = 0.78            # the strip that gives each curve its intuition
CARTOON_GAP = 0.10
DATA_BELOW = 0.37           # x tick labels and the x label, under the curve


def _boxes():
    """Resolve the rows into per-panel rects, in inches, measured from the FIGURE TOP."""
    rects, letters = {}, {}
    y = PAD_TOP
    for keys, row_h in ROWS:
        y += LETTER_BLOCK
        for k, x0 in zip(keys, COL_X):
            letters[k] = (x0, y)
            if k in DATA_PANELS:
                ax_x = x0 + LETTER_GUTTER + Y_FURNITURE
                ax_w = FIGW / 2.0 - LETTER_GUTTER - Y_FURNITURE - RIGHT_MARGIN - 0.02
                rects[k + "_top"] = (ax_x, y, ax_w, CARTOON_H)
                rects[k] = (ax_x, y + CARTOON_H + CARTOON_GAP, ax_w,
                            row_h - CARTOON_H - CARTOON_GAP - DATA_BELOW)
            else:
                rects[k] = (x0 + LETTER_GUTTER, y,
                            FIGW / 2.0 - LETTER_GUTTER - RIGHT_MARGIN, row_h)
        y += row_h + ROW_GAP
    return y - ROW_GAP + PAD_BOT, rects, letters


FIGH, RECTS, LETTER_XY = _boxes()


def _letter(fig, key):
    """Panel letters in the gutter, on one baseline per row, at this figure's own 9.5 pt.

    Placed in FIGURE coordinates rather than as an axes-fraction offset: a fixed dx would put the
    letter at a different distance on every panel width, and the two columns would never line up.
    """
    x0, row_top = LETTER_XY[key]
    fig.text(x0 / FIGW, 1.0 - (row_top - 0.05) / FIGH, key,
             fontsize=PT_LETTER, fontweight="bold", va="bottom", ha="left", color=TEXT)


_SUBSUP = re.compile(r"\$[^$]*[\^_][^$]*\$")


def _assert_floor(fig, floor=PT_FLOOR):
    """Refuse to return a figure carrying text below THIS figure\'s floor.

    figstyle.save() already enforces the deck\'s 5 pt production limit. This is stricter and runs
    earlier, because the point of the rebuild was legibility rather than compliance: 5 pt is what
    production rejects, 6.5 pt is what a reader can actually take in at 183 mm. Mathtext is
    measured at its effective size, since a sub/superscript prints at 0.7x nominal.
    """
    bad = []
    for t in fig.findobj(mtext.Text):
        s = str(t.get_text())
        if not s.strip() or not t.get_visible():
            continue
        eff = t.get_fontsize() * (0.7 if _SUBSUP.search(s) else 1.0)
        if eff < floor - 1e-6:
            bad.append((round(eff, 2), s.replace("\n", "/")[:40]))
    assert not bad, (
        f"Figure 1 sets its own {floor} pt floor and these are under it: {sorted(bad)[:8]}. "
        f"The fix is to cut the annotation and move the sentence into the caption, not to "
        f"lower the size.")
    return fig


# A symbol is not a claim. Panel a composes its subscripted distances by hand, base at PT_EQ and
# subscript at PT_SMALL, which reproduces mathtext's own 1.43 ratio exactly and prints d with a
# 9.3 pt base; panel h sets its y axis to $D_\beta$ at the same size. Both are correct and both
# are above the cap, so the gate exempts text that is entirely mathtext. A conclusion sentence is
# never wrapped in dollar signs.
_PURE_MATH = re.compile(r"^\s*\$[^$]*\$\s*$")


def _assert_no_titles(fig, cap=PT_ANNOT):
    """Refuse to return a figure in which any PANEL draws non-symbol text above ``cap``.

    This is the mechanical form of the rule in fig1_style: the panels carry evidence and the
    caption carries the argument. A conclusion sentence set over a panel is always the largest
    text on it, so capping panel text at the annotation size is what stops one coming back. The
    panel letters are exempt because this module draws them, not the panels, and they are the
    figure's navigation rather than its claims.

    It is deliberately a size gate and not a wording gate. Nothing here can tell a claim from a
    label, but a claim that has to fit at 7.2 pt beside the marks it describes is a caption
    sentence that has already lost the argument for being on the panel.
    """
    letters = {id(t) for t in fig.texts}
    bad = []
    for t in fig.findobj(mtext.Text):
        s = str(t.get_text())
        if id(t) in letters or not s.strip() or not t.get_visible():
            continue
        if _PURE_MATH.match(s):
            continue
        if t.get_fontsize() > cap + 1e-6:
            bad.append((round(t.get_fontsize(), 2), s.replace("\n", "/")[:44]))
    assert not bad, (
        f"Figure 1 caps panel text at {cap} pt and these are above it: {sorted(bad)[:8]}. "
        f"A panel states no conclusion; move the sentence to the caption.")
    return fig


def build(apply_style, panel_letter):
    # This figure\'s ladder sits one step above the deck\'s (8, 7, 6); see the module docstring.
    # panel_letter is accepted to keep build_all\'s contract and deliberately not used: its size
    # is fixed at 8 pt, which is below this figure\'s own title size.
    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    fig = plt.figure(figsize=(FIGW, FIGH))
    pin_canvas(fig)

    def _ax(key):
        x, top, w, h = RECTS[key]
        return fig.add_axes([x / FIGW, 1.0 - (top + h) / FIGH, w / FIGW, h / FIGH])

    for key, fn in (("a", draw_1a), ("b", draw_1b), ("c", draw_1c), ("d", draw_1d),
                    ("e", draw_1e), ("f", draw_1f)):
        fn(_ax(key))
    draw_1g(_ax("g"), _ax("g_top"))
    draw_1h(_ax("h"), _ax("h_top"))

    for key in "abcdefgh":
        _letter(fig, key)

    # Nature panels carry no titles, and since 2026-09-01 no panel phrases either: the six
    # conclusion sentences this figure drew over itself were the caption\'s own opening clauses,
    # so the figure asserted them twice. _assert_no_titles keeps it that way.
    return _assert_no_titles(_assert_floor(strip_titles(soften_axes(fig))))


if __name__ == "__main__":
    # build() must NOT export. Every export goes through figstyle.save(), which applies the
    # deck-wide 5 pt floor first; a savefig here would ship a figure that never met the gate.
    from figstyle import apply_style, panel_letter, save
    save(build(apply_style, panel_letter),
         os.path.join(os.path.dirname(os.path.abspath(__file__)), STEM))
    print(f"wrote {STEM}.pdf / .svg / .png  ({FIGW} x {FIGH:.2f} in)")
