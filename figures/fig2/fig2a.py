"""PopRetrieve Figure 2 panel 2a: overall Hit@1 ladder.

Source data: results/exp08_signature_baselines/summary.csv (7 task x setting cells).
The plotted quantity is the UNWEIGHTED macro-mean over those seven cells, which is what the
manuscript reports (energy 0.837 vs mean/CMap cosine 0.389); the query-weighted variant
(0.887 vs 0.421) is quoted in the text but deliberately not plotted here.

Run standalone: python fig2a.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
# Palette comes from the house-style module; do NOT re-declare the hex values here. Every
# panel file used to carry its own copy, which made figstyle's "one edit here recolours the
# whole deck" untrue: a recolour meant editing 43 files and missing one was silent.
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from figstyle import FOCAL_SOFT, COMP_SOFT, SLATE, TRACK, RULE, META, INK  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def draw_2a(ax):
    """Overall Hit@1 ladder by scorer (unweighted mean over the 7 task x setting cells)."""
    s = pd.read_csv(f"{REPO}/results/exp08_signature_baselines/summary.csv")
    cells = sorted(s.groupby('method').size().unique())
    assert cells == [7], f"expected 7 task x setting cells per method, got {cells}"
    agg = s.groupby('method')['hit@1'].mean().sort_values()

    labs = {'global_energy': 'energy', 'pca_dist': 'PCA-dist', 'coverage_mean': 'coverage-mean',
            'coverage_worst': 'coverage-worst', 'pca_mean': 'PCA-mean', 'cmap_wtcs': 'CMap WTCS',
            'cmap_cosine': 'CMap cosine', 'mean_cosine': 'mean cosine'}
    fam = {'global_energy': FOCAL_SOFT, 'coverage_mean': FOCAL_SOFT,
           'coverage_worst': FOCAL_SOFT, 'pca_dist': SLATE, 'pca_mean': SLATE,
           'cmap_wtcs': SLATE, 'cmap_cosine': COMP_SOFT, 'mean_cosine': COMP_SOFT}

    ys = np.arange(len(agg))
    for y, (m, v) in zip(ys, agg.items()):
        # Full-extent track first, value bar on top. Hit@1 runs 0 to 1, so the track is the
        # scale: it says how much of the attainable range each scorer reaches without the
        # reader having to travel to the axis.
        ax.barh(y, 1.0, color=TRACK, height=0.46, linewidth=0, zorder=1)
        ax.barh(y, v, color=fam[m], height=0.46, linewidth=0, zorder=2)
        # Right-aligned past the end of the track, not chasing the bar tip: one reading line.
        ax.text(1.045, y, f'{v:.3f}', va='center', ha='left', fontsize=6, color=META)

    ax.set_yticks(ys)
    ax.set_yticklabels([labs[m] for m in agg.index], fontsize=6.5, color=INK)
    # The label is not coloured. In this style the mark carries the family and the text does not,
    # which is also what keeps every glyph on the panel above the contrast floor.
    ax.set_xlabel('Hit@1  (macro-mean of 7 cells)')
    ax.set_xlim(0, 1.27)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_ylim(-0.72, len(agg) - 0.5)
    ax.tick_params(axis='y', length=0)
    ax.tick_params(axis='x', length=2.2, color=RULE, labelcolor=INK)
    for sp in ['right', 'top', 'left']:
        ax.spines[sp].set_visible(False)
    ax.spines['bottom'].set_color(RULE)

    # Family key, as a metadata line rather than a legend box.
    # x positions measured against the printed panel: "population" is 0.23 axis units wide at
    # 5.6 pt, so the 0.30 slot the key first used put the next swatch inside it.
    for x, col, lab in [(0.0, FOCAL_SOFT, 'population'), (0.42, COMP_SOFT, 'mean'),
                        (0.72, SLATE, 'other')]:
        ax.add_patch(Rectangle((x, -0.70), 0.055, 0.20, color=col, lw=0, clip_on=False,
                               zorder=3))
        ax.text(x + 0.075, -0.60, lab, fontsize=5.6, color=META, va='center', ha='left')

    ax.set_title("Distributional scorers top\nthe Hit@1 ladder", loc='left', linespacing=1.15)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.6, 3.0))
    draw_2a(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "2a.png"), dpi=200, bbox_inches="tight")
    print("wrote 2a.png")
