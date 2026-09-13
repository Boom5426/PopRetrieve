"""PopRetrieve Figure 6: what survives when candidate responses are predicted rather than observed.

Eight panels, a-h, assembled into fig6_prediction_bottleneck.{pdf,svg,png}.

WHY THIS PAGE EXISTS SEPARATELY FROM FIGURE 5
----------------------------------------------
Until 2026-09-03 both halves of the Phase-II result shared one eight-panel page. They answer
different questions and were competing for the same room. Figure 5 keeps the oracle: candidate
responses are OBSERVED, and the question is what population information is worth and where that
worth comes from. This page changes exactly one thing about that experiment, and measures what
happens.

No experiment was re-run for the split. Every panel here reads the same Phase-II tree, and panels
e, f and h were on the previous page unchanged. Panel a is the same drawing as Figure 5 panel a,
from the same function with one station switched (figures/phase2_task.py), so that the one change
is visible rather than asserted.

WHAT THIS FIGURE ARGUES
------------------------
    the oracle advantage does not survive forward prediction   -0.0356 MRR for the best predictor
    it does not attenuate, it inverts                          retained fraction -1.17
    and the deficit is a magnitude error, not a shape error    -0.0020 once magnitude is controlled

The third line is the correction this page exists to make. On the same predictions the
magnitude-aware mean loses 0.0335 of the same 0.0356, although it reads no distribution at all: an
additive predictor hands every scorer a population whose magnitude is an average over the other
cell lines, and a scorer that reads magnitude pays for that error where a cosine does not. Panel f
is the constructive test of the remaining explanation, a predictor that gets interaction fidelity
right for the first time, and it does not close the gap either.

GEOMETRY, AUTHORED 1:1
----------------------
The manuscript text block is 6.951 in and the figure enters with \\includegraphics[width=\\textwidth],
so the canvas is authored at 6.90 in: nominal point size IS printed point size and LaTeX applies
no rescale. figstyle.pin_canvas pins the tight bbox to the authored width.

Two panels per row throughout. Row 1 gives c the wide box because it scores seven predictors in one
unit and its seven one-line names need 1.15 in of gutter before the axis begins.
"""
import os
import re
import sys

import matplotlib.pyplot as plt
import matplotlib.text as mtext

_HERE = os.path.dirname(os.path.abspath(__file__))
_FIGROOT = os.path.abspath(os.path.join(_HERE, ".."))
for _p in (_HERE, _FIGROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# The one canonical output stem for this figure; build_all asserts it equals STEMS[5], because
# that is the name copied to manuscript/figures/fig5.pdf.
STEM = "fig6_prediction_bottleneck"

from figstyle import pin_canvas, strip_titles          # noqa: E402
from phase2_style import PT_ANNOT, PT_FLOOR, PT_LETTER, PT_TICK, PT_TITLE, TEXT  # noqa: E402
from fig6a import draw_6a                              # noqa: E402
from fig6b import draw_6b                              # noqa: E402
from fig6c import draw_6c                              # noqa: E402
from fig6d import draw_6d                              # noqa: E402
from fig6e import draw_6e                              # noqa: E402
from fig6f import draw_6f                              # noqa: E402
from fig6g import draw_6g                              # noqa: E402
from fig6h import draw_6h                              # noqa: E402

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
# CUT AGAIN ON 2026-09-04, 1.95/1.62/1.58/1.52 to 1.74/1.42/1.34/1.32, alongside the same pass on
# Figure 5, which this figure was split from and whose ledger it inherited.
#
# The bottom pads were the larger error and are corrected first. Rendered, the x apparatus under
# every panel with an axis measured 0.28 in, against pads of 0.42 to 0.45; panel a is a schematic
# and used none of its 0.28 in. Pads are now what the apparatus was measured to occupy, so a
# quarter of an inch per row leaves the page without any axes losing plotting area.
#
# The rows then lost what was left, checked panel by panel rather than by a uniform fraction: c
# holds seven one-line predictor names and now runs at a 0.159 in pitch against 0.167 before, and
# h is a text ledger and keeps the height its four boxes and two section rules need. Neither this
# figure's own gates nor figures/check_overlaps.py fires anywhere in the new ledger.
ROWS = [
    (1.74, [("a", 4.45), ("b", 2.45)]),
    (1.42, [("c", 4.30), ("d", 2.60)]),
    (1.34, [("e", 3.55), ("f", 3.35)]),
    (1.32, [("g", 3.55), ("h", 3.35)]),
]

# (left, right, bottom) pad in inches inside the panel BOX. Top is always zero: the panel letter
# sits in the LETTER_BLOCK band above the row. Left pads are each panel's measured y apparatus
# plus the 0.14 in letter reserve: c carries seven one-line predictor names, d and g two-line
# ones, the schematic and the ledger none. Bottom pads hold the x apparatus.
PADS = {"a": (0.30, 0.06, 0.11), "b": (0.58, 0.06, 0.30),
        "c": (1.15, 0.10, 0.31), "d": (0.76, 0.08, 0.31),
        "e": (0.63, 0.10, 0.31), "f": (0.60, 0.06, 0.31),
        "g": (0.92, 0.10, 0.31), "h": (0.30, 0.06, 0.02)}


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

    When it fires, the fix is to cut the annotation into the caption or to give the panel more
    slot; it is never to lower the size.
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
        f"Figure 6 sets its own {floor} pt floor and these are under it: {sorted(bad)[:8]}. "
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
        f"Figure 6 caps panel text at {cap} pt and these are above it: {sorted(bad)[:8]}. "
        f"A panel states no conclusion; move the sentence to the caption.")
    return fig


DRAW = {"a": draw_6a, "b": draw_6b, "c": draw_6c, "d": draw_6d,
        "e": draw_6e, "f": draw_6f, "g": draw_6g, "h": draw_6h}


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
