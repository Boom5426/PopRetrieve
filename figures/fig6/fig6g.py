"""DART Figure 6 panel 6g: conditional advantage by response-divergence stratum.
Source data: results/exp17_true_divergence_subset/divergence_stratified.csv
Run standalone: python fig6g.py

Rewritten 2026-07-12 for two reasons.

1. It re-derived its own tertile means from upgrade/conditional_advantage_per_query.csv.
   exp17 already computes exactly this quantity, stratified by TRUE response divergence and
   Benjamini-Hochberg corrected, and it is the source the verdict document quotes. Reading
   exp17 directly means this panel cannot drift away from the verdict.

2. It printed "trend rho=+0.08 (p=0.046) / identifiability rho=-0.01 (p=0.90)" as a literal
   string that would not update if the data changed, and those numbers predate the sentinel
   fix: 165 of 765 MoA-nDCG values are UNDEFINED (the leave-MoA-out and partial-library
   splits remove the mechanism class from the library) and were carrying a -1 that was
   differenced as if it were a measurement, so (-1)-(-1)=0 pinned every stratum's median at
   exactly 0.000. Significance is now read from the file, per stratum.

The corrected picture is stronger than the one it replaces: the gain is not merely "near
zero", it is significantly NEGATIVE in the lowest-divergence stratum and indistinguishable
from zero everywhere else.
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

FOCAL, COMP, GREY, INK = "#5185C0", "#E99D4E", "#7A7A7A", "#1A1A1A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
STRAT = f"{REPO}/results/exp17_true_divergence_subset/divergence_stratified.csv"


def draw_6g(ax):
    d = pd.read_csv(STRAT)
    d = d[(d.metric == "moa_ndcg") & (d.stratum.isin(["Q1", "Q2", "Q3", "Q4"]))] \
        .sort_values("stratum")
    if d.empty:
        raise KeyError(f"no moa_ndcg quartile rows in {STRAT}; re-run exp17.")

    xs = np.arange(len(d))
    vals = d["mean_gap"].values
    errs = (d["sd_gap"] / np.sqrt(d["n"])).values          # standard error, not the raw sd
    qs = d["bh_qvalue"].values
    cols = [COMP if v < 0 else GREY for v in vals]

    ax.axhline(0, ls="-", lw=1.2, color="k", zorder=2)
    ax.bar(xs, vals, yerr=errs, width=0.60, color=cols, alpha=0.8,
           error_kw=dict(lw=1.0, capsize=3), zorder=3)

    lo = float((vals - errs).min())
    hi = float((vals + errs).max())
    pad = max(abs(lo), abs(hi)) * 0.55
    ax.set_ylim(lo - pad, hi + pad * 1.15)
    # Value labels go on the far side of each bar from zero (below a negative bar, above a
    # positive one) so no label is ever printed on top of the bar it belongs to.
    for x, m, e, q in zip(xs, vals, errs, qs):
        star = "*" if q < 0.05 else "ns"
        if m < 0:
            ax.text(x, m - e - pad * 0.12, f"{m:+.3f} {star}".replace("-", "\u2212"), ha="center", va="top",
                    fontsize=5.6, color=INK)
        else:
            ax.text(x, m + e + pad * 0.12, f"{m:+.3f} {star}".replace("-", "\u2212"), ha="center", va="bottom",
                    fontsize=5.6, color=INK)

    ax.set_xticks(xs)
    ax.set_xticklabels([f"{s}\ndiv {dm:.2f}" for s, dm in
                        zip(d["stratum"], d["divergence_median"])], fontsize=5.6)
    # labelpad 1.5, not the default: row 2 reserves 0.38 in under its axes and the two-line
    # x tick labels ("Q1 / div 0.02") already spend most of it, so at the default pad this
    # label hung 0.03 in BELOW the canvas. bbox_inches="tight" would then have expanded the
    # exported media box past the authored 6.90 in and reintroduced a LaTeX rescale.
    ax.set_xlabel("true response-divergence quartile (median divergence)", labelpad=1.5)
    ax.set_ylabel("MoA-nDCG gain,\ndistributional $-$ mean")
    # Direct label on the null line: what "zero" means here, and what the stars mean.
    ax.set_xlim(-0.62, len(xs) - 0.38)
    ax.text(-0.57, pad * 0.10, "no difference", ha="left", va="bottom",
            fontsize=5.5, color=GREY)
    ax.text(0.015, 0.02, "* $q<0.05$ (Benjamini$-$Hochberg);  ns, not significant",
            transform=ax.transAxes, ha="left", va="bottom", fontsize=5.4, color=GREY)
    for sp in ["right", "top"]:
        ax.spines[sp].set_visible(False)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.4, 3.0))
    draw_6g(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "6g.png"), dpi=200, bbox_inches="tight")
    print("wrote 6g.png")
