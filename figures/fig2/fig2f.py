"""PopRetrieve Figure 2 panel 2f: Class-A robustness across the five PopRetrieve metrics.

Source data: figures/source_data/fig2f_classA_robustness.csv (exp12, the 621 gate-recommended
partial-observed queries). The n differs from panel c on purpose: panel c reports the headline on
all 765 queries, this panel reuses the per-metric table computed on the recommended subset, so the
subset is stated on the panel.

Run standalone: python fig2f.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
# Palette comes from the house-style module; do NOT re-declare the hex values here. Every
# panel file used to carry its own copy, which made figstyle's "one edit here recolours the
# whole deck" untrue: a recolour meant editing 43 files and missing one was silent.
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from figstyle import FOCAL_SOFT, TRACK, RULE, META, INK  # noqa: E402
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

LABS = {'DART_energy': 'energy', 'DART_mmd': 'MMD', 'DART_sliced_wasserstein': 'sliced-W',
        'DART_coverage_mean': 'coverage-mean', 'DART_coverage_worst': 'coverage-worst'}


def draw_2f(ax):
    """All five PopRetrieve metrics show a positive Class-A regret reduction."""
    f = pd.read_csv(f"{REPO}/figures/source_data/fig2f_classA_robustness.csv")
    f = f.sort_values('median_regret_reduction')
    assert (f['median_regret_reduction'] > 0).all(), "the caption asserts all five are positive"
    ns = sorted(f['n'].unique())
    assert len(ns) == 1, f"mixed query counts in 2f source data: {ns}"

    # The track runs to a round number above the largest value, so it is a stated scale rather
    # than a bar-relative one. Same idiom as panel a.
    TRACK_MAX = 0.15
    ys = np.arange(len(f))
    for y, v in zip(ys, f['median_regret_reduction']):
        ax.barh(y, TRACK_MAX, color=TRACK, height=0.44, linewidth=0, zorder=1)
        ax.barh(y, v, color=FOCAL_SOFT, height=0.44, linewidth=0, zorder=2)
        ax.text(TRACK_MAX * 1.055, y, f'+{v:.3f}', va='center', ha='left', fontsize=6,
                color=META)

    ax.set_yticks(ys)
    ax.set_yticklabels([LABS[m] for m in f['method']], fontsize=6.5, color=INK)
    ax.set_xlabel('median regret reduction\nvs mean cosine', linespacing=1.2)
    ax.set_xlim(0, TRACK_MAX * 1.42)
    ax.set_xticks([0, 0.05, 0.10, 0.15])
    ax.set_ylim(-0.62, len(f) - 0.5)
    ax.tick_params(axis='y', length=0)
    ax.tick_params(axis='x', length=2.2, color=RULE, labelcolor=INK)
    for sp in ['right', 'top', 'left']:
        ax.spines[sp].set_visible(False)
    ax.spines['bottom'].set_color(RULE)
    ax.set_title("All five distributional metrics\ngain under response matching", loc='left',
                 linespacing=1.15)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.6, 3.0))
    draw_2f(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "2f.png"), dpi=200, bbox_inches="tight")
    print("wrote 2f.png")
