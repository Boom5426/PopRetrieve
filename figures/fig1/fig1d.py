"""PopRetrieve Figure 1 panel 1d: two candidates that share a mean and differ in distribution.

Synthetic, seeded (RandomState(3)); this is a labelled schematic, not a data panel, and the
figure caption says so. Nothing here is read from results/.

What changed, and why (presentation only):
  * The claim of this panel is an EQUALITY of means and an INEQUALITY of distributions. The
    equality is now exact rather than approximate: each candidate cloud is rigidly translated so
    its sample mean lands on the target's sample mean. Without that the panel would draw a
    "shared mean" marker at a point none of the three clouds actually has.
  * The inequality is now carried by a marginal density band above the scatter, because in a
    plain overlaid scatter a bimodal cloud and a unimodal cloud of the same centre and similar
    footprint are genuinely hard to tell apart. Bimodal versus unimodal on the marginal is not.
  * Direct labels on the marginal curves replace the detached legend.

Run standalone: python fig1d.py
"""
import os

import numpy as np
import matplotlib.pyplot as plt

# Palette comes from the house-style module; do NOT re-declare the hex values here. Every
# panel file used to carry its own copy, which made figstyle's "one edit here recolours the
# whole deck" untrue: a recolour meant editing 43 files and missing one was silent.
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from figstyle import FOCAL_SOFT, COMP_SOFT, GREY, INK  # noqa: E402

BAND_H = 1.35          # height of the marginal density band, in data units
XLIM = (-3.0, 3.0)


def _kde(x, grid, h):
    """Plain gaussian kernel density estimate; no scipy dependency, no tuning knobs."""
    z = (grid[None, :] - x[:, None]) / h
    return np.exp(-0.5 * z ** 2).sum(0) / (len(x) * h * np.sqrt(2 * np.pi))


def draw_1d(ax):
    rng = np.random.RandomState(3)
    tgt = np.vstack([rng.normal([-1.4, 0.0], 0.35, (80, 2)),
                     rng.normal([1.4, 0.3], 0.35, (80, 2))])
    cand_a = np.vstack([rng.normal([-1.4, 0.1], 0.38, (80, 2)),
                        rng.normal([1.4, 0.2], 0.38, (80, 2))])
    m = tgt.mean(0)
    cand_b = rng.normal(m, 0.55, (160, 2))
    # rigid translation: make "shared mean" exactly true rather than approximately true
    cand_a = cand_a - cand_a.mean(0) + m
    cand_b = cand_b - cand_b.mean(0) + m

    ax.scatter(tgt[:, 0], tgt[:, 1], s=6, facecolors="none", edgecolors=GREY,
               linewidths=0.35, alpha=0.55, zorder=2)
    ax.scatter(cand_b[:, 0], cand_b[:, 1], s=6, color=COMP_SOFT, alpha=0.60,
               edgecolors="none", zorder=3)
    ax.scatter(cand_a[:, 0], cand_a[:, 1], s=6, color=FOCAL_SOFT, alpha=0.60,
               edgecolors="none", zorder=4)

    # The band baseline is derived from the drawn points, not hard-coded: with a fixed baseline
    # the upper tail of the wide candidate-B cloud leaked into the density band and read as stray
    # data inside a panel that is not a scatter.
    all_y = np.concatenate([tgt[:, 1], cand_a[:, 1], cand_b[:, 1]])
    y_rule = all_y.max() + 0.22
    y_bot = all_y.min() - 0.62

    # ---- the shared mean, drawn once and marked unambiguously ----
    # The mean rule runs up through the density band so that "same centre" is visible on the
    # marginals too, but it stops at the top of the band: carried to the axes top it ran into the
    # candidate-B label that sits above the band.
    ax.plot([m[0], m[0]], [y_bot, y_rule + BAND_H + 0.04], color=INK, lw=0.6,
            ls=(0, (3, 2)), zorder=1)
    ax.plot(m[0], m[1], marker="P", ms=6.5, color=INK, mec="white", mew=0.7, zorder=6)
    ax.annotate("", xy=(m[0] + 0.06, m[1] - 0.22), xytext=(0.92, y_bot + 0.52),
                arrowprops=dict(arrowstyle="-", lw=0.55, color=INK,
                                connectionstyle="arc3,rad=-0.18"))
    ax.text(0.98, y_bot + 0.48, "shared mean", ha="left", va="top", fontsize=5.8, color=INK)

    # ---- marginal band: same centre, different shape ----
    grid = np.linspace(-3.0, 3.0, 400)
    curves = [(tgt[:, 0], GREY, "target", 0.9),
              (cand_a[:, 0], FOCAL_SOFT, "candidate A\ndistribution-matched", 1.1),
              (cand_b[:, 0], COMP_SOFT, "candidate B\nmean-matched", 1.1)]
    dens = [_kde(x, grid, 0.30) for x, *_ in curves]
    scale = BAND_H / max(d.max() for d in dens)

    ax.plot(list(XLIM), [y_rule, y_rule], lw=0.5, color="#D9D9D9", zorder=1)
    for (x, col, _lab, lw), d in zip(curves, dens):
        y = y_rule + d * scale
        ax.fill_between(grid, y_rule, y, color=col, alpha=0.13, lw=0, zorder=2)
        ax.plot(grid, y, color=col, lw=lw, zorder=3, solid_capstyle="round")

    ax.text(-3.22, y_rule + BAND_H / 2, "density", rotation=90, ha="center", va="center",
            fontsize=5.8, color=GREY, clip_on=False)

    # ---- direct labels, no legend ----
    # The bimodal curves peak at about 0.68 of BAND_H (the unimodal candidate B sets the scale),
    # so 0.78 left this label sitting on the blue peak once the panel was authored at print width.
    ax.text(-1.44, y_rule + BAND_H * 0.90, "candidate A\ndistribution-matched", ha="center",
            va="bottom", fontsize=5.8, color=INK, linespacing=1.15)
    ax.text(m[0] + 0.16, y_rule + BAND_H + 0.10, "candidate B\nmean-matched", ha="left",
            va="bottom", fontsize=5.8, color=INK, linespacing=1.15)
    ax.text(-2.98, y_bot + 0.10, "target population", ha="left", va="bottom",
            fontsize=5.8, color=GREY)

    ax.set_xlabel("latent dimension 1 (arbitrary units)")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(*XLIM)
    ax.set_ylim(y_bot, y_rule + BAND_H + 0.82)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    # the left spine, and its label, describe the SCATTER only: above Y_RULE the vertical
    # coordinate is a density, not latent dimension 2.
    ax.spines["left"].set_bounds(y_bot, y_rule)
    ax.text(-3.22, (y_bot + y_rule) / 2, "latent dimension 2", rotation=90,
            ha="center", va="center", fontsize=plt.rcParams["axes.labelsize"],
            color="#1A1A1A", clip_on=False)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.5, 3.0))
    draw_1d(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "1d.png"), dpi=200, bbox_inches="tight")
    print("wrote 1d.png")
