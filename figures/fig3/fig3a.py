"""PopRetrieve Figure 3 panel 3a: overall Hit@1 ladder.

Source data: results/exp08_signature_baselines/summary.csv (7 task x setting cells).
The plotted quantity is the UNWEIGHTED macro-mean over those seven cells, which is what the
manuscript reports (energy 0.837 vs mean/CMap cosine 0.389); the query-weighted variant
(0.887 vs 0.421) is quoted in the text but deliberately not plotted here.

Run standalone: python fig3a.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
FOCAL, COMP, GREY, INK = "#5185C0", "#E99D4E", "#7A7A7A", "#1A1A1A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def draw_3a(ax):
    """Overall Hit@1 ladder by scorer (unweighted mean over the 7 task x setting cells)."""
    s = pd.read_csv(f"{REPO}/results/exp08_signature_baselines/summary.csv")
    cells = sorted(s.groupby('method').size().unique())
    assert cells == [7], f"expected 7 task x setting cells per method, got {cells}"
    agg = s.groupby('method')['hit@1'].mean().sort_values()

    labs = {'global_energy': 'energy', 'pca_dist': 'PCA-dist', 'coverage_mean': 'coverage-mean',
            'coverage_worst': 'coverage-worst', 'pca_mean': 'PCA-mean', 'cmap_wtcs': 'CMap WTCS',
            'cmap_cosine': 'CMap cosine', 'mean_cosine': 'mean cosine'}
    fam = {'global_energy': FOCAL, 'coverage_mean': FOCAL, 'coverage_worst': FOCAL,
           'pca_dist': GREY, 'pca_mean': GREY, 'cmap_wtcs': GREY,
           'cmap_cosine': COMP, 'mean_cosine': COMP}
    ys = np.arange(len(agg))
    for y, (m, v) in zip(ys, agg.items()):
        ax.barh(y, v, color=fam[m], alpha=0.9, height=0.68, linewidth=0)
        ax.text(v + 0.016, y, f'{v:.3f}', va='center', ha='left', fontsize=6, color=INK)

    ax.set_yticks(ys)
    ax.set_yticklabels([labs[m] for m in agg.index], fontsize=6.5)
    for t, m in zip(ax.get_yticklabels(), agg.index):
        t.set_color(fam[m] if fam[m] != GREY else INK)
    # Shortened for the 1.77 in printed panel width; the caption carries the full definition
    # ("unweighted macro-mean over the seven (task x setting) cells").
    ax.set_xlabel('Hit@1  (macro-mean of 7 cells)')
    ax.set_xlim(0, 1.06)          # headroom so the 0.837 value label is not clipped at 1:1
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.tick_params(axis='y', length=0)
    for sp in ['right', 'top']:
        ax.spines[sp].set_visible(False)
    ax.set_title("Distributional scorers top\nthe Hit@1 ladder", loc='left', linespacing=1.15)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.6, 3.0))
    draw_3a(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "3a.png"), dpi=200, bbox_inches="tight")
    print("wrote 3a.png")
