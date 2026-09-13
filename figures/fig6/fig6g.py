"""Figure 6 panel g: query by query, most of the oracle's gains do not survive prediction.
Source data: results/phase2_transition/synthesis/oracle_to_prediction.csv
             (via phase2_data.case_decomposition)
Run standalone: python fig6g.py

WHY A PER-QUERY DECOMPOSITION AND NOT ANOTHER MEAN
---------------------------------------------------
Panel b reports a mean ΔMRR per predictor and panel c shows where the two routes end up. Neither
says how many individual decisions changed hands, and a mean can move for two very different
reasons: many queries losing a little, or a few losing a lot. This panel counts them.

The denominator is not 3,992. It is the 755 queries on which the ORACLE population route had a
gain at all, because those are the only ones where there is something for prediction to preserve.
That number is a property of the oracle and not of any predictor, so it is identical down all five
rows, and draw_6g asserts that rather than assuming it. The other 3,237 queries are the ceiling of
panel 5d seen from the other side.

WHAT THE PANEL DOES NOT DRAW
-----------------------------
Case IV, a gain appearing under a predictor where the oracle had none, is in the caption and not on
the panel. It has a different denominator, and for ot_map it is 1,165 queries, which would be the
largest bar here and would read as the strongest result on the page. It is not one: ot_map's mean
route reaches 0.665 against the oracle's 0.945, so it has room to improve that a good ranker does
not, and by panel 5e that room alone produces gains. Drawing it beside the retained counts would
invite exactly the reading panels 5d and 5e exist to remove.
"""
import os as _os
import sys as _sys

import matplotlib.pyplot as plt
import numpy as np

_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from phase2_style import INK  # noqa: E402
from phase2_data import case_decomposition  # noqa: E402
from phase2_style import (LW_HAIR, MEAN, POP, PT_ANNOT, PT_SMALL,  # noqa: E402
                          PT_TICK, SHARED, TEXT, key_label)

BAR_H = 0.62


# The axes fig6_assemble gives this panel, which phase2_style.key_label needs.
# The axes size is measured at draw time; see phase2_style.axes_size_in.


def draw_6g(ax):
    d = case_decomposition()
    kept = d["case_III_both"].to_numpy()
    lost = d["case_II_oracle_only"].to_numpy()
    have = kept + lost
    assert len(set(have.tolist())) == 1, (
        f"the number of queries with an oracle gain differs between predictors ({have.tolist()}); "
        f"it is a property of the oracle and cannot.")
    n_have = int(have[0])

    ys = np.arange(len(d))[::-1]
    ax.barh(ys, -lost, height=BAR_H, color=MEAN, lw=0, zorder=3)
    ax.barh(ys, kept, height=BAR_H, color=POP, lw=0, zorder=3)
    for y, k, l in zip(ys, kept, lost):
        # Ink. Each count sits at the tip of its own bar, and a bar is the largest coloured mark
        # on the panel, so the hue is carried already.
        ax.text(-l - 14, y, f"{l:,}", ha="right", va="center", fontsize=PT_SMALL, color=TEXT)
        ax.text(k + 14, y, f"{k:,}", ha="left", va="center", fontsize=PT_SMALL, color=TEXT)
    ax.axvline(0, lw=1.0, color=SHARED, zorder=4)

    ax.set_yticks(ys)
    ax.set_yticklabels(d.label, fontsize=PT_TICK)
    ax.set_ylim(-0.62, len(d) - 0.38)
    ax.set_xlim(-780, 640)
    ax.set_xticks([-600, -300, 0, 300, 600])
    ax.set_xticklabels(["600", "300", "0", "300", "600"], fontsize=PT_TICK)
    ax.set_xlabel(f"queries, of the {n_have} with an oracle gain", fontsize=PT_ANNOT,
                  labelpad=1.5)
    ax.grid(axis="x", lw=LW_HAIR, color="#E5E7E7", zorder=0)
    ax.set_axisbelow(True)
    for sp in ("right", "top", "left"):
        ax.spines[sp].set_visible(False)

    # The two half-planes named on the band above the bars, each with a swatch of its own. These
    # two have no marker beside them to inherit a hue from, unlike the counts on the bars, so
    # they take the second half of the deck's rule. The denominator is in the x label, where it
    # has room: set beside these two it overlapped the left one at every width tried.
    for x, txt, col, ha in ((0.0, "oracle gain lost", MEAN, "left"),
                            (1.0, "kept", POP, "right")):
        w = key_label(ax, x, 1.02, txt, col, ha=ha)
        assert w < 0.45, (
            f"the key {txt!r} plus its swatch spans {w:.0%} of the panel; the two keys sit at "
            f"opposite ends of one band and would meet in the middle.")
    return ax


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(2.60, 1.30))
    draw_6g(ax)
    fig.savefig(_os.path.join(_os.path.dirname(__file__), "6g.png"), dpi=200, bbox_inches="tight")
    print("wrote 6g.png")
