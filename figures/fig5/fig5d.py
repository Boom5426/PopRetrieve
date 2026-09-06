"""Figure 5 panel d: the ceiling. Most oracle queries leave the population route nothing to win.
Source data: results/phase2_transition/bottleneck/bottleneck_per_query.csv (via phase2_data.ceiling)
Run standalone: python fig5d.py

WHY THIS PANEL EXISTS, AND WHY IT IS NOT A RESULT ABOUT BIOLOGY
---------------------------------------------------------------
Panel b measures a +0.0303 MRR advantage for the population route at the oracle, and a reader
naturally asks where it comes from. The answer is a property of the BASELINE, not of the cells: on
3,110 of 3,992 queries the mean route already ranks the true drug first at every seed, so its
reciprocal rank is exactly 1 and no ranking decision is available to improve. The pooled advantage
is therefore an average over a population of queries most of which could not have contributed to it.

The panel draws that as the decomposition it is. The two group means, weighted by their own query
counts, reproduce the pooled value the caption and panel b quote, and draw_5d asserts exactly that
against results/phase2_transition/phase_a/delta_vs_reference.csv rather than trusting it.

WHY NO INTERVAL IS DRAWN
------------------------
The split is an identity, not a comparison. The groups are defined by the reference route's own
performance, so a test of "do the groups differ" would be testing the definition; and the pooled
value, which IS a comparison, carries its interval in panel b where it belongs. Drawing two
intervals here would invite a reader to read a significance the construction cannot support.
"""
import os as _os
import sys as _sys

import matplotlib.pyplot as plt
import numpy as np

_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from figstyle import INK  # noqa: E402
from phase2_data import ceiling, oracle_ladder  # noqa: E402
from phase2_style import (FAINT, LW_HAIR, POP, PT_ANNOT, PT_SMALL,  # noqa: E402
                          PT_TICK, SHARED)

POOLED_TOL = 1e-9


def draw_5d(ax):
    c = ceiling()
    rr, g = c["rr_mean_route"], c["gain"]
    perfect = rr >= 1.0 - 1e-12
    groups = [("mean route\nalready perfect", perfect, SHARED),
              ("room to\nimprove", ~perfect, POP)]

    # The pooled value this panel decomposes, read from the file panel b draws, so the two panels
    # cannot disagree about the number one of them explains.
    from phase2_data import _one, _read, MEAN_SCORER, POP_SCORER
    pooled = float(_one(_read("phase_a", "delta_vs_reference.csv"),
                        {"scorer": POP_SCORER, "reference": MEAN_SCORER}, "oracle gain")["dMRR"])
    assert abs(g.mean() - pooled) < POOLED_TOL, (
        f"the per-query gains average {g.mean():.6f} but phase_a reports {pooled:.6f}; this panel "
        f"decomposes that number and must be reading the same queries.")

    xs = np.arange(len(groups))
    for x, (label, mask, colour) in zip(xs, groups):
        m = float(g[mask].mean())
        ax.bar([x], [m], width=0.52, color=colour, lw=0, zorder=3)
        # Above a positive bar, below a negative one, so the value never sits on its own ink.
        ax.text(x, m + (0.008 if m >= 0 else -0.008), f"{m:+.4f}".replace("-", "−"),
                ha="center", va="bottom" if m >= 0 else "top", fontsize=PT_SMALL, color=INK)

    ax.axhline(pooled, ls="--", lw=1.0, color=SHARED, zorder=2)
    # On the LEFT, over the near-empty first group: the right half of the panel is the tall bar
    # and any label there sits on its ink.
    ax.text(-0.55, pooled + 0.006, f"all {c['n']:,} queries\n{pooled:+.4f}".replace("-", "−"),
            ha="left", va="bottom", fontsize=PT_SMALL, color=SHARED, linespacing=1.15)
    ax.axhline(0, lw=LW_HAIR, color=FAINT, zorder=1)

    ax.set_xticks(xs)
    # The group size goes IN the tick label. Set as its own line under the bar it belongs to, it
    # lands in the band the negative bar's value label already uses.
    ax.set_xticklabels([f"{lab}\nn = {int(mask.sum()):,}" for lab, mask, _ in groups],
                       fontsize=PT_TICK, linespacing=1.12)
    ax.tick_params(axis="x", length=0, pad=3)
    ax.set_xlim(-0.62, len(groups) - 0.38)
    ax.set_ylim(-0.030, 0.190)
    ax.set_yticks([0.0, 0.05, 0.10, 0.15])
    ax.set_yticklabels(["0", "0.05", "0.10", "0.15"], fontsize=PT_TICK)
    ax.set_ylabel("mean ΔMRR,\npopulation − mean", fontsize=PT_ANNOT, labelpad=1.5,
                  linespacing=1.15)
    ax.grid(axis="y", lw=LW_HAIR, color="#EDEDED", zorder=0)
    ax.set_axisbelow(True)
    for sp in ("right", "top"):
        ax.spines[sp].set_visible(False)
    return ax


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(1.85, 1.16))
    draw_5d(ax)
    fig.savefig(_os.path.join(_os.path.dirname(__file__), "5d.png"), dpi=200, bbox_inches="tight")
    print("wrote 5d.png")
