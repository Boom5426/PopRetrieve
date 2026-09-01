"""PopRetrieve Figure 3: the population advantage weakens, and can change direction, once the
judge stops sharing the retrieval objective.

ARCHETYPE: quantitative grid with two hero panels (a and h). Thirteen panels, six rows,
one argument. Four numbers are its skeleton, and everything else on the
page exists to support or to qualify one of them:

    +0.129   response matching: population retrieval wins, decisively        (a)
     0.000   mechanism recovery, the SAME rankings: the advantage is gone    (a, b)
    +0.276   external functional similarity: a real population signal        (h)
    +0.097   after the response-magnitude channel is partialled out          (h, m)

  Row 1  a | b   The reversal, and that it is distribution-wide rather than an outlier artifact.
  Row 2  c | g   The biological gain that does exist is small and does not grow with response
                 divergence, across 765 stratified queries and across 239 real-data tasks.
  Row 3  d | e | f   The pre-specified diagnostic fails three ways: it does not enrich for the
                 gain, its own reliability axis runs opposite to true divergence, and its verdict
                 does not sort queries by divergence.
  Row 4  h | i   The external functional readout, in aggregate and per query.
  Row 5  j | k   What the endpoint choice does, and the channel that explains it.

THE 2026-08-31 REBUILD
----------------------
Three things changed that are about the argument rather than the drawing.

  * COLOUR WAS ENCODING THE WRONG VARIABLE, in the figure's most important panel. Panel a draws
    two distributions of the SAME quantity, the population-minus-mean advantage on the same 480
    queries; only the judge differs. They were blue and orange, the deck's colours for population
    and mean retrieval, so the panel said the right-hand distribution was the mean method. Panel e
    coloured the gate's reliability axis orange and panels j and k coloured the MoA-nDCG evaluator
    orange, and none of the three is a mean-signature retriever. fig3_style now makes blue and
    orange a statement about SIGN, carried by half-planes behind a neutral distribution, and
    reserves them as object colours only where methods are genuinely compared.

  * PANEL c NO LONGER CLAIMS "NEGLIGIBLE", because that word depended on a chosen denominator.
    The largest quartile mean, +0.0062, is 0.6 per cent of the nominal [0, 1] metric range, 2.6
    per cent of the metric's observed range, and 53 per cent of the metric's own interquartile
    range; the paired Cohen's d is 0.33. Picking the flattering denominator is the error this
    paper exists to criticise. What the data support without a choice is that the gain does not
    grow with response divergence: Spearman rho = +0.050, p = 0.165 over all 765 queries, and the
    four quartile intervals overlap. The old panel drew four bars on an axis truncated at 0.012,
    where that non-trend read as a rise.

  * PANEL g NO LONGER LETS A MEAN STAND FOR A SHIFT. The constructed cross-line mixtures have the
    largest dataset mean, +0.00426, and a median of exactly 0.000 with only 18 per cent of tasks
    above zero; the within-line tasks have 56 per cent above zero at a mean of +0.00038. The mean
    is a few large positives, not a broad advantage, and 102 of the 239 tasks select the same
    candidate under both methods. The panel now shows the tasks, not only their means.

THE POWER PANELS LEFT THE PAGE, 2026-08-31. Two panels used to sit between rows 4 and 5, showing
achieved power and the queries needed for 80 per cent power in the highest response-divergence
quartile. They answered the one objection this paper's central negative result invites, and they
answered it well, but they are third-tier diagnostics and they cost a whole row on a page whose
argument is rows 1 to 4. Their numbers moved to Supplementary Note 2 in full, so nothing is lost:
achieved power 1.00 for minority-state coverage against 0.06 for MoA-nDCG, and 45 queries needed
against 20,844, a difference driven by a twelvefold gap in standard deviation rather than by effect
size. The Results now cite that Note rather than the figure.

Removing them took the canvas from 9.20 to 7.96 in, a 13.5 per cent shorter page, and lifted panel
a from 15.6 to 17.5 per cent of panel area without changing any other panel's size. The surviving
l and m were relabelled j and k.

Panels j and k are re-authored from the retired Extended Data module ed5/ed5.py (draw_a and
draw_b), reading the same file, because that module sets 5.2 to 5.6 pt type and this figure has a
6.5 pt floor.

GEOMETRY, IN INCHES ON THE PRINTED PAGE
---------------------------------------
Authored at 6.90 in, the width it prints at, so nominal point size IS printed point size. The
float budget is the 9.461 in text block less about 16/72 in of float overhead, i.e. 9.238 in, so
the canvas is 9.20 in and exports at 9.22.

Thirteen panels on one page is genuinely tight, and the ledger says so honestly rather than
pretending otherwise: rows 5 and 6 give their panels under 0.65 in of axes height. That is the
budget, and the response to it is to cut annotation into the caption, never to shrink type. Row
widths are unequal inside a row because the panels are: g needs width for 239 tasks spread about
zero, h needs a label column for five method rows, and b, d and i do not.

Rebuild: python fig3_assemble.py
"""
import os
import re
import sys

import matplotlib.pyplot as plt
import matplotlib.text as mtext

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# The one canonical output stem; build_all.STEMS[3] holds the same string and the build fails if
# the two drift apart. This is the name copied to manuscript/latex/figures/fig3.pdf.
STEM = "fig3_collapse"

from figstyle import pin_canvas, strip_titles  # noqa: E402
from fig3_style import PT_ANNOT, PT_FLOOR, PT_LETTER, PT_TICK, PT_TITLE, TEXT  # noqa: E402

from fig3a import draw_3a  # noqa: E402
from fig3b import draw_3b  # noqa: E402
from fig3c import draw_3c  # noqa: E402
from fig3d import draw_3d  # noqa: E402
from fig3e import draw_3e  # noqa: E402
from fig3f import draw_3f  # noqa: E402
from fig3g import draw_3g  # noqa: E402
from fig3h import draw_3h  # noqa: E402
from fig3i import draw_3i  # noqa: E402
from fig3j import draw_3j  # noqa: E402
from fig3k import draw_3k  # noqa: E402

# ------------------------------------------------------------------------------------------
# The inch ledger
# ------------------------------------------------------------------------------------------
FIGW = 6.90

PAD_TOP, PAD_BOT = 0.05, 0.08
# The panel letter alone. It was 0.24 in while every panel also stated a bold conclusion phrase;
# removing those phrases (see fig3_style) returns 0.42 in to the six rows, which is most of what
# made rows 5 and 6 cramped. The height a figure spends on sentences is height it does not spend
# on evidence.
LETTER_BLOCK = 0.16
# 0.16, not 0.22. 2026-09-01, measured against ink: this figure's bottom pads have NO slack left
# (the smallest unused pad in a row runs -0.03 to 0.05 in, i.e. the x apparatus fills them), so
# unlike Figures 4 and 5 the only white here to reclaim is the gap itself. Corridors go from
# 0.21-0.32 in to 0.14-0.25. Cutting further would work on paper and not on the page: the
# tightest boundary, row 1 to row 2, is set by c's x label, which already sits 0.01 in below its
# own box.
ROW_GAP = 0.16

# (row height in inches, [(key, box width in inches), ...]). Box widths sum to FIGW per row.
# TWO HERO ROWS, 2026-08-31. Row heights are not a taste decision: they were measured against
# this figure's own tiering and found inverted. The five tier-3 diagnostics (d, j, k, l, m)
# averaged 6.6 per cent of panel area against 6.1 per cent for the four tier-2 panels, and k and
# m were drawn as large as i, a discovery panel. A page that gives its diagnostics discovery
# weight tells the reader the wrong thing before they read a single label.
#
# Rows 1 and 4 hold the four numbers that are this figure's skeleton, so they take the height,
# and the two diagnostic rows give it up. The total is unchanged at 6.95 in, so nothing outside
# these six numbers moves. Resulting area share: a 13.1 -> 15.6 per cent, h 11.0 -> 13.1,
# k 7.9 -> 5.9, m 7.7 -> 6.0; tier 1 averages 12.0 per cent against tier 3's 5.2.
ROWS = [
    (1.52, [("a", 4.00), ("b", 2.90)]),
    (1.20, [("c", 2.75), ("g", 4.15)]),
    (1.00, [("d", 2.10), ("e", 2.40), ("f", 2.40)]),
    (1.46, [("h", 4.10), ("i", 2.80)]),
    (0.92, [("j", 3.60), ("k", 3.30)]),
]

# (left, right, bottom) pad in inches inside the panel BOX. Top is always zero: the phrase is
# drawn at transAxes y = 1.0 and sits in the LETTER_BLOCK band. Left pads hold the panel's y
# apparatus plus 0.24 in reserved for the letter, and they differ because the apparatus does:
# h and l carry a column of method names, b c e f i j k m carry a rotated label plus numeric
# ticks, and a and d carry a rotated label only.
# LEFT PADS OF THE SECOND-COLUMN PANELS WERE CUT ON 2026-09-01 to a common rule: keep the
# measured furniture plus 0.14 in for the letter, and give the rest back as axes width. Measured
# unused left pad was b 0.24, e 0.25, i 0.19, k 0.49 in; k's alone made the j|k corridor 0.59 in,
# the widest in the deck. First-column pads are NOT cut: their slack is the page margin, which is
# already 0.01 in here, and cutting them would push ink off the left edge.
PADS = {"a": (0.74, 0.10, 0.42), "b": (0.60, 0.10, 0.44),
        "c": (0.78, 0.10, 0.40), "g": (1.02, 0.10, 0.42),
        "d": (0.76, 0.10, 0.42), "e": (0.59, 0.10, 0.42), "f": (0.70, 0.10, 0.42),
        "h": (1.34, 0.10, 0.36), "i": (0.67, 0.10, 0.38),
        "j": (1.20, 0.10, 0.38), "k": (0.37, 0.10, 0.38)}


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

    Figure coordinates rather than a transAxes offset: this figure has eleven distinct axes
    widths, and a fixed dx would put the letter a different distance out on each of them.
    """
    x0, row_top = LETTER_XY[key]
    fig.text(x0 / FIGW, 1.0 - (row_top - 0.04) / FIGH, key,
             fontsize=PT_LETTER, fontweight="bold", va="bottom", ha="left", color=TEXT)


_SUBSUP = re.compile(r"\$[^$]*[\^_][^$]*\$")


def _assert_floor(fig, floor=PT_FLOOR):
    """Refuse to return a figure carrying text below THIS figure's floor.

    figstyle.save() enforces the deck's 5 pt production limit. This is stricter and runs earlier:
    5 pt is what production rejects, 6.5 pt is what a reader can take in at 183 mm. Mathtext is
    measured at its effective size, a sub/superscript printing at 0.7x nominal.

    Thirteen panels on one page makes this the deck's tightest figure, which is exactly why the
    gate is here. The fix when it fires is to CUT the annotation into the caption.
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
        f"Figure 3 sets its own {floor} pt floor and these are under it: {sorted(bad)[:8]}. "
        f"Cut the annotation into the caption; do not lower the size.")
    return fig


def _assert_no_titles(fig, cap=PT_ANNOT):
    """Refuse to return a figure in which any PANEL draws text above ``cap``.

    This is the mechanical form of the rule in fig3_style: the panels carry evidence and the
    caption carries the argument. A conclusion sentence set over a panel is always the largest
    text on it, so capping panel text at the annotation size is what stops one coming back. The
    panel letters are exempt because fig3_assemble draws them, not the panels, and they are the
    figure's navigation rather than its claims.

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
        f"Figure 3 caps panel text at {cap} pt and these are above it: {sorted(bad)[:8]}. "
        f"A panel states no conclusion; move the sentence to the caption.")
    return fig


DRAW = {"a": draw_3a, "b": draw_3b, "c": draw_3c, "d": draw_3d, "e": draw_3e, "f": draw_3f,
        "g": draw_3g, "h": draw_3h, "i": draw_3i, "j": draw_3j, "k": draw_3k}


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
    # inheriting it. The one phrase each panel states over itself is drawn ink via fig3_style.title
    # and survives on purpose.
    return _assert_no_titles(_assert_floor(strip_titles(fig)))


if __name__ == "__main__":
    # build() must NOT export. Every export goes through figstyle.save(), which applies the
    # deck-wide 5 pt floor first; a savefig here would ship a figure that never met the gate.
    from figstyle import apply_style, panel_letter, save
    save(build(apply_style, panel_letter),
         os.path.join(os.path.dirname(os.path.abspath(__file__)), STEM))
    print(f"wrote {STEM}.pdf / .svg / .png  ({FIGW} x {FIGH:.2f} in)")
