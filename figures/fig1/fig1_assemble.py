"""PopRetrieve Figure 1: response representation, scoring rule, and how the result is judged.

Figure 1 answers two questions and nothing else. It does not preview a result, name a dataset or
mention forward prediction; Figures 2 to 6 do that. The two questions are:

    WHAT INFORMATION IS RETAINED?
      a  The two layers, kept apart    representation (mu or P), then the rule that reads it
      b  Why averaging can fail        the same mean shift can hide opposite fates for a minority
      c  What is actually computed     one pair of populations, three scoring rules
      d  What that does to a ranking   both mean scores tie, the population score separates

    HOW SHOULD THAT INFORMATION BE JUDGED?
      e  Why evaluation can mislead    objective-aligned versus less score-aligned evaluation
      f  How this study evaluates it   the evidence ladder, and how far each body of work reports
      g  P contains mu as a limit      the population distance\'s lambda -> 0 endpoint
      h  Population scoring is itself a continuum, from mean aggregation to worst-case emphasis

THE ONE TERMINOLOGY RULE THIS FIGURE EXISTS TO FIX
--------------------------------------------------
A mean representation is not direction-only. mu carries a direction AND a magnitude, and it is
the COSINE that throws the magnitude away. So "direction-only" names a SCORING RULE, the mean
cosine, and never a representation. Panels a, c and d were rebuilt on 2026-09-03 around that
distinction, because the paper\'s own measurement depends on it: restoring magnitude to a mean
signature is worth +0.399 in Hit@1 and adding the full distribution on top of it a further
+0.048 (Fig. 2a). A figure that had collapsed the first two rungs into one would have made the
larger of those two effects invisible by construction.

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

PAD_TOP, PAD_BOT = 0.05, 0.04
# 0.15 and 0.11 since 2026-09-04, down from 0.17 and 0.22. The band only has to hold a 9.5 pt
# letter, whose ink measures 0.09 in, and the gap only has to say that one row has ended. Both
# were sized when every row also carried a bold conclusion phrase inside its panels and needed
# the separation to keep two phrases from reading as one block; the phrases went on 2026-09-01
# and the band did not follow them down. Measured on the render rather than chosen: the white
# between the last ink of one row and the letter of the next was 0.26 in on all three corridors.
# With PAD_BOT this is 0.47 in of the figure's height, and it is white in every case.
#
# The rows themselves are near their content. Panels a, c and d are laid out in absolute inches
# and points, so a shorter row does not compress them, it clips them; a asserts its own height
# for that reason. Rows 3 and 4 are fractional and gave back the slack their tightest panel was
# measured to have: 0.08 in for the e/f row, 0.15 for g/h once the cartoon strip lost the 0.12 in
# of white above its marks. Rows 1 and 2 gave nothing, because b and d already fill them.
LETTER_BLOCK = 0.15
ROW_GAP = 0.11

LETTER_GUTTER = 0.24        # box left edge -> axes left edge, for a panel with no y axis
Y_FURNITURE = 0.32          # extra, for the two panels that have one
# 0.32, not 0.46. 2026-09-01: this figure's row corridors measure 0.04 in, the tightest in the
# deck, and five of its six panel boundaries measure 0.03. The sixth, g|h, measured 0.32,
# because only g and h carry a y axis and this constant was 0.14 in wider than the tick labels
# and y label actually occupy. ax_w is defined against it, so both axes GAIN that 0.14 in and
# g's right edge does not move; only h's furniture slides left, to a 0.24 in corridor.
RIGHT_MARGIN = 0.06

ROWS = [(("a", "b"), 1.58),
        (("c", "d"), 1.58),
        (("e", "f"), 1.92),
        (("g", "h"), 1.80)]
COL_X = (0.0, FIGW / 2.0)

DATA_PANELS = ("g", "h")    # the only two with axes furniture
CARTOON_H = 0.66            # the strip that gives each curve its intuition; 0.78 until
                            # 2026-09-04, when the render showed 0.12 in of white over its marks
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


# A symbol is not a claim. Panel h sets its y axis to $D_\beta$ at PT_EQ, which is the smallest
# nominal size whose 0.7x subscript still clears this figure's 6.5 pt floor, so it is correct and
# above the cap; the gate therefore exempts text that is entirely mathtext. Panel c composes its
# subscripts from two artists instead and needs no exemption, and panel a carried a third case
# until 2026-09-03 and now draws no subscript at all. A conclusion sentence is never wrapped in
# dollar signs.
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

    # SLOTS b AND c EXCHANGED THEIR CONTENT ON 2026-09-05, and the module names were left alone,
    # as in fig3_assemble and fig4_assemble: fig1c.py draws panel b. Two reasons, and they point
    # the same way. Citation order: the Results cite the scoring-rule pair first and the
    # shared-mean pair second, so with the old assignment panel c was cited before panel b.
    # Grouping: row 1 now holds the representation and the three rules that read it, and row 2
    # holds the two cases where the mean is the same and the populations are not, which is what
    # each row is arguing. The two boxes are identical, 3.45 x 1.58 in, so nothing was resized.
    for key, fn in (("a", draw_1a), ("b", draw_1c), ("c", draw_1b), ("d", draw_1d),
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
