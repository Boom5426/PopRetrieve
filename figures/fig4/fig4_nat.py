"""Figure 4 panels e and f: the natural-tissue arm, retuned for the 6.9 in print canvas.

WHY THIS FILE EXISTS
--------------------
Panels e (Gate 1 on patient glioblastoma) and f (the premise tested on the same tumours) are drawn
by ``figures/fig7/fig7_natural.py``, which is where they were authored when they were their own
figure. The data loading, the marks, the statistics and the colours all stay there: this module
imports those two draw functions unchanged, so there is exactly one copy of the plotting code and
no possibility of the two versions drifting apart.

What this module adds is GEOMETRY AND TYPOGRAPHY ONLY. Figure 4 is now authored at its final print
width (6.9 in) instead of 11.6 in, so each of these panels is ~1.4-1.7 in wide instead of ~3.2 in,
while the annotation text is at last full size. The interpretive sentences that fit at 11.6 in
("(near-orthogonal)", "additive-predictor limit ... no divergence at all") no longer fit, and at
this size they run across the point cloud. They are shortened here and the sentences they carried
are in the Fig. 4 caption.

Nothing below changes a data value, a statistic, a colour or a mark. Every edit is a set_text,
set_position or set_fontsize on an annotation, plus the axis labels and tick sizes. Each edit is
keyed to the annotation it retunes by a substring of the ORIGINAL text and raises if that
annotation is not found, so an upstream rewording fails the build here instead of silently leaving
the old, too-wide label on the page.

NO NUMBER IS RETYPED HERE. A shortened label is rebuilt from the value fig7_natural drew, never
from digits copied into this file: e's n keeps the count computed from gate1_natural.csv and drops
only the unit, and e's band label takes its endpoints from the same CONSTRUCTED dict the axhspan is
drawn from and refuses to print if the two disagree. Panel f's rho line is not edited at all.

2026-08-31: THE 6.5 pt FLOOR, AND THE BOX THAT PAID FOR IT
----------------------------------------------------------
fig7_natural was authored against the deck's old 5 pt floor and set its own sizes: 5.6 pt for e's
band label and its limit label, 5.8 pt for e's n, 6.0 pt for e's median and f's Spearman line,
6.2 pt for three axis labels, and ``tick_params(labelsize=6)`` on both panels. Figure 4 now sets a
6.5 pt floor (fig4_style.PT_FLOOR, asserted in fig4_assemble._assert_floor), so all 28 of those
artists were under it. Every size below is now taken from the fig4_style ladder rather than typed:

    e   band label 5.6 -> PT_SMALL, limit label 5.6 -> PT_SMALL, n 5.8 -> PT_SMALL,
        median readout 6.0 -> PT_ANNOT, y label 6.2 -> PT_ANNOT, y ticks 6.0 -> PT_TICK
    f   Spearman line 6.0 -> PT_ANNOT, x label 6.2 -> PT_ANNOT, y label 6.2 -> PT_ANNOT,
        both tick axes 6.0 -> PT_TICK

The upstream ``tick_params`` calls are re-issued here at PT_TICK rather than deleted, because
deleting them would mean editing fig7_natural, which still prints Fig. 7 at its own authored size.

WHAT WAS CUT TO PAY FOR THE RAISE, AND WHERE IT GOES
    e   "(near-orthogonal)" leaves the band label, which now reads
        "constructed / mixtures / <lo> to <hi>". The noun "mixtures" was cut with it in an earlier
        pass and is RESTORED here on a third line: at PT_SMALL a first line reading
        "constructed mixtures" is 0.880 in wide and covers the points at (0.99, 0.081) and
        (0.944, 0.217), but the same two words stacked keep the block at 0.490 in and grow it
        upward into empty plot area, clearing every point. "constructed" alone is an adjective
        with no noun, and the caption does not currently supply one. The caption still owes
        "(near-orthogonal)" and the 1-cos divergence scale.
    e   "pairs" leaves the sample size, which now reads "n = 17": the caption states that the
        unit is a patient-drug pair and that the pairs come from ten glioblastoma patients.
    f   both axis labels drop to ONE line in a shared "cos(<quantity> A, B)" grammar. The x label
        loses "of drug ... drug" ("cos(mean signature A, B)") and the y label loses "compartment"
        and "of" ("cos(malignant response A, B)"). The caption must say that A and B are the two
        drugs of a pair and that the response cosine is taken within the MALIGNANT COMPARTMENT,
        which is the word doing real work in the cut. The y label is what forced this: rotated, a
        second line costs WIDTH, and two lines at PT_ANNOT measured 0.53 in against the 0.48 in of
        gutter this panel has.
No size was lowered to make anything fit; the cuts above are what fitting cost.

THE BOX GREW, 2026-08-31. e went from 1.64 x 1.56 in to 1.70 x 1.75, f from 1.27 x 1.56 to
1.43 x 1.75, when j to m left this figure for Supplementary Note 4. Every annotation in both panels
is positioned in DATA coordinates on fixed limits, so none of them moved with the box; what changed
is that the same string now occupies less of the panel, which is the room the raise was taken out
of. Three things did have to be re-tuned against the new box:

    e   the limit label at x = 1.50 was pulled in from x = 1.62, where fig7_natural right-aligns
        it, so its outer edge would not touch f's rotated y label across the gutter. At 1.70 in
        wide with 0.48 in of gutter it still clears, so it stays where it was measured; this is a
        re-check, not a move.
    e   the y label takes labelpad 2.0 pt rather than the 4.0 pt default. At PT_ANNOT the label
        plus its tick labels plus the default pad measures 0.359 in against the 0.36 in of gutter
        before panel d's axes, i.e. it arrived flush against d.
    f   set_anchor("N"). The upstream set_aspect("equal", adjustable="box") shrinks f to a square,
        and the default centre anchor put that square, and the panel letter drawn on it, 0.16 in
        below d's and e's on the taller row. Anchored north the three tops of row 2 line up.

One edit was DELETED rather than retuned: a .replace() that shortened a phrase the upstream rho
line has not carried since its dependency structure moved to the caption. str.replace does not
raise on a miss, so it had been a silent no-op.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "fig7")))

from fig4_style import PT_ANNOT, PT_SMALL, PT_TICK
from fig7_natural import CONSTRUCTED as _CONSTRUCTED
from fig7_natural import draw_b as _draw_gate1_natural
from fig7_natural import draw_c as _draw_premise_natural


def _one(ax, key, panel):
    """The single annotation on ``ax`` whose text contains ``key``.

    Raises if the key matches no annotation or more than one, because a silently skipped edit here
    means a label that overruns its panel, or keeps a stale number, on the printed page.
    """
    hits = [t for t in ax.texts if key in t.get_text()]
    if len(hits) != 1:
        raise KeyError(
            f"panel {panel}: {len(hits)} annotation(s) contain {key!r}, expected exactly 1. "
            f"fig7_natural.py was reworded; re-point this retune at the new text rather than "
            f"letting the un-retuned label print.")
    return hits[0]


def _retune(ax, edits, panel):
    """Apply {substring-of-original-text: {text/position/fontsize/...}} to ax's annotations."""
    for key, spec in edits.items():
        t = _one(ax, key, panel)
        if "text" in spec:
            t.set_text(spec["text"])
        if "position" in spec:
            t.set_position(spec["position"])
        if "fontsize" in spec:
            t.set_fontsize(spec["fontsize"])
        if "ha" in spec:
            t.set_ha(spec["ha"])
        if "va" in spec:
            t.set_va(spec["va"])


def draw_nat_gate1(ax):
    """Panel e. Induced response cosine in patient tumours against our constructed mixtures."""
    _draw_gate1_natural(ax)
    # THE TWO NUMERIC LABELS ARE REBUILT FROM THEIR SOURCES, NOT RETYPED. Shortening a label by
    # typing its digits again is how a panel comes to name a band it is no longer drawing.
    #   the band label takes its endpoints from the same CONSTRUCTED dict that axhspan is drawn
    #   from, and refuses to print if the string fig7_natural composed disagrees with it;
    #   "(near-orthogonal)" is the interpretation and is in the caption, which also gives the
    #   1-cos divergence scale the comparison should use. "mixtures" is STACKED rather than cut:
    #   on one line with "constructed" it is 0.880 in wide and covers two points, on its own line
    #   the block is still 0.490 in and grows into empty plot area. Dropping it would leave the
    #   band named by an adjective with no noun.
    # The band label prints no number, so there is nothing here to rebuild and nothing to check.
    # It used to read "constructed mixtures / 0.014 - 0.044", two hard-typed digits that this
    # function had to guard against drifting from the axhspan they described; both were wrong
    # (CORRECTIONS.md R53). The band's range, median and n are in the caption.
    #   n keeps the count fig7_natural computed from len(gate1_natural.csv) and drops only the
    #   unit; the caption states that the unit is a patient-drug pair over ten glioblastoma donors
    n_lab = _one(ax, "patient-drug pairs", "e")
    n_lab.set_text(n_lab.get_text().replace(" patient-drug pairs", ""))
    _retune(ax, {
        # Centred in the band, on its empty right side. It was pinned at (0.60, 0.075), above the
        # old 0.044 band; the band is the real range now and that position is inside it.
        "constructed\n": {"position": (1.62, 0.5 * (_CONSTRUCTED["cos_lo"]
                                                     + _CONSTRUCTED["cos_hi"])),
                          "fontsize": PT_SMALL},
        # One line, not two. Right-aligned at 1.50 rather than at the spine, the two-line form
        # reached back across the point column AND its outer edge touched panel f's rotated y
        # label in the gutter between the two panels. "cos = 1" restates the y axis, which is
        # already a cosine and already ticked at 1.0, so the half that carries meaning stays.
        "additive-predictor limit": {"text": "no divergence",
                                     "position": (1.50, 0.985),
                                     "fontsize": PT_SMALL},
        # the median is the panel's readout, so it is the one annotation at the ordinary
        # annotation size rather than at the floor
        "median": {"fontsize": PT_ANNOT},
        # n stays on the panel; the unit and the ten donors are in the caption
        "n = ": {"position": (0.60, 1.08), "fontsize": PT_SMALL},
    }, "e")
    # the full label, cos(d_malignant, d_myeloid), is 50 characters: rotated at PT_ANNOT it
    # measures 2.09 in against a 1.75 in axes, i.e. it overhangs 0.17 in at each end and runs past
    # the panel above. It also cannot
    # be set as mathtext here, because matplotlib prints the two subscripts at 0.7x nominal and
    # clearing the 6.5 pt floor would need 9.3 pt, above the 7.2 pt cap fig4_assemble enforces on
    # panel text. The caption defines the symbol.
    # labelpad 2.0 pt, not the 4.0 pt default: this panel has 0.36 in of gutter before panel d's
    # axes box, and at PT_ANNOT the label plus its tick labels plus a 4 pt pad measures 0.359 in,
    # i.e. it arrives flush against d. Two points of pad buys 0.028 in of clearance and still
    # leaves the label and the tick labels visibly apart.
    ax.set_ylabel("induced response cosine", fontsize=PT_ANNOT, labelpad=2.0)
    # fig7_natural sets labelsize=6 for its own canvas; this figure's floor is 6.5
    ax.tick_params(axis="y", labelsize=PT_TICK)


def draw_nat_premise(ax):
    """Panel f. Myeloid-compartment against malignant-compartment response similarity.

    Disjoint compartments, which is what the caption and the Results sentence describe. The
    overlapping mean-signature form is quoted in the Results as a number only; see the docstring
    of fig7_natural.draw_c for why this panel may not draw it.
    """
    _draw_premise_natural(ax)
    # The rho line is composed from the data in fig7_natural and nothing here retypes it. It used
    # to be shortened by a .replace() of " of them from one patient", a phrase the upstream string
    # has not contained since the dependency structure moved to the caption: str.replace does not
    # raise on a miss, so that edit had been a silent no-op. It is deleted rather than re-pointed,
    # because the line it targeted no longer exists.
    # rho is mathtext with no sub/superscript, so it prints at nominal and PT_ANNOT clears the
    # floor without needing the hand-composed treatment e's y label would have needed.
    _one(ax, "Spearman", "f").set_fontsize(PT_ANNOT)
    # BOTH AXIS LABELS ARE NOW ONE LINE, in the same "cos(<quantity> A, B)" grammar, and the words
    # they lost are in the caption. The y label is the binding constraint: rotated, a second line
    # costs 0.12 in of WIDTH, and at PT_ANNOT the two-line form measured 0.53 in of y furniture
    # against the 0.48 in gutter this panel has, i.e. it reached 0.05 in into panel e's axes. The
    # fix is the cut, not a smaller label: at one line the furniture measures 0.41 in.
    #   x  loses "-compartment" and "of": "cos(myeloid response A, B)" is 1.24 in under a 1.43 in
    #      axes. It named the mean signature until 2026-09-01, when the panel was corrected to the
    #      disjoint statistic its caption had always described.
    #   y  loses "compartment" and "of": "cos(malignant response A, B)" is 1.36 in beside a
    #      1.43 in axes, so it no longer overhangs its own spines either
    # The caption must therefore say that A and B are the two drugs of a pair, and that the
    # response cosine is taken WITHIN the malignant compartment.
    ax.set_xlabel("cos(myeloid response A, B)", fontsize=PT_ANNOT)
    ax.set_ylabel("cos(malignant response A, B)", fontsize=PT_ANNOT)
    # fig7_natural sets labelsize=6 for its own canvas; this figure's floor is 6.5
    ax.tick_params(labelsize=PT_TICK)
    # set_aspect("equal", adjustable="box") upstream shrinks this 1.43 x 1.75 in box to a 1.43 in
    # square, and matplotlib's default anchor centres the square in the box: on the taller row that
    # dropped f's axes, and the panel letter drawn on it, 0.16 in below d's and e's. Anchored north
    # the three tops of row 2 line up again. This is the one constant here that the new box moved.
    ax.set_anchor("N")
