"""Figure 4 panel d: Gate 2, on the SAME construct in constructed and natural data.

Source: results/zhao_gbm/gate2_drug_response.json (analysis/natural/gate2_drug_response.py)
        results/zhao_gbm/gate2_uncertainty.json   (patient-level cluster bootstrap)

WHAT THIS PANEL REPLACES, AND WHY
---------------------------------
The previous version of this panel compared a supervised ceiling of 0.692 in our constructed K562
mixture (HDAC-treated vs JAK-treated cells: a DRUG-RESPONSE partition) against 0.964 in a patient
tumour (malignant vs myeloid control cells: a CELL-TYPE partition). Those are different questions.
Separating a glioma cell from a macrophage is trivial and says nothing about whether a retrieval
score can resolve the drug-response subpopulations inside a candidate population, which is what
Gate 2 is defined on. The 0.964 is withdrawn.

Re-posed as the same question in both settings, the answer inverts twice:

  constructed, one drug vs one drug : ceiling 0.879, unsupervised 0.837, gap +0.007
  natural tumour, one drug vs one drug : ceiling 0.923, unsupervised 0.777, gap +0.117

So (i) the old 0.692 ceiling was largely an artefact of POOLING several drugs into each class, and
(ii) in real tissue the information IS there and unsupervised clustering CANNOT reach it. Gate 2 in
a tumour is an ALGORITHMIC bottleneck, not an informational one, which is the one constructive
finding in this study and the opposite of what we concluded from our own benchmark twice.

TYPOGRAPHY, 2026-08-31: THE LAST PANEL OFF THE DECK'S OLD 5 pt FLOOR
--------------------------------------------------------------------
Everything drawn here was set between 5.6 and 6.2 pt, under the 6.5 pt floor fig4_style declares
and fig4_assemble._assert_floor now enforces. All 18 offenders were RAISED, none was shrunk to fit,
and the sizes come from the fig4_style ladder rather than from numbers typed in here:

  value labels, gap labels and their intervals, the chance keyed label  5.8 -> PT_SMALL (6.5)
  x tick labels 5.8 and y tick labels 6.0                              -> PT_TICK (6.8), by
                                                                          deleting the per-call
                                                                          sizes so the rcParams
                                                                          ladder applies
  the y axis label                                                     6.2 -> PT_ANNOT (7.2)
  the two-entry key, at 5.6                                            deleted, see below

WHAT WAS CUT, AND WHERE IT WENT
-------------------------------
  * THE KEY BOX ("best unsupervised" / "supervised ceiling", 5.6 pt, inside the axes) is gone. The
    same two words are now set DIRECTLY on the two bars of the constructed group, rotated, at
    PT_SMALL. The open/filled encoding is constant across both arms, so one labelled group names
    both, and a direct label cannot detach from the mark it names the way a key can. This also
    returns the upper-left band the key occupied to the bars.
  * THE ROBUSTNESS BLOCK is in the caption, and the disabled copy of its drawing code that sat
    here is deleted. It was four numbers of prose positioned by constants measured against a
    2.55 x 1.18 in axes, i.e. against neither the box this panel had last week nor the one it has
    now, so keeping it "for provenance" only preserved coordinates that were already wrong. The
    numbers themselves live in results/zhao_gbm/gate2_uncertainty.json, which is cited above, and
    caption entry d states both checks: every fixed probe-clusterer pair, and dropping the patient
    that contributes 30 of 36 splits.
  * The three-line tick-label glosses ("(as first reported)", "(like for like)", "(within
    compartment)") were cut on 2026-07-26 and remain in the caption, including that the natural
    comparison is within one compartment of one patient.

THE NEW BOX, 2.28 x 1.75 in (was 2.55 x 1.56)
---------------------------------------------
0.27 in narrower and 0.19 in taller, so three constants measured against the old box were re-tuned:
  * y limit 1.20 -> 1.12. The 1.20 headroom existed to hold the robustness block and the key,
    and both are gone; the tallest ink above the bars is now the natural arm's two-line gap
    interval, whose top measures at 1.069. Spending the freed height on the bars is what makes
    the two direct labels fit inside the constructed bars at 6.5 pt: measured on the printed
    rect they clear their own bar tops by 0.055 in (open) and 0.186 in (filled).
  * x limits -0.62/1.62 -> -0.72/1.72, symmetric about the group centres. The keyed word "chance"
    grew with the type and at the old right limit it OVERLAPPED the natural arm's filled bar by
    0.046 in; in the wider band it clears that bar by 0.027 in and the axes edge by 0.028 in, and
    the same band on the left keeps the first bar off the y axis.
  * the gap label sits 0.065 above the taller bar rather than 0.050: at 6.5 pt the value label
    below it had 0.040 in of clearance, under half the 0.089 in line height of the type it has to
    clear, which closes on any font substitution. At 0.065 the clearance is 0.079 in, in both arms.
The bars are drawn FROM the y floor (bottom=YMIN) rather than from zero. Nothing about them moves,
because everything below 0.45 was clipped anyway; what changes is that their extents no longer
report as 0.45 of an axis-height of ink hanging out of the bottom of the panel box.

The class-pooled arm was dropped on 2026-08-28. It rested on a single split (n_splits = 1) and
reported 0.687/0.700, a second estimate of the same constructed recoverability problem that
main-text Fig. 5e reports as 0.674/0.692 under a different protocol. Two numbers for one quantity
is a contradiction a reader cannot resolve, and the weaker of the two is the one to drop.
"""
import json
import os
import sys

import numpy as np
import matplotlib.pyplot as plt

# Palette and type ladder come from the house-style modules; do NOT re-declare a hex value or a
# point size here. Every panel file used to carry its own copy of the palette, which made
# figstyle's "one edit here recolours the whole deck" untrue: a recolour meant editing 43 files
# and missing one was silent. PURPLE_SOFT is the house colour for "a second experimental arm
# carrying no other semantics" and is imported for the same reason, not spelled out.
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))
sys.path.insert(0, _HERE)
from figstyle import PURPLE_SOFT  # noqa: E402
from fig4_style import POP, PT_ANNOT, PT_SMALL, SHARED, TEXT  # noqa: E402

# fig4_style freezes green for an external readout or a control that performs no retrieval (Fig. 3h
# and Fig. 5e,f), and in this panel colour encodes the experimental ARM, with both bars of an arm
# (unsupervised AND supervised ceiling) sharing it. A green arm here would therefore mean the
# opposite of green next door, so the natural arm takes PURPLE_SOFT, which carries no semantic load.
REPO = os.path.abspath(os.path.join(_HERE, "..", ".."))
SRC = f"{REPO}/results/zhao_gbm/gate2_drug_response.json"
UNC_SRC = f"{REPO}/results/zhao_gbm/gate2_uncertainty.json"
# Patient-level cluster-bootstrap intervals. Absent -> the panel still renders, without them, and
# says so; it does NOT invent an interval.
UNC = json.load(open(UNC_SRC)) if os.path.exists(UNC_SRC) else None

ARMS = [("constructed_drug", "constructed\ndrug vs drug", POP),
        ("natural", "natural tumour\ndrug vs drug", PURPLE_SOFT)]

YMIN, YMAX = 0.45, 1.12      # the bars are drawn from YMIN; see the box note in the docstring
XPAD = 0.72                  # data units of clear band each side of the two group centres
BAR_W = 0.34


def draw_gate2(ax):
    if not os.path.exists(SRC):
        raise FileNotFoundError(
            f"{SRC} missing. Run analysis/natural/gate2_drug_response.py.")
    d = json.load(open(SRC))

    x = np.arange(len(ARMS))
    w = BAR_W
    cols = [c for _, _, c in ARMS]
    unsup = [d[a]["best_unsup"] for a, _, _ in ARMS]
    ceil = [d[a]["ceiling_matched"] for a, _, _ in ARMS]

    ax.set_ylim(YMIN, YMAX)
    # Open = what an unsupervised method reaches, filled = what a supervised probe reaches.
    # Open-versus-filled is the standard journal encoding for this contrast and is what Fig. 3h
    # uses for its controls; the "///" hatch it replaces was a third visual channel spent on a
    # binary that fill alone already carries.
    ax.bar(x - w / 2, [u - YMIN for u in unsup], w, bottom=YMIN, color="white", edgecolor=cols,
           linewidth=0.9, zorder=3)
    ax.bar(x + w / 2, [c - YMIN for c in ceil], w, bottom=YMIN, color=cols, edgecolor="none",
           zorder=3)

    # DIRECT LABELS, replacing the 5.6 pt key box. Rotated inside the two bars of the CONSTRUCTED
    # group, which is the taller pair and is the group a reader meets first; the encoding is
    # constant across arms, so labelling one group names both. Ink on the open bar, white on the
    # filled one. The 0.075 offset lifts both off the chance rule that passes behind the bars.
    #
    # SET ON TWO LINES SINCE 2026-09-05, and that is a height constraint rather than a taste.
    # A label rotated into a bar runs along the bar, so its PRINTED LENGTH is what has to fit
    # between the chance rule and the bar top, and that length does not shrink when the panel
    # does. On one line "best unsupervised" measures 0.68 in, which put this panel's floor at
    # 1.59 in of axes and made it the tallest thing in Figure 4's lower half. Broken at the
    # space the run is 0.48 in, the floor is 1.20 in, and no word was dropped: "best" and
    # "ceiling" are the two words that stop the pair reading as two competing methods, which is
    # the misreading this panel exists to prevent.
    for dx, lab, col in ((-w / 2, "best\nunsupervised", TEXT),
                         (w / 2, "supervised\nceiling", "white")):
        ax.text(x[0] + dx, YMIN + 0.075, lab, rotation=90, rotation_mode="anchor", ha="left",
                va="center", fontsize=PT_SMALL, color=col, zorder=6)

    for xi, (u, c, (arm, _, _)) in enumerate(zip(unsup, ceil, ARMS)):
        ax.text(xi - w / 2, u + 0.008, f"{u:.3f}", ha="center", fontsize=PT_SMALL, color=TEXT)
        ax.text(xi + w / 2, c + 0.008, f"{c:.3f}", ha="center", fontsize=PT_SMALL, color=TEXT)
        # The GAP is the finding, and it is the median of the PAIRED per-split differences, not
        # the difference of the two marginal medians drawn as bars. Those are not the same number
        # (a median is not linear), and quoting the larger of the two would overstate the result:
        # for the natural arm the difference of medians is +0.147 while the paired median is
        # +0.117. The paired statistic is the correct one and is what the text reports.
        gap = d[arm]["gap_matched"]
        # Drawn as a vertical double arrow at the group centre with thin leaders to the two bar
        # tops. The previous bar-top-to-bar-top diagonal ran straight through the printed values.
        # The mark is INK when the gap clears 0.05 and SHARED grey when it does not, which pairs
        # it with the weight and colour of the gap label directly above it. It used to be MEAN
        # orange, which fig4_style freezes for the evaluator-derived, circular arm: orange on this
        # panel's one honest, externally checked finding said the opposite of what the figure's
        # colour key says. The arm's own colour is not available either, because the natural arm's
        # double arrow stands at the seam between its two bars and would vanish into the filled one.
        gcol = TEXT if gap > 0.05 else SHARED
        ax.plot([xi - w / 2, xi], [u, u], lw=0.5, ls=(0, (2, 1.6)), color=gcol, zorder=5)
        ax.plot([xi, xi + w / 2], [c, c], lw=0.5, ls=(0, (2, 1.6)), color=gcol, zorder=5)
        if gap > 0.05:
            ax.annotate("", xy=(xi, c), xytext=(xi, u),
                        arrowprops=dict(arrowstyle="<->", lw=0.9, color=gcol), zorder=6)
        else:
            # two arrowheads inside a 0.013-tall span collide into a blob; a plain rule reads as
            # "these two are the same height", which is exactly what the number says
            ax.plot([xi, xi], [u, c], lw=0.9, color=gcol, zorder=6)
        # The gap carries a 95% interval from a PATIENT-level cluster bootstrap. It is printed
        # rather than drawn as a whisker because the bars are marginal medians while the gap is a
        # median paired difference, so an interval hung off the bar tops would imply an arithmetic
        # relationship that does not hold.
        lab = f"{gap:+.3f}"
        if UNC and arm in UNC and not np.isnan(UNC[arm]["ci95"][0]):
            lo, hi = UNC[arm]["ci95"]
            # interval on its own line under the gap. Set on one line these two labels are wider
            # than the 1.0 in that separates the two arms at print size, so the constructed
            # interval ran into the tumour one. Stacking is also the honest layout: every arm that
            # HAS a cluster-bootstrap interval prints it, at the same size.
            lab += f"\n[{lo:+.3f}, {hi:+.3f}]"
        # placed ABOVE the taller bar, not between the two bar tops: a label hung between them
        # collides with both value labels wherever the two bars are close.
        # One size for both arms: the constructed gap used to be set 0.4 pt smaller to de-emphasise
        # it, which at print size put the smallest type in the figure on a number the caption
        # quotes. Emphasis is carried by WEIGHT and by the coloured double arrow below.
        ax.text(xi, max(u, c) + 0.065, lab, ha="center", va="bottom", fontsize=PT_SMALL,
                linespacing=1.25, fontweight="bold" if gap > 0.05 else "normal",
                color=TEXT if gap > 0.05 else SHARED, zorder=7)

    ax.axhline(0.5, ls="--", lw=0.8, color=SHARED, zorder=1)
    ax.set_xlim(-XPAD, len(ARMS) - 1 + XPAD)
    # keyed at the RIGHT end of the rule, in the band the widened x limits open up: on the left the
    # word laps onto the first open bar, and at the old right limit it lapped onto the filled bar
    # of the natural arm.
    ax.text(len(ARMS) - 1 + XPAD - 0.03, 0.506, "chance", ha="right", va="bottom",
            fontsize=PT_SMALL, color=SHARED)

    ax.set_xticks(x)
    # no per-call sizes on either axis: the tick labels take PT_TICK from the rcParams ladder that
    # fig4_assemble sets, which is what keeps this panel in step with the rest of the figure.
    ax.set_xticklabels([l for _, l, _ in ARMS])
    # two lines: rotated, the one-line label is wider than the axes is tall
    ax.set_ylabel("accuracy recovering\nthe true partition", fontsize=PT_ANNOT)
    ax.set_yticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    # the y range runs past 1.0 to hold the gap intervals, but accuracy only goes to 1.0; the spine
    # is bounded so it does not advertise an axis that carries no data
    ax.spines["left"].set_bounds(YMIN, 1.0)
    for s in ("right", "top"):
        ax.spines[s].set_visible(False)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(2.28, 1.75))
    draw_gate2(ax)
    # No ax.set_title, and no typed point size anywhere in this file. This panel's title lives in
    # fig4_assemble.TITLES["d"], "Recoverability in a tumour: an algorithmic limit"; the standalone
    # copy that used to sit here was set at 8 pt, above the PT_ANNOT cap that
    # fig4_assemble._assert_no_titles enforces, and survived only because strip_titles() deletes it
    # before that gate runs. A second wording of the claim that never prints is a place for the two
    # to drift apart, so there is one wording and it is the composite's.
    out = os.path.join(_HERE, "4gate2.png")
    fig.savefig(out, dpi=200, bbox_inches="tight")
    print(f"wrote {out}")
