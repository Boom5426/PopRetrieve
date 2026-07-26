"""DART Figure 2 panel 2d: mean cosine and CMap cosine are the identical operation.

Source data: results/exp08_signature_baselines/summary.csv, unweighted macro-mean of hit@1
over the seven (task x setting) cells; mirrored in figures/source_data/fig2d_operation_identity.csv.
mean_cosine and cmap_cosine agree to every printed digit (0.388492); cmap_wtcs (0.463492) is the
rank-based sibling and deliberately differs.

Run standalone: python fig2d.py  (writes 2d.png)
"""
import os, numpy as np, pandas as pd, matplotlib.pyplot as plt
import sys; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def draw_2d(ax):
    """Three signature baselines on one truncated Hit@1 axis; two of them coincide."""
    s = pd.read_csv(f"{REPO}/results/exp08_signature_baselines/summary.csv")
    agg = s.groupby("method")["hit@1"].mean()
    rows = [("mean cosine", float(agg["mean_cosine"]), COMP, 2),
            ("CMap cosine", float(agg["cmap_cosine"]), COMP, 1),
            ("CMap WTCS", float(agg["cmap_wtcs"]), GREY, 0)]

    x_lo, x_hi = 0.365, 0.512
    for lab, val, col, y in rows:
        # full-width guide, not a bar: the axis is truncated, so nothing here encodes length
        ax.plot([x_lo, x_hi], [y, y], ls=":", lw=0.5, color="0.82", zorder=1)
        ax.scatter([val], [y], s=34, color=col, zorder=3)
        ax.text(val - 0.004, y + 0.20, lab, ha="left", va="bottom",
                fontsize=6.5, color=col)
        # white knockout: the row guide is drawn full width, so at 1:1 print size it would
        # otherwise strike through the digits of the value it labels.
        ax.text(val + 0.009, y, f"{val:.4f}", ha="left", va="center",
                fontsize=6, color=col, zorder=3,
                bbox=dict(facecolor="white", edgecolor="none", pad=0.9))

    # bracket tying the two coincident rows together
    xb = 0.436
    ax.plot([xb, xb], [1, 2], color="0.2", lw=0.8, zorder=4)
    ax.plot([xb - 0.004, xb], [2, 2], color="0.2", lw=0.8, zorder=4)
    ax.plot([xb - 0.004, xb], [1, 1], color="0.2", lw=0.8, zorder=4)
    ax.text(xb + 0.005, 1.5, "identical\noperation", va="center", ha="left", fontsize=6)

    ax.set_xlim(x_lo, x_hi)
    ax.set_ylim(-0.75, 2.75)
    ax.set_yticks([]); ax.spines["left"].set_visible(False)
    ax.set_xticks([0.38, 0.42, 0.46, 0.50])
    ax.set_xlabel(r"Hit@1 (macro-mean, 7 task $\times$ setting cells)")

    # axis-break glyph: the x axis starts at 0.365, not 0
    for xf in (0.014, 0.028):
        ax.plot([xf - 0.006, xf + 0.006], [-0.028, 0.028], transform=ax.transAxes,
                lw=0.7, color="0.2", clip_on=False, zorder=6)

    ax.set_title(r"Mean cosine $=$ CMap cosine, exactly", loc="left")


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(2.4, 1.9))
    draw_2d(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "2d.png"), dpi=200, bbox_inches="tight")
    print("wrote 2d.png")
