"""Figure 5 panel e: the headroom correlation is reproduced by a null with no relationship in it.
Source data: results/phase2_transition/bottleneck/summary.json (via phase2_data.headroom_null)
Run standalone: python fig5e.py

WHAT THIS PANEL RETRACTS
------------------------
Spearman(headroom, gain) = +0.79 was reported in an earlier draft as the strongest explanation of
where population scoring pays: the more room the mean route leaves, the more the population route
gains. The quantity is arithmetic. Gain is RR_pop − RR_mean and headroom is 1 − RR_mean, so the two
share a term with the same sign, and reciprocal rank is capped at 1, which bounds the gain by the
headroom query for query.

The null draws that out and nothing else. It reshuffles the population route's reciprocal ranks
WITHIN each context, so both marginals, the cap and the clustering survive and only the pairing
between the two scorers is destroyed. It reproduces the observed value. The panel therefore draws
the observed number INSIDE its own null, which is the only honest way to show a statistic that
measures its own construction.

WHY THE OBSERVED MARKER IS NOT COLOURED AS A FINDING
-----------------------------------------------------
It is drawn in the deck's neutral rather than in POP blue. Blue means population-level retrieval
throughout this deck, and a blue marker here would read as a property of the population route. It
is a property of the pairing of two reciprocal ranks under a ceiling, which is not a method.
"""
import os as _os
import sys as _sys

import matplotlib.pyplot as plt

_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from phase2_style import INK  # noqa: E402
from phase2_data import headroom_null  # noqa: E402
from phase2_style import (FAINT, LW_HAIR, PT_ANNOT, PT_SMALL, PT_TICK,  # noqa: E402
                          SHARED)

XLIM = (0.740, 0.830)       # wide enough to show the band is not a hairline, tight enough that
                            # the 0.004 between the observed value and the null mean is visible
Y_BAND = 0.60               # the null, drawn as a band on its own row
Y_OBS = 0.60                # the observed, on the SAME row: the panel's whole point is that one
                            # sits inside the other, and two rows would let a reader read them
                            # as two measurements to compare


def draw_5e(ax):
    n = headroom_null()
    assert n["inside"], (
        "the summary no longer reports the observed correlation inside its null; this panel draws "
        "a retraction and must not draw it if the retraction has stopped holding.")
    assert XLIM[0] < n["null_lo"] and n["null_hi"] < XLIM[1] and XLIM[0] < n["observed"] < XLIM[1], (
        f"the view {XLIM} no longer contains the null {n['null_lo']:.3f} to {n['null_hi']:.3f} or "
        f"the observed {n['observed']:.3f}")

    ax.axhspan(Y_BAND - 0.17, Y_BAND + 0.17, xmin=0, xmax=0, color="none")   # keeps the y scale
    ax.add_patch(plt.Rectangle((n["null_lo"], Y_BAND - 0.17), n["null_hi"] - n["null_lo"], 0.34,
                               fc=FAINT, ec="none", zorder=2))
    ax.plot([n["null_mean"]] * 2, [Y_BAND - 0.17, Y_BAND + 0.17], lw=1.1, color=SHARED, zorder=3,
            solid_capstyle="butt")
    ax.plot([n["observed"]], [Y_OBS], "o", ms=5.6, color="white", mec=INK, mew=1.2, zorder=5)

    ax.text(n["observed"], Y_OBS + 0.245, f"observed {n['observed']:.3f}", ha="center",
            va="bottom", fontsize=PT_SMALL, color=INK)
    ax.text(n["null_lo"] - 0.003, Y_BAND, f"ceiling null\n{n['n_shuffles']} shuffles",
            ha="right", va="center", fontsize=PT_SMALL, color=SHARED, linespacing=1.15)
    ax.text(n["null_hi"] + 0.003, Y_BAND - 0.02,
            f"{n['null_lo']:.3f} to {n['null_hi']:.3f}", ha="left", va="center",
            fontsize=PT_SMALL, color=SHARED)

    ax.set_ylim(0.0, 1.35)
    ax.set_yticks([])
    ax.set_xlim(*XLIM)
    ax.set_xticks([0.75, 0.78, 0.81])
    ax.set_xticklabels(["0.75", "0.78", "0.81"], fontsize=PT_TICK)
    ax.set_xlabel("Spearman ρ, headroom against oracle gain", fontsize=PT_ANNOT, labelpad=1.5)
    ax.grid(axis="x", lw=LW_HAIR, color="#E5E7E7", zorder=0)
    ax.set_axisbelow(True)
    for sp in ("right", "top", "left"):
        ax.spines[sp].set_visible(False)
    return ax


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(2.30, 0.92))
    draw_5e(ax)
    fig.savefig(_os.path.join(_os.path.dirname(__file__), "5e.png"), dpi=200, bbox_inches="tight")
    print("wrote 5e.png")
