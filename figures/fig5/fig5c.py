"""Figure 5 panel c: decision correction at the oracle, corrected against reverse top-1 flips.
Source data: results/phase2_transition/synthesis/gate3_decision_relevance.csv (via phase2_data)
Run standalone: python fig5c.py

WHY BOTH BARS
-------------
A corrected-flip rate on its own is not interpretable. Any rule that reshuffles the top of a
ranking produces corrected flips in proportion to how often it flips at all, so the quantity that
carries the claim is the balance against flips in the other direction. The reverse bar is not a
control added for completeness; without it the corrected bar means nothing.
"""
import os, sys as _sys, os as _os
import numpy as np, matplotlib.pyplot as plt
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from phase2_style import INK  # noqa: E402
from phase2_style import POP, MEAN, SHARED, PT_SMALL, PT_TICK, PT_ANNOT, LW_HAIR  # noqa: E402
from phase2_data import oracle_flips  # noqa: E402

W = 0.34


def draw_5c(ax):
    d = oracle_flips()
    xs = np.arange(len(d))
    for x, (_, r) in zip(xs, d.iterrows()):
        for off, key, col in ((-W / 2 - 0.02, "corrected", POP), (W / 2 + 0.02, "reverse", MEAN)):
            v, lo, hi = r[key], r[f"{key}_lo"], r[f"{key}_hi"]
            ax.bar(x + off, v * 100, width=W, color=col, lw=0, zorder=2)
            ax.plot([x + off, x + off], [lo * 100, hi * 100], lw=0.9, color=INK, zorder=3)
            ax.text(x + off, hi * 100 + 0.16, f"{v * 100:.1f}", ha="center", va="bottom",
                    fontsize=PT_SMALL, color=INK)
        # The ratio is the quantity, so it is written once per reference rather than left to be
        # divided off the two bar heights.
        ax.text(x, -0.62, f"{r.corrected / r.reverse:.1f} : 1", ha="center", va="top",
                fontsize=PT_SMALL, color=SHARED)

    ax.set_xticks(xs)
    ax.set_xticklabels(d.label, fontsize=PT_TICK, linespacing=1.15)
    ax.tick_params(axis="x", pad=12)
    ax.set_xlabel("reference for the top-1 comparison", fontsize=PT_ANNOT, labelpad=1.0)
    ax.set_xlim(-0.6, len(d) - 0.4)
    ax.set_ylim(0, 8.6)
    ax.set_ylabel("decisions changed (%)", fontsize=PT_ANNOT, labelpad=2.0)
    ax.tick_params(axis="y", labelsize=PT_TICK)
    ax.grid(axis="y", lw=LW_HAIR, color="#E5E7E7", zorder=0)
    ax.set_axisbelow(True)
    for sp in ("right", "top"):
        ax.spines[sp].set_visible(False)
    # A two-swatch key on the top band, the same idiom as panel f. Set beside the bars it
    # landed on the first value label, which is 5.6 and the largest number in the panel.
    from matplotlib.patches import Rectangle
    for i, (txt, col) in enumerate((("corrected", POP), ("broken", MEAN))):
        x0 = -0.52 + i * 0.72
        ax.add_patch(Rectangle((x0, 8.02), 0.10, 0.30, color=col, lw=0, clip_on=False, zorder=5))
        ax.text(x0 + 0.14, 8.17, txt, ha="left", va="center", fontsize=PT_SMALL, color=INK)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(1.96, 1.15))
    draw_5c(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "5c.png"), dpi=200, bbox_inches="tight")
    print("wrote 5c.png")
