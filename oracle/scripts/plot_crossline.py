#!/usr/bin/env python
"""Cross-line crossover figure: the 'population-in, mean-out' failure on a real
two-cell-type mixture, replicated across line pairs. mean-cosine decays as the
majority cell type dominates (alpha->0.9); distributional scores stay high."""
from __future__ import annotations
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results/subflow"; FIG = RES / "figures"; FIG.mkdir(parents=True, exist_ok=True)
SC = ["mean_cosine", "global_energy", "coverage_mean", "coverage_worst"]
LAB = {"mean_cosine": "mean-cosine (incumbent)", "global_energy": "global energy",
       "coverage_mean": "coverage (mean)", "coverage_worst": "coverage (worst)"}
COL = {"mean_cosine": "#c0392b", "global_energy": "#2980b9",
       "coverage_mean": "#27ae60", "coverage_worst": "#f39c12"}

# (csv, divergence csv, title) per line pair
PAIRS = [
    ("crossline_mixture.csv", "crossline_divergence.csv", "K562(maj) + A549(min)"),
    ("crossline_mixture_A549_MCF7.csv", "crossline_divergence_A549_MCF7.csv", "A549(maj) + MCF7(min)"),
    ("crossline_mixture_K562_MCF7.csv", "crossline_divergence_K562_MCF7.csv", "K562(maj) + MCF7(min)"),
]
avail = [(c, d, t) for c, d, t in PAIRS if (RES / c).exists()]
fig, axes = plt.subplots(1, len(avail), figsize=(4.6 * len(avail), 4.3), squeeze=False)
axes = axes[0]

for ax, (csv, dcsv, title) in zip(axes, avail):
    df = pd.read_csv(RES / csv)
    for s in SC:
        ax.plot(df["alpha"], df[f"{s}_hit@1"], "o-", color=COL[s], label=LAB[s])
    med = ""
    if (RES / dcsv).exists():
        dv = pd.read_csv(RES / dcsv)
        rel = dv[dv.get("reliable", dv["cross_cos"] < 0.9)]
        if len(rel):
            med = f"\ncross-line response cos: median {rel['cross_cos'].median():.2f}"
    ax.set_title(title + med, fontsize=10)
    ax.set_xlabel("mixture ratio α (majority cell-type fraction)")
    ax.set_ylim(-0.03, 1.05)
    ax.axhspan(-0.03, 0.0, color="k", alpha=0)
axes[0].set_ylabel("Hit@1 of correct 'covers-both'")
axes[0].legend(fontsize=8, loc="lower left")
fig.suptitle("Cross-line 'population-in, mean-out': divergent modes are two real cell types "
             "under the SAME drug\n(mean-cosine decays as the majority cell type dominates; "
             "distributional scoring stays high)", y=1.03, fontsize=11)
fig.tight_layout()
fig.savefig(FIG / "fig_crossline_crossover.png", dpi=150, bbox_inches="tight")
print("wrote", FIG / "fig_crossline_crossover.png", f"({len(avail)} line pairs)")
