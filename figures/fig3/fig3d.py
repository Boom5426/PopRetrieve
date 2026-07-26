"""DART Figure 3 panel 3d: gate-recommended vs not-recommended queries.

Source data: results/exp12_partial_observed_retrieval/recommendation_vs_outcome.csv
(row DART_coverage_worst). The two medians the manuscript quotes are +0.119 on the 621
gate-recommended queries and +0.122 on the 133 "mean or no call" queries: the gate does not
concentrate the Class-A gain.

Scope note kept visible on the panel: the 765 partial-observed queries of panel c split
621 + 133 + 11, the last being the gate's "mean-sufficient" verdict (median regret reduction
exactly 0.000, n = 11). Those 11 are not part of the manuscript's two-way comparison and are
therefore not plotted, but they are named on the panel so 621 + 133 does not silently fail to
add up to 765.

Run standalone: python fig3d.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
FOCAL, COMP, GREY, INK = "#5185C0", "#E99D4E", "#7A7A7A", "#1A1A1A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

MODES = [('DART_recommended', 'gate-\nrecommended', FOCAL),
         ('mean_or_no_call', 'not\nrecommended', GREY)]


def draw_3d(ax):
    """Median regret reduction inside vs outside the gate's recommendation."""
    rvo = pd.read_csv(f"{REPO}/results/exp12_partial_observed_retrieval/recommendation_vs_outcome.csv")
    cw = rvo[rvo.dart_method == 'DART_coverage_worst'].set_index('recommendation_mode')

    xs, labels, meds, ns, cols = [], [], [], [], []
    for i, (mode, lab, col) in enumerate(MODES):
        xs.append(i)
        labels.append(f'{lab}\nn = {int(cw.loc[mode, "n_queries"])}')
        meds.append(float(cw.loc[mode, 'median_regret_reduction']))
        ns.append(int(cw.loc[mode, 'n_queries']))
        cols.append(col)

    ax.bar(xs, meds, width=0.52, color=cols, alpha=0.9, linewidth=0, zorder=3)
    # level reference at the recommended-subset median: the gap between the bars is 0.003
    ax.axhline(meds[0], ls=':', lw=0.8, color=GREY, zorder=2)
    for x, m in zip(xs, meds):
        ax.text(x, m + 0.004, f'+{m:.3f}', ha='center', va='bottom', fontsize=6.5, color=INK)

    # Re-wrapped to three short lines: at 1:1 this panel is 1.45 in wide, and the 621 + 133 + 11
    # bookkeeping has to stay on the panel (the caption gives only the two plotted subsets).
    ax.text(0.5, 0.99, "11 gate\n'mean-sufficient'\nqueries not shown",
            transform=ax.transAxes, ha='center', va='top', fontsize=6, color=GREY,
            linespacing=1.2)

    ax.set_xticks(xs)
    ax.set_xticklabels(labels, fontsize=6, linespacing=1.35)
    ax.set_xlim(-0.62, 1.62)
    ax.set_ylabel('median regret reduction')
    ax.set_ylim(0, 0.212)     # headroom so the three-line scope note clears the +0.119 labels
    ax.set_yticks([0, 0.04, 0.08, 0.12])
    ax.tick_params(axis='x', length=0)
    for sp in ['right', 'top']:
        ax.spines[sp].set_visible(False)
    ax.spines['left'].set_bounds(0, 0.12)
    ax.set_title("The gate does not\nconcentrate the gain", loc='left', linespacing=1.15)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.6, 3.0))
    draw_3d(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "3d.png"), dpi=200, bbox_inches="tight")
    print("wrote 3d.png")
