#!/usr/bin/env python
"""Headline figures for the controlled heterogeneous-source experiment.

Reads results/subflow/controlled_mixture_{K562,A549,MCF7}.csv and produces:
  fig_headline_bar.png   : avg hit@1 per scorer, grouped by cell line
  fig_alpha_crossover.png: hit@1 vs mixture ratio alpha, per scorer (3 cell lines)
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results/subflow"
FIG = RES / "figures"; FIG.mkdir(parents=True, exist_ok=True)

LINES = ["K562", "A549", "MCF7"]
SCORERS = ["mean_cosine", "global_energy", "coverage_mean", "coverage_worst"]
LABELS = {"mean_cosine": "mean-cosine\n(incumbent)", "global_energy": "global energy\n(K=1)",
          "coverage_mean": "coverage (mean)", "coverage_worst": "coverage (worst)"}
COLORS = {"mean_cosine": "#c0392b", "global_energy": "#2980b9",
          "coverage_mean": "#27ae60", "coverage_worst": "#f39c12"}

dfs = {}
for cl in LINES:
    p = RES / f"controlled_mixture_{cl}.csv"
    if cl == "K562" and not p.exists():
        p = RES / "controlled_mixture.csv"   # first K562 run wrote this name
    dfs[cl] = pd.read_csv(p)

# ---- Figure 1: grouped bar of avg hit@1 ----
fig, ax = plt.subplots(figsize=(8, 4.5))
x = np.arange(len(LINES)); w = 0.2
for i, sc in enumerate(SCORERS):
    vals = [dfs[cl][f"{sc}_hit@1"].mean() for cl in LINES]
    ax.bar(x + (i - 1.5) * w, vals, w, label=LABELS[sc], color=COLORS[sc])
ax.set_xticks(x); ax.set_xticklabels(LINES)
ax.set_ylabel("Hit@1 of correct 'covers-both' drug")
ax.set_title("Heterogeneous-source drug ranking: mean-matching fails, distribution-aware fixes it")
ax.axhline(1 / 43, ls="--", c="gray", lw=1, label="random (~1/43)")
ax.legend(fontsize=8, ncol=2); ax.set_ylim(0, 1.05)
fig.tight_layout(); fig.savefig(FIG / "fig_headline_bar.png", dpi=150); plt.close(fig)

# ---- Figure 2: alpha crossover (3 panels) ----
fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharey=True)
for ax, cl in zip(axes, LINES):
    d = dfs[cl]
    for sc in SCORERS:
        ax.plot(d["alpha"], d[f"{sc}_hit@1"], "o-", color=COLORS[sc], label=LABELS[sc].replace("\n", " "))
    ax.set_title(cl); ax.set_xlabel("majority fraction α (source heterogeneity: 0.5=most)")
    ax.axhline(1 / 43, ls="--", c="gray", lw=1)
    ax.invert_xaxis()  # more heterogeneous (0.5) on the right -> left = more homogeneous
axes[0].set_ylabel("Hit@1 of 'covers-both'")
axes[0].legend(fontsize=7)
fig.suptitle("Advantage of distribution-aware ranking grows with source heterogeneity", y=1.02)
fig.tight_layout(); fig.savefig(FIG / "fig_alpha_crossover.png", dpi=150, bbox_inches="tight"); plt.close(fig)

print("wrote:")
for f in sorted(FIG.glob("*.png")):
    print(" ", f, f"({f.stat().st_size//1024} KB)")
# also print a compact summary table
print("\navg hit@1 (over alpha):")
print(f"{'cell_line':10s} " + " ".join(f"{s:>14s}" for s in SCORERS))
for cl in LINES:
    print(f"{cl:10s} " + " ".join(f"{dfs[cl][f'{s}_hit@1'].mean():14.2f}" for s in SCORERS))
