"""PopRetrieve Figure 2 panel 2e: alpha-crossover.

Source data: figures/source_data/fig2e_alpha_crossover.csv (exp01 controlled mixing sweep,
three cell lines x five alpha levels). Higher alpha means the two constructed subpopulations
overlap more; the energy advantage over mean cosine narrows as they merge.

Run standalone: python fig2e.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
from matplotlib.lines import Line2D
# Palette comes from the house-style module; do NOT re-declare the hex values here. Every
# panel file used to carry its own copy, which made figstyle's "one edit here recolours the
# whole deck" untrue: a recolour meant editing 43 files and missing one was silent.
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from figstyle import FOCAL_SOFT, COMP_SOFT, RULE, META, INK  # noqa: E402
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

LINES = [('K562', 'o'), ('A549', 's'), ('MCF7', '^')]


def draw_2e(ax):
    """exp01 alpha-crossover: the energy advantage narrows as subpopulations merge."""
    cr = pd.read_csv(f"{REPO}/figures/source_data/fig2e_alpha_crossover.csv")
    for cl, mk in LINES:
        d = cr[cr.cell_line == cl].sort_values('alpha')
        e = d['global_energy_hit@1'].values
        assert all(e[i] >= e[i + 1] for i in range(len(e) - 1)), \
            f"{cl}: energy Hit@1 is not monotone in alpha, the panel title no longer holds"
        ax.plot(d['alpha'], d['global_energy_hit@1'], '-', marker=mk, color=FOCAL_SOFT,
                ms=3.0, lw=1.0, alpha=0.9, zorder=3, clip_on=False)
        ax.plot(d['alpha'], d['mean_cosine_hit@1'], '--', marker=mk, color=COMP_SOFT,
                ms=3.0, lw=0.9, alpha=0.85, zorder=3, clip_on=False)

    # Two frameless keys in the header band. Both are META grey with the sample line or marker
    # carrying the colour, which is the same rule the rest of this figure follows: a key entry is
    # secondary text, not a coloured label.
    fam = [Line2D([], [], color=FOCAL_SOFT, ls='-', lw=1.0, label='energy'),
           Line2D([], [], color=COMP_SOFT, ls='--', lw=0.9, label='mean cosine')]
    key = [Line2D([], [], color=META, ls='none', marker=mk, ms=3.0, label=cl)
           for cl, mk in LINES]
    leg1 = ax.legend(handles=fam, loc='upper left', bbox_to_anchor=(-0.01, 1.005),
                     fontsize=6, frameon=False, handlelength=1.6, labelspacing=0.55,
                     borderpad=0.0, handletextpad=0.5, labelcolor=META)
    ax.add_artist(leg1)
    ax.legend(handles=key, loc='upper right', bbox_to_anchor=(1.02, 1.005), ncol=3,
              fontsize=6, frameon=False, handlelength=0.6, columnspacing=0.9,
              borderpad=0.0, handletextpad=0.3, labelcolor=META)

    ax.set_xlabel('subpopulation mixing $\\alpha$\n(higher = more merged)', linespacing=1.2)
    ax.set_ylabel('Hit@1')
    ax.set_xlim(0.47, 0.93)
    ax.set_xticks([0.5, 0.6, 0.7, 0.8, 0.9])
    ax.set_ylim(-0.05, 1.42)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.tick_params(axis='both', length=2.2, color=RULE, labelcolor=INK)
    for sp in ['right', 'top']:
        ax.spines[sp].set_visible(False)
    for sp in ['left', 'bottom']:
        ax.spines[sp].set_color(RULE)
    ax.spines['left'].set_bounds(0, 1.0)
    # Deliberately weaker than the manuscript caption's "the energy advantage narrows as
    # subpopulations merge". That is true of K562 (gap 1.00 -> 0.05) but NOT of A549
    # (0.40 -> 0.65) or MCF7 (0.35 -> 0.45). What every line does show is energy Hit@1 falling
    # monotonically with alpha, so that is what the title claims.
    ax.set_title("Energy retrieval degrades as\nsubpopulations merge", loc='left',
                 linespacing=1.15)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.6, 3.0))
    draw_2e(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "2e.png"), dpi=200, bbox_inches="tight")
    print("wrote 2e.png")
