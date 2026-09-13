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

  b  GATE 1. The constructed mixtures put the induced response cosine at a median of 0.011 over
     96 mixtures, range -0.094 to +0.132, i.e. the two subpopulations respond near-orthogonally.
     In a real tumour the median is 0.566: malignant cells and tumour-associated macrophages share
     most of their response direction. Mixing A549 with K562 OVERSTATES the divergence a
     distributional score can exploit by roughly an order of magnitude. The overstatement is real
     but it is not total: the constructed range reaches +0.132 and one of the 17 patient-drug
     pairs sits at +0.081, inside it. The band drawn here is the observed range rather than a
     summary interval so that a reader can see this; it read 0.014-0.044 until 2026-09-01, which
     was the mean as a lower edge and an unsourced upper one (CORRECTIONS.md R53).

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

# Palette comes from the house-style module; do NOT re-declare the hex values here. Every
# panel file used to carry its own copy, which made figstyle's "one edit here recolours the
# whole deck" untrue: a recolour meant editing 43 files and missing one was silent.
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from color_preferences import BLUE, GREEN, GREY, NAVY, ORANGE  # noqa: E402

FOCAL_SOFT = BLUE
COMP_SOFT = ORANGE
GREEN_SOFT = GREEN
INK = NAVY
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = f"{REPO}/results/zhao_gbm"

# The constructed-mixture values this figure is correcting. COMPUTED, not typed, since
# 2026-09-01; see CORRECTIONS.md R53.
#
# These were four literals: {"ceiling": 0.692, "unsup": 0.674, "cos_lo": 0.014, "cos_hi": 0.044}.
# Three of them reproduced. The fourth did not reproduce from anything: on the 96-row real_blend
# arm the summaries are median 0.011, q75 0.038, q90 0.079, q95 0.104, max 0.132, mean 0.0143,
# and 0.044 is none of them. The closest coincidences are the 78th percentile (0.0422) and
# mean + 0.64 s.d. (0.0449), and nobody chooses either as a statistic.
#
# What made it more than a provenance problem: the band drawn from 0.014 to 0.044 is described in
# the Figure 4 caption as "the range spanned by our own constructed mixtures", and it contains
# 24 of the 96 values, 25 per cent. Its lower edge was the MEAN, so it hid the whole lower half of
# a distribution that is centred near zero and runs negative. It also concealed an overlap: the
# constructed values reach +0.132 and one of the 17 natural patient-drug pairs sits at +0.081,
# inside the constructed range, which the drawn band placed well below every natural point.
#
# The band is now the actual range, min to max, computed here, with the median drawn inside it.
UNSUP_COLS = ("acc_kmeans_k2", "acc_gmm_k2", "acc_leiden", "acc_hdbscan")


def constructed():
    """The constructed-mixture reference values, every one read from its own source file.

    ``ceiling`` and ``unsup`` are medians over seeds at the real separation scale, which is the
    same aggregation fig5e uses, so the two panels cannot disagree. ``cos_*`` summarise the
    induced response cosine between the two subpopulations of the constructed mixture.
    """
    g2 = pd.read_csv(f"{REPO}/results/upgrade/gate2_supervised_upper_bound.csv")
    g2 = g2[g2.separation_scale == 1.0]
    assert len(g2), "no rows at separation_scale == 1.0 in gate2_supervised_upper_bound.csv"

    d = pd.read_csv(f"{REPO}/results/exp09_structure_diagnostics/gate1_response_divergence.csv")
    d = d[(d.synth == "real") & (d.predictor == "real_blend")]
    v = d.induced_response_cosine.dropna()
    assert len(v), "no real/real_blend rows in gate1_response_divergence.csv"

    return {"ceiling": float(g2.probe_acc.median()),
            "unsup": max(float(g2[c].median()) for c in UNSUP_COLS),
            "cos_lo": float(v.min()), "cos_hi": float(v.max()),
            "cos_med": float(v.median()), "cos_n": int(len(v))}


CONSTRUCTED = constructed()


def draw_a(ax):
    """Gate 2: constructed vs natural. The bar that matters is the ceiling."""
    g2 = pd.read_csv(f"{SRC}/gate2_natural.csv")
    nat_ceiling = float(g2.probe_acc.median())
    nat_unsup = max(float(g2[c].median()) for c in
                    ["acc_kmeans_k2", "acc_gmm_k2", "acc_leiden", "acc_hdbscan"])

    xs = np.arange(2)
    w = 0.36
    ax.bar(xs - w / 2, [CONSTRUCTED["unsup"], nat_unsup], w, color=FOCAL_SOFT, alpha=0.85,
           label="best unsupervised", zorder=3)
    ax.bar(xs + w / 2, [CONSTRUCTED["ceiling"], nat_ceiling], w, color=GREEN_SOFT, alpha=0.85,
           label="supervised ceiling", zorder=3)
    for x, (u, c) in zip(xs, [(CONSTRUCTED["unsup"], CONSTRUCTED["ceiling"]),
                              (nat_unsup, nat_ceiling)]):
        ax.text(x - w / 2, u + 0.008, f"{u:.3f}", ha="center", fontsize=5.6, fontweight="bold")
        ax.text(x + w / 2, c + 0.008, f"{c:.3f}", ha="center", fontsize=5.6, fontweight="bold")

    ax.axhline(0.5, ls="--", lw=0.8, color=GREY, zorder=1)
    ax.text(1.48, 0.505, "chance", ha="right", va="bottom", fontsize=5.0, color=GREY)
    ax.annotate("", xy=(1 - w / 2 - 0.10, nat_unsup - 0.01),
                xytext=(0 + w / 2 + 0.10, CONSTRUCTED["ceiling"] + 0.01),
                arrowprops=dict(arrowstyle="-|>", lw=1.1, color=COMP_SOFT,
                                connectionstyle="arc3,rad=-0.30"), zorder=5)
    ax.text(0.5, 0.795, "the 'information limit'\nwas OUR BENCHMARK,\nnot biology",
            ha="center", va="center", fontsize=5.6, color=INK, fontweight="bold", zorder=6,
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

    # The band is the ACTUAL range of the constructed mixtures, min to max over all
    # CONSTRUCTED["cos_n"] of them, with their median drawn inside it. It used to be 0.014 to
    # 0.044: the mean as a lower edge and an upper edge that reproduced from nothing. See the
    # note on constructed() above and CORRECTIONS.md R53. Both endpoints are composed into the
    # label from the same dict the span is drawn from, so the label cannot outlive the band.
    ax.axhspan(CONSTRUCTED["cos_lo"], CONSTRUCTED["cos_hi"], color=FOCAL_SOFT, alpha=0.20,
               zorder=1)
    ax.plot([0.57, 1.66], [CONSTRUCTED["cos_med"]] * 2, color=FOCAL_SOFT, lw=1.0, zorder=2,
            solid_capstyle="butt")
    # The label NAMES the band and prints no number. Its endpoints, its median and its n are in
    # the caption. Two reasons, and the second is the one that matters: at three lines the block
    # ran through the scatter, because the points jitter about x = 1.0 and the panel has no clear
    # space at low y on the left; and a printed range here would be a second copy of two numbers
    # that already have to agree with the axhspan, which is exactly the drift the old hard-typed
    # "0.014 - 0.044" was. With nothing printed there is nothing to drift.
    ax.text(1.62, 0.5 * (CONSTRUCTED["cos_lo"] + CONSTRUCTED["cos_hi"]),
            "constructed\nmixtures", fontsize=5.6, color=INK, va="center", ha="right")

    rng = np.random.default_rng(0)
    ax.scatter(rng.normal(1.0, 0.045, len(v)), v, s=16, color=COMP_SOFT, alpha=0.75, lw=0, zorder=3)
    ax.plot([0.82, 1.18], [np.median(v)] * 2, color=COMP_SOFT, lw=2.2, zorder=4)
    ax.text(1.24, np.median(v), f"median\n{np.median(v):.3f}", va="center", fontsize=6.0,
            color=INK, fontweight="bold")

    ax.axhline(1.0, ls="-", lw=1.0, color=INK, alpha=0.5, zorder=1)
    ax.text(1.62, 0.985, "additive-predictor limit (cos = 1):\nno divergence at all",
            ha="right", va="top", fontsize=5.6, color=INK, style="italic")

    # n is load-bearing and was previously dropped for being below the 5 pt floor; at 5.8 pt it is
    # legal, so the panel carries its own sample size again instead of leaning on the caption.
    ax.text(0.60, 1.06, f"n = {len(v)} patient-drug pairs", fontsize=5.8, color=INK,
            fontweight="bold", ha="left", va="top")

    ax.set_xlim(0.55, 1.66)
    # Bottom at -0.14, not -0.05: the constructed range reaches -0.094 and the old limit clipped
    # it. Nothing else on this panel goes below zero.
    ax.set_ylim(-0.14, 1.10)
    ax.set_xticks([])
    ax.set_ylabel(r"induced response cosine  $\cos(d_{\rm malignant}, d_{\rm myeloid})$",
                  fontsize=6.2)
    ax.tick_params(axis="y", labelsize=6)
    for s in ("right", "top", "bottom"):
        ax.spines[s].set_visible(False)
    # The sampling footnote ("one point per patient-drug pair (n = ...), 10 GBM patients") was
    # 4.8 pt, below Nature's 5 pt floor. It is an n, so it is load-bearing and was not dropped:
    # the Fig. 5 caption states both the pair count and the ten glioblastoma patients. If the
    # source CSV ever changes, len(v) is no longer printed anywhere, so the caption's pair count
    # becomes the only record of n and must be re-checked against gate1_natural.csv.


def draw_c(ax):
    """The premise, on DISJOINT compartments: does one compartment rank what another does?

    The x quantity is the MYELOID response similarity, not the mean signature. The mean signature
    is the equal-weight average of the malignant and myeloid compartment deltas, so the malignant
    compartment it would be used to rank is half of it and correlating the two mixes biology with
    arithmetic (corrected 2026-09-06 from "contains 43% of the malignant cells", which counted a
    three-compartment cell share the signature is not built from); the myeloid and malignant compartments share
    no cells, and each is already referred to its own matched control upstream. That disjoint form
    is what the manuscript's argument rests on, and it is the only one this panel may draw: the
    caption and the Results sentence both describe the disjoint statistic. Drawing the overlapping
    one here (as this panel did until 2026-09-01) put rho = +0.878 and an x label reading
    "cos(mean signature ...)" under a caption that said myeloid-versus-malignant at +0.835.

    Both values come from the same per-pair table and neither is retyped: the overlapping form is
    quoted in the Results by its own macro, this panel computes the disjoint one from the column
    it plots. See analysis/natural/zhao_premise_disjoint.py.
    """
    p = pd.read_csv(f"{SRC}/premise_mean_vs_compartment.csv")
    # x = myeloid, NOT cos_mean_signature. See the docstring before changing this line.
    x, y = p.cos_myeloid_response.values, p.cos_malignant_response.values
    r = stats.spearmanr(x, y)

    lo, hi = -0.2, 0.95
    ax.plot([lo, hi], [lo, hi], ls="--", lw=0.8, color=INK, zorder=2)
    ax.scatter(x, y, s=18, color=FOCAL_SOFT, alpha=0.8, lw=0, zorder=3)
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("cos(myeloid-compartment response of A, B)", fontsize=6.2)
    # Sentence case: the compartment is named in the caption and caps-for-emphasis in an axis
    # label is a slide idiom.
    ax.set_ylabel("cos(malignant-compartment\nresponse of A, B)", fontsize=6.2)
    ax.tick_params(labelsize=6)
    for s in ("right", "top"):
        ax.spines[s].set_visible(False)

    # NO p-VALUE IS PRINTED, DELIBERATELY. 15 of these 18 pairs come from one patient (PW030, the
    # only one given more than two compounds) and they reuse the same six drugs, so a p-value that
    # treats 18 pairs as independent observations is anticonservative by a wide margin. Reporting
    # 1.6e-06 here would be the pseudo-replication this paper devotes a section to criticising.
    # The correlation is the measurement; the dependency structure is stated in the caption.
    n_top = int((p.patient == p.patient.mode()[0]).sum()) if "patient" in p else 0
    # n and the single-patient dependency are in the caption, where the dependency structure has
    # to be stated in any case; the panel keeps the correlation it plots.
    ax.text(0.04, 0.96, f"Spearman $\\rho$ = {r.statistic:+.3f}",
            transform=ax.transAxes, ha="left", va="top", fontsize=6.0, color=INK)
    _ = (len(p), n_top)
    # The three-line italic gloss that used to sit here ("points near the diagonal mean the MEAN
    # already ranks what the compartment does") is the panel's claim, and it now lives in the panel
    # title where it costs no plot area and cannot crowd the point cloud. Only the key to the
    # dashed line stays, because that is a legend, not an interpretation.
    # The dashed line is defined in the caption.


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
