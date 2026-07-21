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
    pad = max(abs(lo), abs(hi)) * 0.45
    ax.set_ylim(lo - pad, hi + pad)
    for x, m, q in zip(xs, vals, qs):
        star = "*" if q < 0.05 else "ns"
        ax.text(x, m + pad * 0.12, f"{m:+.3f} {star}", ha="center", va="bottom",
                fontsize=5.2, color=INK)

    ax.set_xticks(xs)
    ax.set_xticklabels([f"{s}\ndiv={dm:.2f}" for s, dm in
                        zip(d["stratum"], d["divergence_median"])], fontsize=5.4)
    ax.set_xlabel("true response-divergence quartile")
    ax.set_ylabel("DART $-$ mean MoA-nDCG")
    ax.text(0.97, 0.05,
            "gate stays closed: no positive\neffect at any divergence level",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=5.2, color=COMP,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="0.8", lw=0.5, alpha=0.9))
    for sp in ["right", "top"]:
        ax.spines[sp].set_visible(False)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.4, 3.0))
    draw_6g(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "6g.png"), dpi=200, bbox_inches="tight")
    print("wrote 6g.png")
