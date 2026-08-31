"""PopRetrieve Figure 4, panel h: best decision regret by information condition.

Source data: results/exp11_hir_benchmark/method_dominance.csv (metric == decision_regret).
Run standalone: python3 ed6_panel_d.py

WHAT THE PANEL SHOWS
--------------------
Two welfare definitions, each priced twice: once from the observed responses and once from the
predicted mean. The four bars are read straight from the source file at draw time; no value in this
module is typed. Blue is the observable arm, orange is the evaluator-derived one, which is the
figure-wide colour contract in fig4_style, and it is the same contract as panel b two rows up.

2026-08-31 TYPOGRAPHY PASS: THE 6.5 pt FLOOR
--------------------------------------------
This was the last panel of the figure still drawing at the deck's old 5 pt floor. Eight artists were
under 6.5 pt and all eight were raised, none by re-sizing anything downward to compensate:

  * the four bar value labels, 5.6 -> PT_SMALL (6.5), and their gap to the bar top is now given in
    OFFSET POINTS rather than in data units, so it no longer has to be re-tuned when the axes box or
    the y limit moves;
  * the two legend entries, 5.6 -> PT_SMALL. The legend box itself is GONE: at 1.62 in wide a
    bordered key with swatches costs more area than it returns, so each series is now named once,
    in its own colour, in the headroom above the left group. Colour, not a swatch, carries the key.
    The names were first hung directly over their own bars, which is the better idiom but does not
    fit here: at 6.5 pt "observed" is 0.44 category units wide against a 0.36-unit bar, and the
    predicted-mean bar beside it is four times taller, so the overhanging letters were drawn ON
    that bar. Note for anyone tempted to move the names back: the preview harness cannot catch
    this, because it tests text against text and not text against a patch;
  * the two x tick labels, which set fontsize=6 locally and so overrode the house ladder. The local
    size is deleted and the rcParams value (PT_TICK, 6.8) applies, which is what the other eight
    panels of this figure use.

WHAT WAS CUT, AND WHERE IT GOES
-------------------------------
The standalone title "Losing structure inflates regret" is deleted. It was a conclusion, this
figure's panels state none, and fig4_assemble._assert_no_titles now enforces that; the sentence
belongs in the caption. Nothing else was removed: the legend's content survives as the two coloured
names, so no number and no name left the panel.

The caption still has to carry two things the panel does not state. First, each bar is the BEST
value over the method set, not one method followed across the four cells, and the winning method is
not the same in all four: DART_mmd for mean/observed, DART_sliced_wasserstein for
mean/predicted_mean, DART_coverage_worst for worst/observed, DART_mmd for worst/predicted_mean.
Second, the conclusion recorded in fig4_assemble.TITLES["h"], that losing population structure
inflates the decision cost and inflates it most under the minority-sensitive (worst) welfare.

THE NEW BOX
-----------
The axes is 1.62 x 1.75 in, up from 1.56 x 1.46 when four panels left this figure for Supplementary
Note 4 and the freed row went back into the nine that remain. The only constants that were measured
against the old box were the two label pads. The value pad is now expressed in points from the bar
it attaches to and the key is expressed in points from the axes corner, so both are box-independent.
The y limit is unchanged at 1.1: the tallest bar is 0.96 and its value label, at 6.5 pt, tops out at
1.021 in data units, and the key clears that by more than half the axes width horizontally.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(_HERE, "..")))
sys.path.insert(0, os.path.abspath(os.path.join(_HERE, "..", "fig4")))
# Colour and type come from the figure's frozen vocabulary; do NOT re-declare a hex value or type a
# point size here. One edit in fig4_style has to recolour and re-size the whole figure.
from fig4_style import MEAN, POP, PT_SMALL, TEXT  # noqa: E402

REPO = os.path.abspath(os.path.join(_HERE, "..", ".."))
H = os.path.join(REPO, "results", "exp11_hir_benchmark")

# layout constants, in POINTS from the artist or the corner they attach to, so they survive a
# change of axes box
PAD_VALUE = 1.8      # bar top -> baseline of its value label
KEY_X = 4.0          # left spine -> left edge of the series key
KEY_TOP = -7.5       # top spine -> baseline of the key's first line
KEY_STEP = 1.6 * PT_SMALL   # baseline -> baseline within the key; derived, so it follows PT_SMALL
BAR_W = 0.36         # bar width, in category units


def draw_ed6c(ax):
    """Best decision regret, observed against predicted-mean, for two welfare definitions."""
    md = pd.read_csv(f"{H}/method_dominance.csv")
    reg = md[md.metric == "decision_regret"]
    rows = []
    for wt in ["mean", "worst"]:
        for ic in ["observed", "predicted_mean"]:
            v = reg[(reg.welfare_type == wt) & (reg.information_condition == ic)]["best_value"]
            # one row per (welfare, condition) or the panel is not the panel it claims to be; the
            # previous `if len(v)` dropped a missing cell without saying so, which would have drawn
            # a three-bar panel captioned as four.
            assert len(v) == 1, f"expected exactly one decision_regret row for {wt}/{ic}, got {len(v)}"
            rows.append((f"{wt}\nwelfare", ic, v.iloc[0]))
    dfp = pd.DataFrame(rows, columns=["welfare", "ic", "regret"])
    piv = dfp.pivot(index="welfare", columns="ic", values="regret")
    x = np.arange(len(piv))

    series = [("observed", "observed", POP, -BAR_W / 2),
              ("predicted_mean", "predicted-mean", MEAN, +BAR_W / 2)]
    for i, (col, name, colour, dx) in enumerate(series):
        ax.bar(x + dx, piv[col], BAR_W, color=colour)
        for xi, v in enumerate(piv[col]):
            ax.annotate(f"{v:.2f}", xy=(xi + dx, v), xytext=(0, PAD_VALUE),
                        textcoords="offset points", ha="center", va="baseline",
                        fontsize=PT_SMALL, color=TEXT)
        # the legend this replaces: the series is named once, in its own colour, so the colour and
        # not a swatch carries the key. It sits in the headroom above the left group, which is the
        # only region of this axes that clears every bar and every value label at both ends of the
        # x range; a name hung directly over its own bar does NOT fit, because "observed" is wider
        # than the 0.36-unit bar it would label and the neighbouring predicted-mean bar is four
        # times taller, so the overhanging letters land ON that bar.
        ax.annotate(name, xy=(0, 1), xycoords="axes fraction",
                    xytext=(KEY_X, KEY_TOP - i * KEY_STEP), textcoords="offset points",
                    ha="left", va="baseline", fontsize=PT_SMALL, color=colour)

    ax.set_xticks(x)
    ax.set_xticklabels(piv.index)          # size comes from the house ladder (PT_TICK), not locally
    ax.set_ylabel("best decision regret")
    ax.set_ylim(0, 1.1)


if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(_HERE, "..")))
    from figstyle import apply_style, soften_axes  # noqa: E402
    from fig4_style import PT_ANNOT, PT_TICK, PT_TITLE  # noqa: E402

    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    fig = plt.figure(figsize=(3.5, 3.0))
    ax = fig.add_axes([0.22, 0.14, 1.62 / 3.5, 1.75 / 3.0])
    draw_ed6c(ax)
    soften_axes(fig)
    fig.savefig(os.path.join(_HERE, "ed6c.png"), dpi=300)
    print("wrote ed6c.png")
