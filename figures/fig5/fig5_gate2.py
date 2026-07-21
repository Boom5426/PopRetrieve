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
GREEN = "#55966B"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = f"{REPO}/results/zhao_gbm/gate2_drug_response.json"
UNC_SRC = f"{REPO}/results/zhao_gbm/gate2_uncertainty.json"
# Patient-level cluster-bootstrap intervals. Absent -> the panel still renders, without them, and
# says so; it does NOT invent an interval.
UNC = json.load(open(UNC_SRC)) if os.path.exists(UNC_SRC) else None

ARMS = [("constructed_class", "CONSTRUCTED\ndrug CLASS pooled\n(what we reported)", GREY),
        ("constructed_drug", "CONSTRUCTED\none drug vs one drug\n(like for like)", FOCAL),
        ("natural", "NATURAL TUMOUR\none drug vs one drug\n(within compartment)", GREEN)]


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
           linewidth=1.3, hatch="///", zorder=3, label="best unsupervised")
    ax.bar(x + w / 2, ceil, w, color=[c for _, _, c in ARMS], alpha=0.88, zorder=3,
           label="supervised ceiling")

    for xi, ((u, c), (arm, _, _)) in enumerate(zip(zip(unsup, ceil), ARMS)):
        ax.text(xi - w / 2, u + 0.008, f"{u:.3f}", ha="center", fontsize=5.2, color=INK)
        ax.text(xi + w / 2, c + 0.008, f"{c:.3f}", ha="center", fontsize=5.2,
                fontweight="bold", color=INK)
        # The GAP is the finding, and it is the median of the PAIRED per-split differences, not
        # the difference of the two marginal medians drawn as bars. Those are not the same number
        # (a median is not linear), and quoting the larger of the two would overstate the result:
        # for the natural arm the difference of medians is +0.147 while the paired median is
        # +0.117. The paired statistic is the correct one and is what the text reports.
        gap = d[arm]["gap_matched"]
        ax.annotate("", xy=(xi + w / 2, c), xytext=(xi - w / 2, u),
                    arrowprops=dict(arrowstyle="<->", lw=0.9,
                                    color=COMP if gap > 0.05 else GREY), zorder=6)
        # The gap carries a 95% interval from a PATIENT-level cluster bootstrap. It is printed
        # rather than drawn as a whisker because the bars are marginal medians while the gap is a
        # median paired difference, so an interval hung off the bar tops would imply an arithmetic
        # relationship that does not hold.
        lab = f"{gap:+.3f}"
        if UNC and arm in UNC and not np.isnan(UNC[arm]["ci95"][0]):
            lo, hi = UNC[arm]["ci95"]
            lab += f"\n[{lo:+.3f}, {hi:+.3f}]"
        ax.text(xi, (c + u) / 2 + 0.012, lab, ha="center", va="bottom",
                fontsize=5.4 if gap > 0.05 else 5.0,
                fontweight="bold" if gap > 0.05 else "normal",
                color=COMP if gap > 0.05 else GREY, zorder=7,
                bbox=dict(fc="white", ec="none", alpha=0.9, pad=0.6))

    ax.axhline(0.5, ls="--", lw=0.8, color=GREY, zorder=1)
    ax.text(len(ARMS) - 0.55, 0.507, "chance", ha="right", va="bottom", fontsize=5.0, color=GREY)

    ax.text(2, 0.60, "the information IS there,\nclustering cannot reach it:\n"
                     "an ALGORITHMIC limit,\nnot an informational one",
            ha="center", va="center", fontsize=5.4, color=COMP, fontweight="bold", zorder=8,
            bbox=dict(fc="white", ec=COMP, lw=0.5, alpha=0.94, pad=1.6))

    ax.set_xticks(x)
    ax.set_xticklabels([l for _, l, _ in ARMS], fontsize=5.4)
    ax.set_ylabel("accuracy recovering the true partition", fontsize=6)
    ax.set_ylim(0.45, 1.02)
    ax.tick_params(axis="y", labelsize=5.6)
    for s in ("right", "top"):
        ax.spines[s].set_visible(False)
    ax.legend(fontsize=5.0, loc="upper left", frameon=False, handlelength=1.3,
              labelspacing=0.25)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(4.2, 3.0))
    draw_gate2(ax)
    ax.set_title("Gate 2, asked the same question twice", loc="left", fontsize=8)
    fig.savefig(os.path.join(os.path.dirname(__file__), "6gate2.png"), dpi=200,
                bbox_inches="tight")
    print("wrote 6gate2.png")
