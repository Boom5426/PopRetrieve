"""DART Figure 6 panel 6f: the separation ladder, and the positive control Gate 2 needs.

Source data: results/upgrade/gate2_supervised_upper_bound.csv

Panel 5e reports that on this CONSTRUCTED mixture the supervised ceiling (0.692) and the best
unsupervised method (0.674) are 0.018 apart, so within that benchmark the limit is informational
rather than algorithmic. (On natural patient-tumour heterogeneity the ceiling is 0.964: the
information limit was a property of the benchmark, not of biology. See main-text Fig. 5c.) That conclusion is only safe if the probe is capable of pulling away from
clustering WHEN THERE IS SOMETHING TO PULL AWAY WITH. Otherwise "no gap" could simply mean the
probe is insensitive, and the whole argument collapses.

This panel is that control. Artificially raise the separation between the two source populations
and the gap opens exactly as it should: +0.114 at 1.5x, +0.162 at 2.0x, before both saturate at
perfect recovery. The probe detects exploitable structure whenever exploitable structure exists.
Its failure to detect any on real data (leftmost point, separation = 1.0) is therefore a
measurement, not a null result.

The panel replaces an ARI phase diagram over (separation x cell budget). The cell-budget axis was
flat and is reported in Extended Data; the separation axis is the one that carries the argument,
and it now carries the ceiling with it.

Run standalone: python fig6f.py
"""
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

FOCAL, COMP, GREY, INK = "#5185C0", "#E99D4E", "#7A7A7A", "#1A1A1A"
GREEN = "#55966B"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = f"{REPO}/results/upgrade/gate2_supervised_upper_bound.csv"

UNSUP = ["acc_kmeans_k2", "acc_gmm_k2", "acc_leiden", "acc_hdbscan"]


def draw_6f(ax):
    if not os.path.exists(SRC):
        raise FileNotFoundError(
            f"{SRC} does not exist. Run analysis/identifiability/gate2_supervised_upper_bound.py.")
    d = pd.read_csv(SRC)

    g = d.groupby("separation_scale")
    seps = np.array(sorted(d.separation_scale.unique()))
    ceil = np.array([float(g.get_group(s).probe_acc.median()) for s in seps])
    best = np.array([max(float(g.get_group(s)[c].median()) for c in UNSUP) for s in seps])

    ax.fill_between(seps, best, ceil, color=COMP, alpha=0.18, zorder=1,
                    label="unreachable by clustering")
    ax.plot(seps, ceil, "-o", color=GREEN, ms=4, lw=1.5, zorder=3,
            label="supervised ceiling")
    ax.plot(seps, best, "-s", color=FOCAL, ms=4, lw=1.5, zorder=3,
            label="best unsupervised")
    ax.axhline(0.5, ls="--", lw=0.8, color=GREY, zorder=1)

    # the real-data regime: the gap is closed, and that is the finding
    ax.axvline(1.0, ls=":", lw=1.0, color=INK, zorder=2)
    ax.annotate(f"real data\ngap {ceil[0] - best[0]:+.3f}",
                xy=(1.0, (ceil[0] + best[0]) / 2), xytext=(1.75, 0.565),
                fontsize=5.6, color=INK, fontweight="bold",
                arrowprops=dict(arrowstyle="->", lw=0.8, color=INK))
    # ... and the control: raise separation and the probe DOES pull away
    i = int(np.argmax(ceil - best))
    ax.annotate(f"probe pulls away\nwhen structure exists\n(gap {ceil[i] - best[i]:+.3f})",
                xy=(seps[i], (ceil[i] + best[i]) / 2), xytext=(2.6, 0.72),
                fontsize=5.6, color=COMP, fontweight="bold",
                arrowprops=dict(arrowstyle="->", lw=0.8, color=COMP))

    ax.set_xlabel(r"source separation ($\times$ real)", fontsize=6)
    ax.set_ylabel("accuracy recovering the true partition", fontsize=6)
    ax.set_xscale("log")
    ax.set_xticks(seps)
    ax.set_xticklabels([f"{s:g}" for s in seps], fontsize=5.6)
    ax.set_ylim(0.45, 1.06)
    ax.tick_params(axis="y", labelsize=5.6)
    ax.minorticks_off()
    for sp in ("right", "top"):
        ax.spines[sp].set_visible(False)
    ax.legend(fontsize=5.5, loc="lower right", frameon=True, framealpha=0.92,
              edgecolor="none", labelspacing=0.25, handlelength=1.5,
              bbox_to_anchor=(1.0, 0.02))


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.6, 3.0))
    draw_6f(ax)
    ax.set_title("The probe can see structure when it is there", loc="left", fontsize=8)
    fig.savefig(os.path.join(os.path.dirname(__file__), "6f.png"), dpi=200, bbox_inches="tight")
    print("wrote 6f.png")
