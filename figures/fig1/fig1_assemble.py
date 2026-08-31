"""PopRetrieve Figure 1: from perturbation signatures to population-to-population drug retrieval.

Figure 1 is the paper's visual thesis, and it is read in one order:

    ROW 1   WHAT IS POPULATION RETRIEVAL?
      a  Task                         one query, one candidate library, two representations
      b  Why averaging can fail       the same mean shift can hide opposite fates for a minority
      c  What mathematically changes  the same pair, scored at two resolutions
      d  How ranking can change       means tie, distributions separate, the preference flips

    ROW 2   HOW SHOULD WE EVALUATE AND FORMALIZE IT?
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
FIGW = 6.90

PAD_TOP, PAD_BOT = 0.05, 0.10
LETTER_BLOCK = 0.26         # the band above each row that the bold letter sits in
ROW1_H, ROW2_H = 3.00, 3.70
ROW_GAP = 0.44

LETTER_GUTTER = 0.24        # box left edge -> axes left edge, for a panel with no y axis
Y_FURNITURE = 0.44          # extra, for the two panels that have one
RIGHT_MARGIN = 0.04

# Row shares. These are not equal because the panels are not equal: e states the question the
# paper exists to answer and is the widest in its row. g and h take 24% rather than the 22% a
# first pass gave them, with the 4% coming off e and f, because at 22% a box leaves 0.78 in of
# axes once the letter and the y-axis furniture are paid for, and the three lambda cartoons g
# needs above its curve are not legible at 0.26 in each.
ROW1_SHARE = {"a": 0.26, "b": 0.24, "c": 0.22, "d": 0.28}
ROW2_SHARE = {"e": 0.28, "f": 0.24, "g": 0.24, "h": 0.24}

DATA_PANELS = ("g", "h")    # the only two with axes furniture
# g and h are two axes each: a cartoon strip that gives the curve its intuition, and the curve.
CARTOON_H = 1.00
CARTOON_GAP = 0.20
DATA_BELOW = 0.55           # x tick labels and the x label, under the curve


def _boxes():
    """Resolve the shares into per-panel rects, in inches, measured from the FIGURE TOP."""
    row1_top = PAD_TOP + LETTER_BLOCK
    row2_top = row1_top + ROW1_H + ROW_GAP + LETTER_BLOCK
    figh = row2_top + ROW2_H + PAD_BOT

    rects, letters, x = {}, {}, 0.0
    for k, share in ROW1_SHARE.items():
        w = FIGW * share
        letters[k] = x
        rects[k] = (x + LETTER_GUTTER, row1_top, w - LETTER_GUTTER - RIGHT_MARGIN, ROW1_H)
        x += w
    assert abs(x - FIGW) < 1e-9, x

    x = 0.0
    for k, share in ROW2_SHARE.items():
        w = FIGW * share
        letters[k] = x
        if k in DATA_PANELS:
            ax_x = x + LETTER_GUTTER + Y_FURNITURE
            ax_w = w - LETTER_GUTTER - Y_FURNITURE - RIGHT_MARGIN - 0.04
            rects[k + "_top"] = (ax_x, row2_top, ax_w, CARTOON_H)
            rects[k] = (ax_x, row2_top + CARTOON_H + CARTOON_GAP, ax_w,
                        ROW2_H - CARTOON_H - CARTOON_GAP - DATA_BELOW)
        else:
            rects[k] = (x + LETTER_GUTTER, row2_top, w - LETTER_GUTTER - RIGHT_MARGIN, ROW2_H)
        x += w
    assert abs(x - FIGW) < 1e-9, x
    return figh, rects, letters


FIGH, RECTS, LETTER_X = _boxes()


def _letter(fig, key):
    """Panel letters on one baseline per row, in the gutter, at this figure\'s own 9.5 pt.

    Placed in FIGURE coordinates rather than as an axes-fraction offset: a fixed dx would put the
    letter twice as far out on a 1.65 in panel as on a 0.94 in one, and the row would never line
    up. The baseline is the top of the row\'s axes, so a to d share one and e to h share one.
    """
    row_top = RECTS["a"][1] if key in ROW1_SHARE else RECTS["e"][1]
    fig.text(LETTER_X[key] / FIGW, 1.0 - (row_top - 0.06) / FIGH, key,
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

    for key in list(ROW1_SHARE) + list(ROW2_SHARE):
        _letter(fig, key)

    # Nature panels carry no rc titles; the phrases the panels state over themselves are drawn by
    # the panels at PT_TITLE, and are the caption\'s own opening clauses.
    return _assert_floor(strip_titles(soften_axes(fig)))


if __name__ == "__main__":
    # build() must NOT export. Every export goes through figstyle.save(), which applies the
    # deck-wide 5 pt floor first; a savefig here would ship a figure that never met the gate.
    from figstyle import apply_style, panel_letter, save
    save(build(apply_style, panel_letter),
         os.path.join(os.path.dirname(os.path.abspath(__file__)), STEM))
    print(f"wrote {STEM}.pdf / .svg / .png  ({FIGW} x {FIGH:.2f} in)")
