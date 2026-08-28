"""Figure 5 panel d: Gate 2, on the SAME construct in constructed and natural data.

Source: results/zhao_gbm/gate2_drug_response.json (analysis/natural/gate2_drug_response.py)

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

The class-pooled bar is kept, greyed, because deleting the number the paper previously reported
would hide the correction rather than make it.
"""
import json
import os

import numpy as np
import matplotlib.pyplot as plt

FOCAL, COMP, GREY, INK = "#5185C0", "#E99D4E", "#7A7A7A", "#1A1A1A"
# The natural-tumour arm used the house GREEN. Across the deck GREEN is reserved for readouts that
# are handed information the retrieval method does not have: the "performs no retrieval" controls in
# Fig. 4h and the "supervised, given the labels" ceiling in Fig. 6e,f. In this panel colour encodes
# the experimental ARM, and both bars of every arm (unsupervised AND supervised ceiling) share it,
# so a green arm here means the opposite of green next door. PURPLE is already in the house palette
# and carries no semantic load, so it separates the arms without colliding with anything.
PURPLE = "#8281B9"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = f"{REPO}/results/zhao_gbm/gate2_drug_response.json"
UNC_SRC = f"{REPO}/results/zhao_gbm/gate2_uncertainty.json"
# Patient-level cluster-bootstrap intervals. Absent -> the panel still renders, without them, and
# says so; it does NOT invent an interval.
UNC = json.load(open(UNC_SRC)) if os.path.exists(UNC_SRC) else None

# 2026-07-26: the tick labels were three lines each, the third being a gloss ("(as first
# reported)", "(like for like)", "(within compartment)"). At this figure's print size one bar group
# is 1.15 in wide and those glosses were 0.7-0.8 in of text on a third line; the caption states all
# three in full, including that the natural comparison is within one compartment of one patient.
# The "classes pooled" arm was dropped on 2026-08-28. It rested on a single split
# (n_splits = 1) and reported 0.687/0.700, a second estimate of the same constructed
# recoverability problem that main-text Fig. 6e reports as 0.674/0.692 under a different
# protocol. Two numbers for one quantity is a contradiction a reader cannot resolve, and
# the weaker of the two is the one to drop. The panel keeps the drug-vs-drug constructed
# arm as the granularity comparator and the natural tumour as the finding.
ARMS = [("constructed_drug", "CONSTRUCTED\ndrug vs drug", FOCAL),
        ("natural", "NATURAL TUMOUR\ndrug vs drug", PURPLE)]


def draw_gate2(ax):
    if not os.path.exists(SRC):
        raise FileNotFoundError(
            f"{SRC} missing. Run analysis/natural/gate2_drug_response.py.")
    d = json.load(open(SRC))

    x = np.arange(len(ARMS))
    w = 0.34
    unsup = [d[a]["best_unsup"] for a, _, _ in ARMS]
    ceil = [d[a]["ceiling_matched"] for a, _, _ in ARMS]

    ax.bar(x - w / 2, unsup, w, color="white", edgecolor=[c for _, _, c in ARMS],
           linewidth=1.3, hatch="///", zorder=3)
    ax.bar(x + w / 2, ceil, w, color=[c for _, _, c in ARMS], alpha=0.88, zorder=3)

    # 2026-07-26: the hatched/solid encoding used to be named by two rotated labels written INSIDE
    # the leftmost pair of bars. That worked while the axes were 2.4 in tall; at the figure's print
    # size the pooled arm's bars are 0.25 in tall and a two-line rotated label is 0.47 in, so both
    # labels stuck out of the bars they were labelling and across the neighbouring group. A
    # two-entry single-row legend in the empty band above the short pooled bars costs the same
    # space and cannot detach from what it names, because the encoding is constant across arms.
    from matplotlib.patches import Patch
    keys = [Patch(facecolor="white", edgecolor=INK, hatch="///", lw=0.9, label="best unsupervised"),
            Patch(facecolor=INK, alpha=0.88, label="supervised ceiling")]
    # one column, hard left: that is the only band of this panel that no bar, no value label and no
    # gap interval reaches, now that the two wide intervals are set on two lines
    ax.legend(handles=keys, loc="upper left", bbox_to_anchor=(0.0, 0.73), ncol=1, fontsize=5.6,
              frameon=False, handlelength=1.1, handletextpad=0.45, labelspacing=0.35,
              borderaxespad=0.0)

    for xi, ((u, c), (arm, _, _)) in enumerate(zip(zip(unsup, ceil), ARMS)):
        ax.text(xi - w / 2, u + 0.008, f"{u:.3f}", ha="center", fontsize=5.8, color=INK)
        ax.text(xi + w / 2, c + 0.008, f"{c:.3f}", ha="center", fontsize=5.8,
                fontweight="bold", color=INK)
        # The GAP is the finding, and it is the median of the PAIRED per-split differences, not
        # the difference of the two marginal medians drawn as bars. Those are not the same number
        # (a median is not linear), and quoting the larger of the two would overstate the result:
        # for the natural arm the difference of medians is +0.147 while the paired median is
        # +0.117. The paired statistic is the correct one and is what the text reports.
        gap = d[arm]["gap_matched"]
        # Drawn as a vertical double arrow at the group centre with thin leaders to the two bar
        # tops. The previous bar-top-to-bar-top diagonal ran straight through the printed values.
        gcol = COMP if gap > 0.05 else GREY
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
            # interval on its own line under the gap. Set on one line these two labels are 0.97 in
            # wide and the two arms they belong to are 1.15 in apart at print size, so the
            # constructed interval ran into the tumour one. Stacking is also the honest layout:
            # every arm that HAS a cluster-bootstrap interval prints it, at the same size.
            lab += f"\n[{lo:+.3f}, {hi:+.3f}]"
        # placed ABOVE the taller bar, not between the two bar tops: in the pooled arm the two
        # bars differ by 0.013 and a label hung between them collided with both value labels.
        # one size for all three arms (5.8 pt): the two constructed gaps used to be set 0.4 pt
        # smaller to de-emphasise them, which at print size put the smallest type in the figure on
        # a number the caption quotes. Weight and colour still carry the emphasis.
        ax.text(xi, max(u, c) + 0.050, lab, ha="center", va="bottom", fontsize=5.8,
                linespacing=1.25,
                fontweight="bold" if gap > 0.05 else "normal",
                color=COMP if gap > 0.05 else GREY, zorder=7)

    ax.axhline(0.5, ls="--", lw=0.8, color=GREY, zorder=1)
    ax.set_xlim(-0.62, len(ARMS) - 0.38)
    # keyed at the RIGHT end of the rule: at print size the left margin of this panel is 0.22 in
    # and the word is 0.24 in, so on the left it lapped onto the first hatched bar
    ax.text(len(ARMS) - 0.40, 0.506, "chance", ha="right", va="bottom", fontsize=5.8, color=GREY)

    # The panel's claim used to live in an orange callout box pinned over the natural-tumour bars,
    # where it collided with them. It is a claim, not data, so it belongs in the panel title; the
    # space it occupied is given back to the bars. What replaces it here is the robustness block,
    # because the Results text sends the reader to this panel for exactly these two numbers
    # ("values in Fig. 5d"). Both are read from the cluster-bootstrap file, never typed in.
    if UNC and "fixed_pair_contrast" in UNC and "natural_WITHOUT_PW030" in UNC:
        fp = UNC["fixed_pair_contrast"]
        wo = UNC["natural_WITHOUT_PW030"]
        lo, hi = wo["ci95"]
        n_wo = UNC["natural_only_PW030"]["n_splits"]
        n_all = UNC["natural"]["n_splits"]
        # 2026-07-26: same two facts, re-set to the panel's real width. The two lines used to be
        # 58 and 55 characters of prefix before their numbers, which is 3.9 in of text in a 2.55 in
        # panel now that the figure is authored at print size. The prefixes are cut to what
        # identifies the check; the caption gives each in full. The numbers themselves are
        # untouched and still read from the cluster-bootstrap file, never typed in.
        ax.text(-0.60, 1.415, "the tumour gap survives every check", fontsize=5.8,
                fontweight="bold", color=INK, ha="left", va="top")
        ax.text(-0.60, 1.330,
                f"every fixed probe-clusterer pair:   "
                f"{fp['natural']:+.3f}  vs  {fp['constructed_drug']:+.3f} constructed\n"
                f"drop the {n_wo}/{n_all}-split patient:   "
                f"{wo['gap_matched']:+.3f}  [{lo:+.3f}, {hi:+.3f}]",
                fontsize=5.8, color=INK, ha="left", va="top", linespacing=1.5)

    ax.set_xticks(x)
    ax.set_xticklabels([l for _, l, _ in ARMS], fontsize=5.8)
    # two lines: rotated, the one-line label is 1.6 in of text against a 1.18 in axes
    ax.set_ylabel("accuracy recovering\nthe true partition", fontsize=6.2)
    ax.set_ylim(0.45, 1.44)
    ax.set_yticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    ax.tick_params(axis="y", labelsize=6)
    # the y range runs past 1.0 to hold the robustness block and the key, but accuracy only goes to
    # 1.0; the spine is bounded so it does not advertise an axis that carries no data
    ax.spines["left"].set_bounds(0.45, 1.0)
    for s in ("right", "top"):
        ax.spines[s].set_visible(False)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(4.2, 3.0))
    draw_gate2(ax)
    # Standalone label only. The composite title is fig5_assemble.TITLES["d"], "Gate 2 in a
    # tumour: an algorithmic limit", which is the claim the manuscript makes and which overwrites
    # this one; the two must never say opposite things. This wording describes the panel's design
    # (the same question in a constructed setting and a natural one) rather than restating that
    # claim, because standalone the panel is a diagnostic and the claim is scoped to one of its
    # three arms.
    ax.set_title("Recoverability, asked the same question twice", loc="left", fontsize=8)
    fig.savefig(os.path.join(os.path.dirname(__file__), "6gate2.png"), dpi=200,
                bbox_inches="tight")
    print("wrote 6gate2.png")
