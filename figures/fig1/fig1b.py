"""PopRetrieve Figure 1 panel 1b: the biological motivation, drawn rather than rendered.

The claim this panel has to carry, and the whole reason a distributional score could matter:
two drugs can produce the SAME population mean shift and OPPOSITE consequences for a resistant
minority. The mean is a sufficient statistic only if every cell responds the same way.

Schematic, not data. It states the hypothesis the paper then tests; it asserts no result.

Design notes (presentation only, no data involved):
  * Everything is laid out on ONE shared response axis, so "same mean shift" is a geometric fact
    the reader can see: a single orange dashed line marks the treated population mean and both
    drugs' mean markers sit on it.
  * Points are drawn from a seeded generator, then each lane is rigidly translated so that its
    POPULATION mean lands exactly on the intended value. Without that correction the two drugs'
    sample means differ by ~0.01 and the panel would assert an identity it does not draw. The
    translation is a whole-lane shift, so it changes no within-lane structure.
  * Drug B's majority must overshoot (1.25 rather than 1.00) precisely because its minority does
    not move: 0.8 x 1.25 + 0.2 x 0 = 1.0. That is the honest way to hold the mean fixed, and it
    also makes the point sharper: the bulk response is not the same either, yet the mean is.
  * Palette semantics: GREY = context (the responding bulk, which both scoring rules see),
    FOCAL_SOFT blue = the distributional signal (the minority, visible only to a distributional score),
    COMP_SOFT orange = the mean / the collapse (mean markers, the shared-mean rules, the delta arrow).

Run standalone: python fig1b.py
"""
import os

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Ellipse

# Palette comes from the house-style module; do NOT re-declare the hex values here. Every
# panel file used to carry its own copy, which made figstyle's "one edit here recolours the
# whole deck" untrue: a recolour meant editing 43 files and missing one was silent.
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from figstyle import FOCAL_SOFT, COMP_SOFT, GREY, INK  # noqa: E402

# response-axis geometry: r (arbitrary response units) -> panel x
R0, RS = 3.10, 3.50
SD_R = 0.105
N_MAJ, N_MIN = 184, 46          # 80 % / 20 %

LANES = [
    # label,        centre y, majority r, minority r, population mean r
    ("untreated",       8.70, 0.00, 0.00, 0.00),
    ("+ drug A",        5.55, 1.00, 1.00, 1.00),
    ("+ drug B",        2.50, 1.25, 0.00, 1.00),
]
DY = 0.92          # majority / minority sub-row offset within a lane
SD_Y = 0.17        # within-sub-row vertical jitter (cosmetic only)


def _X(r):
    return R0 + RS * r


def _lane(ax, rng, cy, r_maj, r_min, r_mean):
    """Draw one population lane and return the drawn population mean x."""
    maj = np.column_stack([rng.normal(r_maj, SD_R, N_MAJ),
                           rng.normal(cy + DY, SD_Y, N_MAJ)])
    mnr = np.column_stack([rng.normal(r_min, SD_R, N_MIN),
                           rng.normal(cy - DY, SD_Y, N_MIN)])
    # rigid translation so the drawn population mean equals the intended one exactly
    shift = r_mean - np.concatenate([maj[:, 0], mnr[:, 0]]).mean()
    maj[:, 0] += shift
    mnr[:, 0] += shift

    ax.scatter(_X(maj[:, 0]), maj[:, 1], s=3.4, c=GREY, alpha=0.50, lw=0, zorder=2)
    ax.scatter(_X(mnr[:, 0]), mnr[:, 1], s=4.6, c=FOCAL_SOFT, alpha=0.90, lw=0, zorder=3)
    return _X(r_mean), _X(r_min)


def draw_1b(ax):
    rng = np.random.default_rng(11)
    # x limits are trimmed to the drawn content (lane labels start near r-units 1.1, the rightmost
    # annotation ends near 9.1). The old 0-10.2 window left about 1.5 units of dead margin, which
    # at the printed panel width is a fifth of an inch of empty canvas on each flank.
    ax.set_xlim(0.80, 9.55)
    # top headroom is set by the "identical mean shift" label, which sits at y = 10.66 with
    # va="bottom": at the printed panel height one line of 6.4 pt is ~0.6 data units, so 11.20
    # clipped it. The panel is authored at final print size, so this margin is now literal.
    ax.set_ylim(-0.22, 11.52)
    ax.axis("off")

    x_un, x_tr = _X(0.0), _X(1.0)

    # ---- the two mean rules: the geometry that makes "identical mean shift" visible ----
    ax.plot([x_un, x_un], [1.10, 10.20], ls=(0, (3, 2)), lw=0.7, color=GREY, zorder=1)
    ax.plot([x_tr, x_tr], [0.72, 10.20], ls=(0, (3, 2)), lw=0.8, color=COMP_SOFT, zorder=1)

    # Hairline weights and plain weight on the annotations. Bold is reserved for the structural
    # row identifiers (the three lane names); a bolded conclusion is emphasis, not information,
    # and this panel had four of them competing with the marks they describe.
    ax.add_patch(FancyArrowPatch((x_un, 10.48), (x_tr, 10.48), arrowstyle="<|-|>",
                                 mutation_scale=6, lw=0.8, color=COMP_SOFT, zorder=4))
    ax.text((x_un + x_tr) / 2, 10.66, "identical mean shift", ha="center", va="bottom",
            fontsize=6.4, color=INK)

    # ---- the three populations ----
    for label, cy, r_maj, r_min, r_mean in LANES:
        xm, x_min_cloud = _lane(ax, rng, cy, r_maj, r_min, r_mean)
        # grouping bracket: the two sub-rows are ONE population, not two samples
        ax.plot([1.94, 1.94], [cy - DY - 0.44, cy + DY + 0.44], lw=0.8, color="#C7C7C7",
                solid_capstyle="round", zorder=1)
        ax.text(1.78, cy, label, ha="right", va="center", fontsize=6.6,
                color=INK, fontweight="bold")
        ax.scatter([xm], [cy], marker="D", s=26, c=COMP_SOFT, edgecolors="white",
                   linewidths=0.6, zorder=6)

    # minority rings: dashed where the minority behaves like the bulk, solid where it does not
    ax.add_patch(Ellipse((x_un, LANES[0][1] - DY), 2.25, 1.00, fill=False, ec=FOCAL_SOFT,
                         lw=0.8, ls=(0, (2.5, 1.8)), zorder=4))
    ax.add_patch(Ellipse((x_tr, LANES[1][1] - DY), 2.25, 1.00, fill=False, ec=FOCAL_SOFT,
                         lw=0.8, ls=(0, (2.5, 1.8)), zorder=4))
    ax.add_patch(Ellipse((x_un, LANES[2][1] - DY), 2.35, 1.10, fill=False, ec=FOCAL_SOFT,
                         lw=1.1, zorder=4))

    # ---- direct labels, all placed in empty space, none crossing a mark ----
    # One line each. The counts identify the two sub-rows and stay; they used to be set on a
    # second line, which doubled the ink of the two largest text blocks in the panel for no
    # information. The arithmetic they support (0.8 x 1.25 + 0.2 x 0 = 1.0) is in the caption.
    # x = 4.35, and no comma: on one line "resistant minority, 20%" is 0.78 in, which at this
    # panel's 3.17 in width is 2.15 data units, so from 4.55 it ran onto the orange mean rule at
    # 6.60. The rule is the panel's whole geometric claim and nothing may cross it.
    ax.text(4.35, LANES[0][1] + DY, "responding bulk 80%", ha="left", va="center",
            fontsize=5.8, color=GREY)
    ax.text(4.35, LANES[0][1] - DY, "resistant minority 20%", ha="left", va="center",
            fontsize=5.8, color=INK)
    ax.text(3.34, LANES[0][1], "population mean", ha="left", va="center",
            fontsize=5.8, color=INK)

    # Both minority labels are set on two lines. On one line "minority responds" is 0.68 in wide,
    # which was 0.9 data units while this panel had a full-width row and is 1.9 units now that
    # it shares row 1 with panel a: it ran past the right edge of the canvas, and its partner ran
    # across the orange shared-mean rule. Wrapping halves the width and costs nothing, because the
    # vertical space beside each ring was empty.
    ax.plot([7.80, 8.02], [LANES[1][1] - DY, LANES[1][1] - DY], lw=0.6, color=FOCAL_SOFT, zorder=4)
    ax.text(8.10, LANES[1][1] - DY, "minority\nresponds", ha="left", va="center",
            fontsize=6.0, color=INK, linespacing=1.15)
    # "minority survives" used to sit BELOW the solid ring. At the printed panel height the gap
    # between the ring and the response axis is about 0.11 in and the label is 0.08 in tall, so it
    # collided with the axis arrow. It is now a leader label on the ring's right flank, which is
    # also how the drug-A ring is labelled, so the two minority annotations read in parallel.
    ax.plot([4.38, 4.58], [LANES[2][1] - DY, LANES[2][1] - DY], lw=0.6, color=FOCAL_SOFT, zorder=4)
    ax.text(4.66, LANES[2][1] - DY, "minority\nsurvives", ha="left", va="center",
            fontsize=6.0, color=INK, linespacing=1.15)

    # ---- the response axis ----
    ax.add_patch(FancyArrowPatch((1.95, 0.34), (8.95, 0.34), arrowstyle="-|>",
                                 mutation_scale=7, lw=0.7, color=INK))
    ax.text(5.45, -0.16, "phenotypic response coordinate (arbitrary units)",
            ha="center", va="bottom", fontsize=5.8, color=GREY)


if __name__ == "__main__":
    # Same axes geometry the composite gives this panel, so a position tuned here is correct there.
    fig, ax = plt.subplots(figsize=(3.167, 1.538))
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    draw_1b(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "1b.png"), dpi=300)
    print("wrote 1b.png")
