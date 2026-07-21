"""Figure 7: the two gates on NATURAL heterogeneity, and what our constructed benchmark got wrong.

Source data: results/zhao_gbm/{gate1_natural,gate2_natural,premise_mean_vs_compartment}.csv

THE POINT OF THIS FIGURE IS THAT IT CORRECTS US.

Every positive real-data result in this study lives in cell-line mixtures we constructed. This
figure tests the same two gates on ZhaoSims2021: acute-slice culture and biopsy from 10
glioblastoma patients, where malignant glioma cells, tumour-associated myeloid cells and
oligodendrocytes co-exist inside one patient's tumour. Nobody mixed anything.

The constructed benchmark turns out to distort the biology in BOTH directions at once, and both
distortions happen to flatter the paper's premise:

  a  GATE 2. We concluded from the constructed mixture (supervised ceiling 0.692, best
     unsupervised 0.674) that subpopulation identifiability is an INFORMATION limit. In a real
     tumour the ceiling is 0.964 and off-the-shelf clustering reaches 0.949. The information
     limit was a property of our benchmark, not of biology. That claim is withdrawn.

  b  GATE 1. The constructed mixtures put the induced response cosine at 0.014-0.044, i.e. the
     two subpopulations respond near-orthogonally. In a real tumour the median is 0.566: malignant
     cells and tumour-associated macrophages share most of their response direction. Mixing A549
     with K562 OVERSTATES the divergence a distributional score can exploit by roughly an order
     of magnitude.

  c  THE PREMISE (Fig. 1a): two drugs share a mean signature and do opposite things to a
     subpopulation. Tested on a real tumour, mean-signature similarity predicts
     malignant-compartment response similarity at rho = +0.878. The mean is largely sufficient.
     The residual is real and small, which is what every other independent criterion in this study
     also finds.

Both gates are OPEN on natural data and the distributional advantage still does not appear. The
two-gate criterion is therefore NECESSARY BUT NOT SUFFICIENT, and this figure is how we found out.

Run standalone: python fig7_natural.py
"""
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

FOCAL, COMP, GREY, INK = "#5185C0", "#E99D4E", "#7A7A7A", "#1A1A1A"
GREEN = "#55966B"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = f"{REPO}/results/zhao_gbm"

# the constructed-mixture values this figure is correcting (results/upgrade/gate2_*, exp09)
CONSTRUCTED = {"ceiling": 0.692, "unsup": 0.674, "cos_lo": 0.014, "cos_hi": 0.044}


def draw_a(ax):
    """Gate 2: constructed vs natural. The bar that matters is the ceiling."""
    g2 = pd.read_csv(f"{SRC}/gate2_natural.csv")
    nat_ceiling = float(g2.probe_acc.median())
    nat_unsup = max(float(g2[c].median()) for c in
                    ["acc_kmeans_k2", "acc_gmm_k2", "acc_leiden", "acc_hdbscan"])

    xs = np.arange(2)
    w = 0.36
    ax.bar(xs - w / 2, [CONSTRUCTED["unsup"], nat_unsup], w, color=FOCAL, alpha=0.85,
           label="best unsupervised", zorder=3)
    ax.bar(xs + w / 2, [CONSTRUCTED["ceiling"], nat_ceiling], w, color=GREEN, alpha=0.85,
           label="supervised ceiling", zorder=3)
    for x, (u, c) in zip(xs, [(CONSTRUCTED["unsup"], CONSTRUCTED["ceiling"]),
                              (nat_unsup, nat_ceiling)]):
        ax.text(x - w / 2, u + 0.008, f"{u:.3f}", ha="center", fontsize=5.6, fontweight="bold")
        ax.text(x + w / 2, c + 0.008, f"{c:.3f}", ha="center", fontsize=5.6, fontweight="bold")

    ax.axhline(0.5, ls="--", lw=0.8, color=GREY, zorder=1)
    ax.text(1.48, 0.505, "chance", ha="right", va="bottom", fontsize=5.0, color=GREY)
    ax.annotate("", xy=(1 - w / 2 - 0.10, nat_unsup - 0.01),
                xytext=(0 + w / 2 + 0.10, CONSTRUCTED["ceiling"] + 0.01),
                arrowprops=dict(arrowstyle="-|>", lw=1.1, color=COMP,
                                connectionstyle="arc3,rad=-0.30"), zorder=5)
    ax.text(0.5, 0.795, "the 'information limit'\nwas OUR BENCHMARK,\nnot biology",
            ha="center", va="center", fontsize=5.6, color=COMP, fontweight="bold", zorder=6,
            bbox=dict(fc="white", ec="none", alpha=0.92, pad=1.2))

    ax.set_xticks(xs)
    ax.set_xticklabels(["CONSTRUCTED\ncell-line mixture\n(HDAC vs JAK)",
                        "NATURAL\npatient tumour\n(malignant vs myeloid)"], fontsize=5.6)
    ax.set_ylabel("accuracy recovering the true partition", fontsize=6)
    ax.set_ylim(0.45, 1.03)
    ax.tick_params(axis="y", labelsize=5.6)
    for s in ("right", "top"):
        ax.spines[s].set_visible(False)
    ax.legend(fontsize=5.0, loc="lower left", frameon=False, handlelength=1.3)


def draw_b(ax):
    """Gate 1: the constructed mixture exaggerates divergence by an order of magnitude."""
    g1 = pd.read_csv(f"{SRC}/gate1_natural.csv")
    v = g1.induced_response_cosine.dropna().values

    ax.axhspan(CONSTRUCTED["cos_lo"], CONSTRUCTED["cos_hi"], color=FOCAL, alpha=0.20, zorder=1)
    ax.text(0.42, 0.075, "constructed mixtures\n0.014 - 0.044 (near-orthogonal)", fontsize=5.2,
            color=FOCAL, va="bottom", ha="left")

    rng = np.random.default_rng(0)
    ax.scatter(rng.normal(1.0, 0.045, len(v)), v, s=16, color=COMP, alpha=0.75, lw=0, zorder=3)
    ax.plot([0.82, 1.18], [np.median(v)] * 2, color=COMP, lw=2.2, zorder=4)
    ax.text(1.24, np.median(v), f"median\n{np.median(v):.3f}", va="center", fontsize=5.8,
            color=COMP, fontweight="bold")

    ax.axhline(1.0, ls="-", lw=1.0, color=INK, alpha=0.5, zorder=1)
    ax.text(1.42, 0.985, "additive-predictor limit (cos = 1):\nno divergence at all",
            ha="right", va="top", fontsize=5.0, color=INK, style="italic")

    ax.set_xlim(0.3, 1.45)
    ax.set_ylim(-0.05, 1.08)
    ax.set_xticks([])
    ax.set_ylabel(r"induced response cosine  $\cos(d_{\rm malignant}, d_{\rm myeloid})$",
                  fontsize=6)
    ax.tick_params(axis="y", labelsize=5.6)
    for s in ("right", "top", "bottom"):
        ax.spines[s].set_visible(False)
    # The sampling footnote ("one point per patient-drug pair (n = ...), 10 GBM patients") was
    # 4.8 pt, below Nature's 5 pt floor. It is an n, so it is load-bearing and was not dropped:
    # the Fig. 6 caption states both the pair count and the ten glioblastoma patients. If the
    # source CSV ever changes, len(v) is no longer printed anywhere, so the caption's pair count
    # becomes the only record of n and must be re-checked against gate1_natural.csv.


def draw_c(ax):
    """The premise: does the mean already know what the compartments do?"""
    p = pd.read_csv(f"{SRC}/premise_mean_vs_compartment.csv")
    x, y = p.cos_mean_signature.values, p.cos_malignant_response.values
    r = stats.spearmanr(x, y)

    lo, hi = -0.2, 0.95
    ax.plot([lo, hi], [lo, hi], ls="--", lw=0.8, color=INK, zorder=2)
    ax.scatter(x, y, s=18, color=FOCAL, alpha=0.8, lw=0, zorder=3)
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("cos(mean signature of drug A, drug B)", fontsize=6)
    ax.set_ylabel("cos(MALIGNANT-compartment\nresponse of A, B)", fontsize=6)
    ax.tick_params(labelsize=5.6)
    for s in ("right", "top"):
        ax.spines[s].set_visible(False)

    # NO p-VALUE IS PRINTED, DELIBERATELY. 15 of these 18 pairs come from one patient (PW030, the
    # only one given more than two compounds) and they reuse the same six drugs, so a p-value that
    # treats 18 pairs as independent observations is anticonservative by a wide margin. Reporting
    # 1.6e-06 here would be the pseudo-replication this paper devotes a section to criticising.
    # The correlation is the measurement; the dependency structure is stated in the caption.
    n_top = int((p.patient == p.patient.mode()[0]).sum()) if "patient" in p else 0
    ax.text(0.04, 0.96, f"Spearman $\\rho$ = {r.statistic:+.3f}\n"
                        f"n = {len(p)} drug pairs\n{n_top} of them from ONE patient",
            transform=ax.transAxes, ha="left", va="top", fontsize=5.8, fontweight="bold",
            color=INK)
    ax.text(0.96, 0.06,
            "Points near the diagonal mean the MEAN\nalready ranks what the compartment does.\n"
            "In a real tumour, most of them are.",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=5.0, color=GREY,
            style="italic")


def build(apply_style=None, panel_letter=None):
    if apply_style:
        apply_style(sizes=(8, 7, 6))
    fig, axes = plt.subplots(1, 3, figsize=(10.6, 3.1))
    draw_a(axes[0])
    draw_b(axes[1])
    draw_c(axes[2])
    titles = ["Gate 2 opens on natural data", "Gate 1: we overstated divergence",
              "The mean already knows most of it"]
    for ax, t, k in zip(axes, titles, "abc"):
        ax.set_title(t, loc="left", fontsize=8)
        if panel_letter:
            panel_letter(ax, k, case="lower")
        else:
            ax.text(-0.18, 1.10, k, transform=ax.transAxes, fontsize=10, fontweight="bold")
    fig.subplots_adjust(wspace=0.46, bottom=0.22)
    out = os.path.dirname(os.path.abspath(__file__))
    fig.savefig(os.path.join(out, "fig7_natural.png"), dpi=300, bbox_inches="tight")
    fig.savefig(os.path.join(out, "fig7_natural.pdf"), bbox_inches="tight")
    print("wrote fig7_natural.png / .pdf")


if __name__ == "__main__":
    build()
