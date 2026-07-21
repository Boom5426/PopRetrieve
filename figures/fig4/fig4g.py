"""DART Figure 4 panel 4g: the real-data coverage advantage, task by task.
Source data: results/exp13_real_data_projection/projection.csv
Run standalone: python fig4g.py

Rewritten 2026-07-13. This panel has now been wrong twice, in opposite directions, and both
times because it printed a COUNT that nobody could check.

  v1: titled "37 real tasks all mean-sufficient", axis label hard-coded "(0 / 37
      DART-dominant)". 37 is the task count of exp13's QUICK *sanity* configuration; the
      FULL configuration builds 239, and a sanity run had been quoted as the real-data
      result.

  v2 (mine): "11 of 215 are distributionally dominant". Wrong denominator (the like-for-like
      figure is 11 of 239), and worse, it presented a count of threshold crossings as a
      finding. The 0.01 threshold sits at 0.77 sd of the nonzero-difference distribution,
      i.e. INSIDE its noise band, and the seed in exp13 is not a replicate (it re-draws
      which drugs are tested and re-clusters the minority subpopulation). Under resampling,
      only 2 of the 10 threshold-crossing cross-line tasks survive, while drugs that do NOT
      cross the threshold in the recorded run cross it in 2-4 of 10 resamples.

So the panel now plots the DISTRIBUTION, states the mean, and circles only the two tasks
that survive seed resampling. A count of threshold crossings on this data is a count of noise
excursions, and this figure no longer reports one. See CORRECTIONS.md R13.
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

FOCAL, COMP, GREY, INK = "#5185C0", "#E99D4E", "#7A7A7A", "#1A1A1A"
DIVMAP = LinearSegmentedColormap.from_list("dart_div", [COMP, "#f7f7f7", FOCAL])
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PROJ = f"{REPO}/results/exp13_real_data_projection/projection.csv"

# The only two tasks that remain dominant in >= 8 of 10 seeds when the drug is held fixed
# and the seed is resampled. Both are HDAC inhibitors. n=2 is a hypothesis, not a result.
REPLICATION_STABLE = {
    "A549->MCF7:Abexinostat (PCI-24781)",
    "A549->MCF7:Belinostat (PXD101)",
}

DS_ORDER = ["sciplex3_within_line", "sciplex3_cross_line", "cd34", "frangieh",
            "sciplex3_predicted_mean"]
DS_LAB = {"sciplex3_within_line": "SP3 within", "sciplex3_cross_line": "SP3 cross",
          "cd34": "CD34+", "frangieh": "Frangieh", "sciplex3_predicted_mean": "SP3 pred-mean"}


def draw_4g(ax):
    p = pd.read_csv(PROJ)
    p["delta"] = p.observed_dart_minority_cov - p.observed_mean_minority_cov

    if len(p) < 100:
        raise ValueError(
            f"{PROJ} has only {len(p)} tasks: that is the QUICK sanity configuration, and the "
            f"FULL run builds 239. Re-run exp13 without QUICK=1. This panel will not present a "
            f"sanity run as the real-data result.")

    present = [d for d in DS_ORDER if (p.dataset == d).any()]
    width = max(int((p.dataset == d).sum()) for d in present)
    M = np.full((len(present), width), np.nan)
    stable = []
    for i, ds in enumerate(present):
        sub = p[p.dataset == ds].reset_index(drop=True)
        for j, r in sub.iterrows():
            M[i, j] = r["delta"]
            base = ":".join(str(r["task_id"]).split(":")[:2])   # drop the :sN suffix
            if base in REPLICATION_STABLE:
                stable.append((j, i))

    vmax = float(np.nanmax(np.abs(M)))
    im = ax.imshow(M, cmap=DIVMAP, vmin=-vmax, vmax=vmax, aspect="auto")

    if stable:
        xs, ys = zip(*stable)
        ax.scatter(xs, ys, s=16, facecolors="none", edgecolors=INK, linewidths=0.9, zorder=3)

    ax.set_yticks(range(len(present)))
    ax.set_yticklabels([DS_LAB.get(d, d) for d in present], fontsize=6)
    ax.set_xlabel(
        f"task index within dataset\n"
        f"mean gain {p.delta.mean():+.4f} over {len(p)} tasks; "
        f"circled = survives seed resampling (2)", fontsize=5.4)
    cb = ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cb.set_label("DART $-$ mean\nminority cov", fontsize=5.5)
    cb.ax.tick_params(labelsize=5)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.8, 3.0))
    draw_4g(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "4g.png"), dpi=200, bbox_inches="tight")
    print("wrote 4g.png")
