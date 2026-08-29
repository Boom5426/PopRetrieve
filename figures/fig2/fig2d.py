"""PopRetrieve Figure 2 panel 2d: gate-recommended vs not-recommended queries.

Source data: results/exp12_partial_observed_retrieval/recommendation_vs_outcome.csv
(row DART_coverage_worst). The two medians the manuscript quotes are +0.119 on the 621
gate-recommended queries and +0.122 on the 133 "mean or no call" queries: the gate does not
concentrate the Class-A gain.

Scope note kept visible on the panel: the 765 partial-observed queries of panel c split
621 + 133 + 11, the last being the gate's "mean-sufficient" verdict (median regret reduction
exactly 0.000, n = 11). Those 11 are not part of the manuscript's two-way comparison and are
therefore not plotted, but they are named on the panel so 621 + 133 does not silently fail to
add up to 765.

Run standalone: python fig2d.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
# Palette comes from the house-style module; do NOT re-declare the hex values here. Every
# panel file used to carry its own copy, which made figstyle's "one edit here recolours the
# whole deck" untrue: a recolour meant editing 43 files and missing one was silent.
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from figstyle import FOCAL_SOFT, SLATE, RULE, META, INK  # noqa: E402
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

MODES = [('DART_recommended', 'diagnostic-\npositive', FOCAL_SOFT),
         ('mean_or_no_call', 'not\nrecommended', SLATE)]
TRACK_MAX = 0.15          # y limit, round above the larger value (+0.122)


def draw_2d(ax):
    """Median regret reduction inside vs outside the gate's recommendation."""
    rvo = pd.read_csv(f"{REPO}/results/exp12_partial_observed_retrieval/recommendation_vs_outcome.csv")
    cw = rvo[rvo.dart_method == 'DART_coverage_worst'].set_index('recommendation_mode')

    for i, (mode, lab, col) in enumerate(MODES):
        med = float(cw.loc[mode, 'median_regret_reduction'])
        n = int(cw.loc[mode, 'n_queries'])
        # NO TRACK HERE. Panel a and panel f draw one because a horizontal track reads as the
        # attainable range. Drawn vertically above a bar the same block reads as a stacked
        # remainder, i.e. as a second quantity, which is exactly what this panel must not say.
        # The near-equality of the two bars is carried by the hairline at the first median.
        ax.bar(i, med, width=0.44, color=col, linewidth=0, zorder=3)
        ax.text(i, med + 0.005, f'+{med:.3f}', ha='center', va='bottom', fontsize=6.5,
                color=INK)
        # Name in ink, n on a grey line below. Two slots of "diagnostic-positive  .  n = 621"
        # are 0.62 in each in a 1.2 in panel, so the one-line form collided; the pair is split
        # the way the reference splits its own narrow slots.
        ax.text(i, -0.020, lab, transform=ax.get_xaxis_transform(), ha='center',
                va='top', fontsize=6, color=INK, linespacing=1.25)
        ax.text(i, -0.215, f'n = {n}', transform=ax.get_xaxis_transform(),
                ha='center', va='top', fontsize=5.6, color=META)

    ax.axhline(float(cw.loc[MODES[0][0], 'median_regret_reduction']), ls=':', lw=0.8,
               color=RULE, zorder=2)
    ax.set_xticks([])
    ax.set_xlim(-0.62, 1.62)
    ax.set_ylabel('median regret reduction')
    ax.set_ylim(0, TRACK_MAX * 1.02)
    ax.set_yticks([0, 0.05, 0.10, 0.15])
    ax.tick_params(axis='x', length=0)
    ax.tick_params(axis='y', length=2.2, color=RULE, labelcolor=INK)
    for sp in ['right', 'top', 'bottom']:
        ax.spines[sp].set_visible(False)
    ax.spines['left'].set_color(RULE)
    ax.spines['left'].set_bounds(0, TRACK_MAX)
    ax.set_title("The diagnostic does not\nconcentrate the gain", loc='left', linespacing=1.15)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.6, 3.0))
    draw_2d(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "2d.png"), dpi=200, bbox_inches="tight")
    print("wrote 2d.png")
