"""PopRetrieve Figure 5: what population information is worth when candidate responses are observed.

Eight panels, a-h, assembled into fig5_intervention_oracle.{pdf,svg,png}.

THE 2026-09-03 SPLIT
--------------------
This page used to carry both halves of the Phase-II result: the oracle measurement AND what
happens to it under forward prediction. Eight panels could hold both only by giving each half four,
and the two halves do not answer the same question. They are now two figures, and no experiment was
re-run to make the split: every panel on both pages reads the same Phase-II tree it read before.

    Figure 5   candidate responses are OBSERVED. How much is population information worth, where
               does that worth come from, and does anything about the biology locate it?
    Figure 6   candidate responses are PREDICTED. What survives, and why not.

The two task schematics are one function with one switch (figures/phase2_task.py), so a reader
comparing the pages can see that the experiment changed in exactly one station.

WHAT THIS FIGURE ARGUES
------------------------
    the population carries information beyond the mean signature   +0.0303 MRR at the oracle
    two thirds of that is response magnitude, not distribution     +0.0102 remains
    it changes a top-1 decision in a minority of queries           5.6 per cent corrected
    and almost all of it comes from a fifth of the queries         on the rest the mean route is
                                                                   already perfect, at every seed

The last line is the figure's own correction to itself. The headroom correlation reported in an
earlier draft as the strongest explanation of where population scoring pays is reproduced by a null
that keeps the ceiling and destroys the pairing (panel e), so what survives is the ceiling fact and
not a relationship. Of the three gates the plan proposed, only recoverability has a coefficient
that survives conditioning on the mean route's own performance (panel h), and the statistic the
interaction gate used to be built on measured effect size rather than interaction (panel g).

GEOMETRY, AUTHORED 1:1
----------------------
The manuscript text block is 6.951 in and the figure enters with \\includegraphics[width=\\textwidth],
so the canvas is authored at 6.90 in: nominal point size IS printed point size and LaTeX applies
no rescale. figstyle.pin_canvas pins the tight bbox to the authored width.

Two panels per row throughout, which is what the 6.5 pt floor costs: at three across a box is
2.30 in and panel d's three-line tick labels alone need 2.0 in of it.
"""
import os
import re
import sys

import matplotlib.pyplot as plt
import matplotlib.text as mtext

_HERE = os.path.dirname(os.path.abspath(__file__))
_FIGROOT = os.path.abspath(os.path.join(_HERE, ".."))
for _p in (_HERE, _FIGROOT, os.path.join(_FIGROOT, "ed7")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# The one canonical output stem for this figure; build_all asserts it equals STEMS[5], because
# that is the name copied to manuscript/latex/figures/fig5.pdf.
STEM = "fig5_intervention_oracle"

from figstyle import pin_canvas, strip_titles          # noqa: E402
from phase2_style import PT_ANNOT, PT_FLOOR, PT_LETTER, PT_TICK, PT_TITLE, TEXT  # noqa: E402
from fig5a import draw_5a                              # noqa: E402
from fig5b import draw_5b                              # noqa: E402
from fig5c import draw_5c                              # noqa: E402
from fig5d import draw_5d                              # noqa: E402
from fig5e import draw_5e                              # noqa: E402
from fig5f import draw_5f                              # noqa: E402
from fig5g import draw_5g                              # noqa: E402
from fig5h import draw_5h                              # noqa: E402

_SUBSUP = re.compile(r"\$[^$]*[\^_][^$]*\$")

FIGW = 6.90
PAD_TOP, PAD_BOT = 0.05, 0.03
# The panel letter alone. Figure 5 never drew a conclusion phrase over a panel on the composite,
# which calls strip_titles, but it carried a TITLES dict of fourteen of them and three panel files
# still set one for their standalone run. Both are gone; see phase2_style.
LETTER_BLOCK = 0.15
# 0.10, not the 0.22 this ledger was written with. 2026-09-01: measured against the ink rather
# than against the ledger, the corridor a reader saw between two rows here was 0.47 to 0.56 in,
# the loosest in the deck, against 0.21 to 0.32 in Figure 3 and 0.04 in Figure 1. The corridor is
# ROW_GAP + the upper row's UNUSED bottom pad + LETTER_BLOCK less the letter's own height, so
# three terms were generous at once and cutting only one would not have shown. All three are now
# sized against measurement: the bottom pads below, this gap, and LETTER_BLOCK, which holds a
# 9.5 pt letter whose cap height is 0.092 in.
ROW_GAP = 0.10

# (row height in inches, [(key, box width in inches), ...]). Box widths sum to FIGW per row, and
# row height INCLUDES the bottom pad that holds the x apparatus.
#
# Widths are the slot measurements above, not a taste decision. Row 0 gives c the widest box
# because its second y axis needs a right margin no amount of axes width supplies. Row 1 gives e
# 4.20 in because it scores seven methods in one unit. Row 2 gives g 3.90 in because at
# three-across it overflowed by 0.252 in. Row 3 divides 6.90 in among four Tahoe panels in
# proportion to the ink each was measured to need.
# Row heights are a hierarchy decision, measured rather than chosen. On the first cut of this
# ledger the largest panel was e at 17.8 per cent of panel area, and e is the panel whose general
# reading this paper WITHDRAWS: its 0.692 ceiling is substantially an artefact of pooling several
# drugs into each class, and posed as individual drug pairs the same cells give 0.879 (see the
# honesty notes in README.md, and CORRECTIONS.md R18 and R21). Meanwhile a, the schematic that
# defines the three requirements the whole figure is organised around, was 8.9 per cent, and c,
# which carries the differential-response finding, was 9.3. Row 1 gives height back to rows 0 and
# 2, which is the same correction Figure 2 needed for its panel d and Figure 3 for its row 5.
#
# e stays the single largest panel afterwards, at 16.1 per cent, and that is a content constraint
# rather than a claim: it scores seven methods in one unit, and seven two-line categorical labels
# need 3.39 in whatever the panel is worth. What the rebalance buys is that it is no longer
# largest by a clear margin over g, which reports the decision-relevance null.
#
# ROW HEIGHTS DROPPED BY THE MEASURED BOTTOM-PAD SLACK ON 2026-09-01, and by nothing else. Each
# row lost the smallest unused bottom pad among its own panels, less a 0.04 in guard, and every
# panel in that row lost the same amount off its bottom pad. Axes heights are therefore UNCHANGED
# to the hundredth: what left the page is white, not plotting area. Per row: 0.13, 0.12, 0.04,
# 0.04 in.
# Row heights are the tallest axes in the row plus that panel's bottom pad. Two panels per row,
# so every box is at least 2.60 in and every axes at least 1.96 in.
#
# CUT AGAIN ON 2026-09-04, 1.95/1.56/1.50/1.46 to 1.74/1.44/1.20/1.20, and this time the axes DO
# shrink. Two separate findings.
#
# First, white. Rendered at the old ledger, the corridor between rows 1 and 2, from the last ink
# above to the first ink below, measured 0.46 in on a figure whose ROW_GAP is 0.10: panel a's
# 0.28 in bottom pad was entirely unused, because a is a schematic with no x apparatus at all,
# and b's 0.49 in pad used 0.28 of it. a's pad is now 0.11 and b's 0.32, which is what they were
# measured to occupy.
#
# Second, plotting area that was not carrying anything. Rows 3 and 4 held four panels of two to
# four categorical rows each in 1.06 to 1.12 in of axes; e is a single interval against a null
# band. Each row was lowered until this figure's own gates and figures/check_overlaps.py fired,
# and then stepped back: row 2 collides at 1.40 (panel c's tallest value label reaches its own
# legend) and rows 3 and 4 at 1.14 by crowding rather than by collision, so they stop at 1.20.
#
# One collision that appeared during this pass was NOT a layout problem and was fixed at its
# source: panels f and g placed their series keys using a hard-coded copy of their own axes size,
# which no longer matched once a row moved. phase2_style.key_label measures the axes now.
ROWS = [
    (1.74, [("a", 4.45), ("b", 2.45)]),
    (1.44, [("c", 3.30), ("d", 3.60)]),
    (1.20, [("e", 3.60), ("f", 3.30)]),
    (1.20, [("g", 3.40), ("h", 3.50)]),
]

# (left, right, bottom) pad in inches inside the panel BOX. Top is always zero: the panel letter
# sits in the LETTER_BLOCK band above the row. Left pads are each panel's measured y apparatus
# plus the 0.14 in letter reserve, and they differ because the apparatus does: the schematic
# carries no y axis, e carries none either, g and h carry two-line term names.
# Bottom pads hold the x apparatus: d carries three-line tick labels (a two-line group name and
# its n), f a two-line first tick under an axis label, the schematic none.
PADS = {"a": (0.30, 0.06, 0.11), "b": (0.60, 0.06, 0.32),
        "c": (0.58, 0.06, 0.45), "d": (0.74, 0.08, 0.46),
        "e": (0.30, 0.10, 0.38), "f": (0.64, 0.10, 0.44),
        "g": (0.86, 0.10, 0.40), "h": (0.86, 0.10, 0.45)}


def _boxes():
    """Resolve the rows into per-panel axes rects, in inches, measured from the FIGURE TOP."""
    rects, letters = {}, {}
    y = PAD_TOP
    for row_h, panels in ROWS:
        assert abs(sum(w for _, w in panels) - FIGW) < 1e-9, panels
        y += LETTER_BLOCK
        x0 = 0.0
        for k, box_w in panels:
            letters[k] = (x0, y)
            left, right, bottom = PADS[k]
            rects[k] = (x0 + left, y, box_w - left - right, row_h - bottom)
            x0 += box_w
        y += row_h + ROW_GAP
    return y - ROW_GAP + PAD_BOT, rects, letters


FIGH, RECTS, LETTER_XY = _boxes()


def _letter(fig, key):
    """Panel letters in the gutter, one baseline per row, at this figure's own 9.5 pt.

    Drawn as figure text rather than through figstyle.panel_letter so that the size is this
    figure's and the letters are exempt from _assert_no_titles, which inspects axes text only.
    """
    x, top = LETTER_XY[key]
    fig.text(max(x + 0.02, 0.02) / FIGW, 1.0 - (top - 0.02) / FIGH, key,
             fontsize=PT_LETTER, fontweight="bold", color=TEXT, ha="left", va="top")


def _assert_floor(fig, floor=PT_FLOOR):
    """Refuse to return a figure carrying text below THIS figure's floor.

    figstyle.save() enforces the deck's 5 pt production limit. This is stricter and runs earlier:
    5 pt is what production rejects, 6.5 pt is what a reader can take in at 176 mm. Mathtext is
    measured at its effective size, a sub/superscript printing at 0.7x nominal.

    This gate is the reason the figure lost three panels. When it fires, the fix is to cut the
    annotation into the caption or to give the panel more slot; it is never to lower the size.
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
        f"Figure 5 sets its own {floor} pt floor and these are under it: {sorted(bad)[:8]}. "
        f"Cut the annotation into the caption; do not lower the size.")
    return fig


def _assert_no_titles(fig, cap=PT_ANNOT):
    """Refuse to return a figure in which any PANEL draws text above ``cap``.

    The panels carry evidence and the caption carries the argument. A conclusion sentence set over
    a panel is always the largest text on it, so capping panel text at the annotation size is what
    stops one coming back. The panel letters are exempt because this module draws them, not the
    panels, and they are the figure's navigation rather than its claims.

    It is deliberately a size gate and not a wording gate. Nothing here can tell a claim from a
    label, but a claim that has to fit at 7.2 pt beside the marks it describes is a caption
    sentence that has already lost the argument for being on the panel.
    """
    letters = {t for t in fig.texts}
    bad = []
    for t in fig.findobj(mtext.Text):
        if t in letters or not str(t.get_text()).strip() or not t.get_visible():
            continue
        if t.get_fontsize() > cap + 1e-6:
            bad.append((round(t.get_fontsize(), 2), str(t.get_text()).replace("\n", "/")[:44]))
    assert not bad, (
        f"Figure 5 caps panel text at {cap} pt and these are above it: {sorted(bad)[:8]}. "
        f"A panel states no conclusion; move the sentence to the caption.")
    return fig


DRAW = {"a": draw_5a, "b": draw_5b, "c": draw_5c, "d": draw_5d,
        "e": draw_5e, "f": draw_5f, "g": draw_5g, "h": draw_5h}


def build(apply_style, panel_letter):
    # This figure's ladder sits one step above the deck's (8, 7, 6). panel_letter is accepted to
    # keep build_all's contract and deliberately not used: its size is fixed at 8 pt.
    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    fig = plt.figure(figsize=(FIGW, FIGH))
    pin_canvas(fig)

    for key, fn in DRAW.items():
        x, top, w, h = RECTS[key]
        fn(fig.add_axes([x / FIGW, 1.0 - (top + h) / FIGH, w / FIGW, h / FIGH]))
        _letter(fig, key)

    # strip_titles clears rc titles so a standalone preview can label itself without the composite
    # inheriting it. No panel states a conclusion on this figure; _assert_no_titles keeps it so.
    return _assert_no_titles(_assert_floor(strip_titles(fig)))


if __name__ == "__main__":
    # build() must NOT export. Every export goes through figstyle.save(), which applies the
    # deck-wide 5 pt floor first; a savefig here would ship a figure that never met the gate.
    from figstyle import apply_style, panel_letter, save
    save(build(apply_style, panel_letter), os.path.join(_HERE, STEM))
    print(f"wrote {STEM}.{{png,pdf,svg}}")
