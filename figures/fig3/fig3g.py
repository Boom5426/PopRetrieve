"""PopRetrieve Figure 3 panel 3g: the real-data coverage advantage, task by task.
Source data: results/exp13_real_data_projection/projection.csv
Run standalone: python fig3g.py

Rewritten 2026-07-13. This panel has now been wrong twice, in opposite directions, and both
times because it printed a COUNT that nobody could check.

  v1: titled "37 real tasks all mean-sufficient", axis label hard-coded "(0 / 37
      PopRetrieve-dominant)". 37 is the task count of exp13's QUICK *sanity* configuration; the
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

2026-07-26, presentation only. The distribution used to be drawn as a 5 x 90 heat map on a colour
scale running to the largest task (|delta| = 0.087). Since 43% of tasks are exactly zero and the
median |delta| is 0.0002, every cell that carried the actual finding rendered as white on white:
the panel was unreadable, and the only legible thing in it was the one outlier. The same numbers
are now one dot per task on a common linear axis, one row per dataset regime, so the reader sees
directly what the claim says: the mass sits on zero, the constructed cross-line mixtures carry a
thin positive tail, and the natural datasets carry none. Nothing is rescaled, clipped or binned;
row means are printed rather than inferred from colour.
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Palette comes from the house-style module; do NOT re-declare the hex values here. Every
# panel file used to carry its own copy, which made figstyle's "one edit here recolours the
# whole deck" untrue: a recolour meant editing 43 files and missing one was silent.
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from figstyle import FOCAL_SOFT, COMP_SOFT, GREY, INK  # noqa: E402
LIGHT_GREY = "#C9C9C9"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PROJ = f"{REPO}/results/exp13_real_data_projection/projection.csv"

# The only two tasks that remain dominant in >= 8 of 10 seeds when the drug is held fixed
# and the seed is resampled. Both are HDAC inhibitors. n=2 is a hypothesis, not a result.
REPLICATION_STABLE = {
    "A549->MCF7:Abexinostat (PCI-24781)",
    "A549->MCF7:Belinostat (PXD101)",
}

# Constructed mixtures first: the tail lives there, and the natural datasets below it are the
# control the claim rests on.
DS_ORDER = ["sciplex3_cross_line", "sciplex3_within_line", "cd34", "frangieh",
            "sciplex3_predicted_mean"]
DS_LAB = {"sciplex3_cross_line": "SciPlex3 cross-line (constructed)",
          "sciplex3_within_line": "SciPlex3 within-line",
          "cd34": "CD34+", "frangieh": "Frangieh",
          "sciplex3_predicted_mean": "SciPlex3, predicted candidates"}
JITTER = 0.11          # vertical spread within a row, so overlapping tasks stay countable
LABEL_OFF = 0.29       # row label baseline, in row units above the row's dots
RNG_SEED = 0           # jitter is cosmetic, but it is still seeded so the panel is reproducible


def draw_3g(ax):
    p = pd.read_csv(PROJ)
    p["delta"] = p.observed_dart_minority_cov - p.observed_mean_minority_cov

    if len(p) < 100:
        raise ValueError(
            f"{PROJ} has only {len(p)} tasks: that is the QUICK sanity configuration, and the "
            f"FULL run builds 239. Re-run exp13 without QUICK=1. This panel will not present a "
            f"sanity run as the real-data result.")

    present = [d for d in DS_ORDER if (p.dataset == d).any()]
    rng = np.random.default_rng(RNG_SEED)
    # Dashed and pale, so it cannot be confused with the column of grey dots sitting on it: 43%
    # of tasks have a difference of exactly zero, and that column is data, not an axis.
    ax.axvline(0, color=LIGHT_GREY, lw=0.7, ls=(0, (3, 2)), zorder=1)

    for i, ds in enumerate(present):
        sub = p[p.dataset == ds]
        dv = sub["delta"].to_numpy()
        yy = i + rng.uniform(-JITTER, JITTER, size=len(dv))
        cols = np.where(dv > 0, FOCAL_SOFT, np.where(dv < 0, COMP_SOFT, GREY))
        ax.scatter(dv, yy, s=5.5, c=cols, alpha=0.75, linewidths=0, zorder=2)

        base = sub["task_id"].astype(str).str.split(":").str[:2].str.join(":")
        keep = base.isin(REPLICATION_STABLE).to_numpy()
        if keep.any():                       # the two tasks that survive seed resampling
            ax.scatter(dv[keep], yy[keep], s=13, facecolors="none", edgecolors=INK,
                       linewidths=0.8, zorder=4)

        m = float(dv.mean())
        ax.plot([m], [i], marker="D", ms=3.0, mfc=INK, mec="white", mew=0.4, zorder=5)
        # Row name and row mean as one direct label in the empty strip above each row's dots.
        # As y-tick labels they were wide enough to run into panel f's axis, and a separate
        # right-hand column of means left a third of the panel empty.
        # The pale dashed zero rule runs the full height of the axes and every one of these five
        # labels crosses x = 0, so at print size the rule struck through the glyphs (clearest in
        # "n=12"). Knocked out behind the text rather than moved: the label has to
        # start at the left spine and the row means are what make it worth printing.
        # Name and statistics are one string because they share a knockout box, but the whole
        # line is set in META: it is provenance, and the dots beside it are the data.
        ax.text(-0.0615, i - LABEL_OFF, f"{DS_LAB[ds]}   mean {m:+.5f}, n={len(dv)}",
                fontsize=5.8, color=INK, va="bottom", ha="left", zorder=3,
                bbox=dict(facecolor="white", edgecolor="none", pad=0.6))

    ax.set_yticks([])
    # The row pitch has to clear the label (0.47 row units of 5.8 pt text), the jitter and the
    # marker radius on both sides of it; at the printed panel height that is the tightest
    # vertical constraint in the panel, so the limits are set from those quantities.
    ax.set_ylim(len(present) - 0.55, -0.85)        # first dataset on top
    ax.set_xlim(-0.065, 0.095)
    ax.set_xticks([-0.05, 0.0, 0.05])
    ax.tick_params(axis="x", labelsize=5.8)
    ax.tick_params(axis="y", length=0)
    # 1:1 re-cut: the old second label line ("all 239 tasks; overall mean ...; circled, above 0.01
    # in 10 of 10 seeds") was 2.4 in of 5.6 pt text on what is now a 2.4 in panel, and the Fig. 3
    # caption states all of it, so it is dropped rather than shrunk. What the caption does NOT
    # carry is the diamond key and the per-row means and n, so those stay on the panel.
    ax.set_xlabel("minority-state coverage gain, distributional $-$ mean"
                  "\none dot per task; diamond, dataset mean", fontsize=5.6)
    for sp in ("right", "top", "left"):
        ax.spines[sp].set_visible(False)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(4.2, 2.2))
    draw_3g(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "3g.png"), dpi=200, bbox_inches="tight")
    print("wrote 3g.png")
