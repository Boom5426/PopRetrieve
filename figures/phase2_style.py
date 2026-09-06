"""The frozen visual vocabulary of Figure 5. Every panel imports from here; none redefines.

WHY THIS FILE EXISTS
--------------------
Figures 1 to 4 each acquired one of these during the 2026-08-31 typography pass. Figure 5 was
last, and by 2026-09-01 it was the worst page in the deck by a wide margin: 239 of its 263 text
artists sat below 6.5 pt and 33 of them at exactly 5.0 pt, which is the size Nature Portfolio
rejects rather than a size a reader can take in at 176 mm. Every one of its fourteen panels failed
the floor. A reader turning from Figure 4 to Figure 5 watched the type shrink by a fifth.

The cause was structural rather than careless. When the Extended Data deck was retired on
2026-08-30, seven of its panels landed here, and they landed as a three-across row and a
four-across row at 1.06 to 1.50 in wide. A panel that narrow cannot carry 6.5 pt: measured, the
four-across row needs 0.16 to 0.31 in more than it has for its labels alone. The floor and the
panel count were therefore the same decision, which is why this file arrives together with an
eleven-panel ledger rather than after it.

WHAT THIS FIGURE ARGUES, AND THEREFORE WHAT ITS COLOURS MEAN
-------------------------------------------------------------
Figure 5 states three requirements that connect cellular heterogeneity to a change in candidate
ranking, and then measures them twice: once on material we constructed, and once on Tahoe-100M,
which nobody constructed. Its colour axis is the deck's ordinary one, and unlike Figure 4 it
carries no second meaning:

    POP     blue    distributional / population-level retrieval
    MEAN    orange  mean-signature retrieval, and the additive limit predictors collapse to
    EXT     green   a readout handed information the retrieval method does not have: the
                    supervised, label-given ceilings. It is not a competing method, and it is
                    green precisely so that it can never be misread as one.
    TISSUE  purple  patient tissue, the third kind of material, neither constructed by us nor
                    Tahoe. It is a material, not a method.
    MATERIAL slate  the constructed mixtures, as a reference mark inside a panel whose data are
                    something else. Also a material, not a method.
    SHARED  grey    context, machinery, reference lines, thresholds, anchors

TISSUE had to be added on 2026-09-01 rather than found. Purple was already in the figure carrying
two meanings at once: patient tissue in the Tahoe differential-response and recoverability panels,
and the "cell state" partition in the state-ordering panel, where the SAME purple also drew the
tissue reference line at 0.835. The tissue median and the cell-cycle median differ by 0.006, so
that panel put a purple line through a blue series and labelled it with the other series' colour.
The two partitions are separated by x position and by their own tick labels, and never needed a
colour contrast at all, so they are now one colour and purple means tissue only.

MATERIAL was added for the same reason, one panel over. Orange also carried two meanings: the
additive limit, in the predictor-gain and gate-1 panels and in the divergence-quartile panel, and
"the constructed mixtures" as a reference mark in the two Tahoe panels. The two meanings met on
one axis: the Tahoe differential-response panel drew the constructed-mixture anchor in orange and
the additive ceiling at cosine 1 in near-black, while the gate-1 panel drew that same ceiling, the
same quantity on the same axis, in orange. Orange is the deck's mean-signature colour and cannot
move, so the constructed mixtures moved to slate, and the additive ceiling is now orange in both
panels.

EXT is the one that has to stay disciplined. Panels e, f and the Tahoe recoverability panel all
put a supervised ceiling beside an unsupervised score, and the whole argument in those panels is
that the two are not commensurable: one of them was told the answer. If the ceiling were drawn in
either family colour it would read as a third method that happened to win.

TYPE
----
Authored at 6.90 in, the width it prints at, so nominal point size IS printed point size.
PT_FLOOR is 6.5, asserted in fig5_assemble._assert_floor. Mathtext is measured at its effective
0.7x, which is why PT_EQ is 9.3.

There is no title() helper, and there must not be one. Until 2026-09-01 fig5_assemble carried a
TITLES dict of fourteen conclusion sentences ("Gain is small and sign-inconsistent", "Where theory
predicts gain, there is none"). They were not drawn on the composite, which calls strip_titles, but
three panels still set them for their standalone runs and the dict read as though the figure
asserted them on its face. The claims live in the caption, which is where a claim can be qualified.
fig5_assemble._assert_no_titles caps every panel text at PT_ANNOT so a phrase cannot arrive later:
a size gate rather than a wording gate, because no code can tell a claim from a label, but a claim
that has to fit at 7.2 pt beside the marks it describes has already lost the argument for being on
the panel.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from figstyle import (COMP_SOFT, FOCAL_SOFT, GREEN_SOFT, GREY, INK,  # noqa: E402
                      LIGHT_GREY, META, PURPLE_SOFT, RULE, SLATE, TRACK)

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))   # figures/ -> repo root

# ---------------------------------------------------------------------------------- colour
POP = FOCAL_SOFT            # #5185C0  distributional / population-level
MEAN = COMP_SOFT            # #E99D4E  mean-signature, and the additive limit
EXT = GREEN_SOFT            # #55966B  handed information the retrieval method does not have
TISSUE = PURPLE_SOFT        # #8281B9  patient tissue: a material, never a method
MATERIAL = SLATE            # #4F6D7A  the constructed mixtures, as a reference mark
SHARED = GREY               # #767676  context, thresholds, reference lines, anchors
FAINT = LIGHT_GREY          # #D4D4D4  structure visible without being read
BAR_TRACK = TRACK
HAIRLINE = RULE
TEXT = INK
SUBTLE = META

POP_WASH = "#E4EDF6"
MEAN_WASH = "#FBF0E4"
EXT_WASH = "#E7F0EA"        # the region unsupervised recovery cannot reach, in f

# ---------------------------------------------------------------------------------- type
PT_LETTER = 9.5             # bold panel letter, drawn by fig5_assemble
PT_ANNOT = 7.2              # ordinary annotation, and the cap on all panel text
PT_TICK = 6.8               # axis tick labels
PT_EQ = 9.3                 # any label containing mathtext; 6.5 / 0.7 = 9.286
PT_SMALL = 6.5              # provenance, n, units. This figure's floor.
PT_FLOOR = 6.5
PT_TITLE = 8.5              # passed to apply_style only; no panel may draw at this size

# ---------------------------------------------------------------------------------- weights
LW_HAIR = 0.6
LW_LINE = 1.1
MS_DOT = 24


# ---------------------------------------------------------------------------------- keys
# THE ONE WAY THIS DECK NAMES A COLOURED SERIES, and the reason it exists.
#
# figstyle's presentation layer states that a label is INK or META and that colour reaches the
# reader through marks, not letters. It is not a preference. Measured against white, COMP_SOFT
# sits at 2.23:1, FOCAL_SOFT at 3.84:1, PURPLE_SOFT at 3.63:1 and GREEN_SOFT at 3.52:1, and every
# one of those is under the 4.5:1 that small text is normally held to. Figures 5 and 6 were
# setting forty series names and value labels in exactly those colours at 6.5 pt.
#
# Two cases, and only the second needs this helper:
#
#   * a label that sits against its own marker inherits the hue from the marker. It is set in ink
#     and nothing else is drawn. Figure 5h was already doing this beside coloured dots.
#   * a label with no marker beside it, a key or a series name in open space, gets a swatch of
#     its own and is then set in ink.
#
# The swatch and its name are placed as ONE unit whose width is measured, so a rename moves the
# swatch with the text instead of stranding it at a typed offset.
STUB_W_IN = 0.085           # the mark: shorter than the 6.5 pt name beside it
STUB_GAP_IN = 0.030         # mark -> its name, so the pair reads as one token
STUB_H_IN = 0.026           # a little under the x-height it sits against
STUB_DROP_IN = 0.012        # lifts the bar onto the name's optical centre


def axes_size_in(ax):
    """The axes box in inches, measured. Panels used to carry this as a pair of constants.

    Four panels declared their own AX_W_IN / AX_H_IN copied from their figure's inch ledger, and
    used them to turn a printed point size into an axes fraction. That is a duplicated constant
    with nothing checking it: when a row height changed on 2026-09-04 the constants did not, so
    a key drawn "one line below the axes top" landed wherever the stale ratio put it, and in
    Figure 5f it landed on the n annotation above the panel. The size is measurable here, so it
    is measured here.
    """
    w, h = ax.get_position().size * ax.figure.get_size_inches()
    return float(w), float(h)


def key_label(ax, x, y, text, colour, ax_w_in=None, ax_h_in=None, ha="left", pt=PT_SMALL,
              zorder=5):
    """Draw ``text`` in ink with a ``colour`` swatch before it, in axes coordinates.

    ``x``/``y`` are the anchor of the whole unit: with ha="left" the swatch starts there, with
    ha="right" the text ends there. The axes size is measured from ``ax``; the two size arguments
    are kept only so an existing caller does not break, and are ignored. Returns the unit's width
    as an axes fraction so a caller can assert it fits.
    """
    from matplotlib.patches import Rectangle

    fig = ax.figure
    fig.canvas.draw()
    ax_w_in, ax_h_in = axes_size_in(ax)
    probe = ax.text(0.0, -1.0, text, fontsize=pt, transform=ax.transAxes)
    tw = float(probe.get_window_extent(renderer=fig.canvas.get_renderer()).width)
    probe.remove()
    tw = tw / fig.dpi / ax_w_in

    sw, gap = STUB_W_IN / ax_w_in, STUB_GAP_IN / ax_w_in
    sh, drop = STUB_H_IN / ax_h_in, STUB_DROP_IN / ax_h_in
    total = sw + gap + tw
    x0 = x if ha == "left" else x - total
    ax.add_patch(Rectangle((x0, y + drop), sw, sh, transform=ax.transAxes,
                           fc=colour, ec="none", zorder=zorder, clip_on=False))
    ax.text(x0 + sw + gap, y, text, transform=ax.transAxes, ha="left", va="bottom",
            fontsize=pt, color=TEXT, zorder=zorder)
    return total
