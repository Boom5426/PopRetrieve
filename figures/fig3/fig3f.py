"""PopRetrieve Figure 3 panel 3f: Class-A robustness across the five PopRetrieve metrics.

Source data: figures/source_data/fig3f_classA_robustness.csv (exp12, the 621 gate-recommended
partial-observed queries). The n differs from panel c on purpose: panel c reports the headline on
all 765 queries, this panel reuses the per-metric table computed on the recommended subset, so the
subset is stated on the panel.

Run standalone: python fig3f.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
FOCAL, COMP, GREY, INK = "#5185C0", "#E99D4E", "#7A7A7A", "#1A1A1A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

LABS = {'DART_energy': 'energy', 'DART_mmd': 'MMD', 'DART_sliced_wasserstein': 'sliced-W',
        'DART_coverage_mean': 'coverage-mean', 'DART_coverage_worst': 'coverage-worst'}


def draw_3f(ax):
    """All five PopRetrieve metrics show a positive Class-A regret reduction."""
    f = pd.read_csv(f"{REPO}/figures/source_data/fig3f_classA_robustness.csv")
    f = f.sort_values('median_regret_reduction')
    assert (f['median_regret_reduction'] > 0).all(), "panel title asserts all five are positive"
    ns = sorted(f['n'].unique())
    assert len(ns) == 1, f"mixed query counts in 3f source data: {ns}"

    ys = np.arange(len(f))
    ax.barh(ys, f['median_regret_reduction'], color=FOCAL, alpha=0.9, height=0.62, linewidth=0)
    for y, v in zip(ys, f['median_regret_reduction']):
        ax.text(v + 0.003, y, f'+{v:.3f}', va='center', ha='left', fontsize=6, color=INK)

    ax.set_yticks(ys)
    ax.set_yticklabels([LABS[m] for m in f['method']], fontsize=6.5)
    ax.set_xlabel('median regret reduction\nvs mean cosine', linespacing=1.2)
    ax.set_xlim(0, 0.158)         # headroom so the +0.119 value label is not clipped at 1:1
    ax.set_xticks([0, 0.05, 0.10, 0.15])
    ax.tick_params(axis='y', length=0)
    # A clear band under the lowest bar, so the scope note sits beside no bar at 1:1.
    ax.set_ylim(-1.15, len(f) - 0.5)
    ax.text(0.98, 0.02, f'response-matching metric\nn = {ns[0]} diagnostic-positive queries',
            transform=ax.transAxes, ha='right', va='bottom', fontsize=6, color=GREY,
            linespacing=1.2)
    for sp in ['right', 'top']:
        ax.spines[sp].set_visible(False)
    ax.set_title("All five distributional metrics\ngain under response matching", loc='left',
                 linespacing=1.15)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.6, 3.0))
    draw_3f(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "3f.png"), dpi=200, bbox_inches="tight")
    print("wrote 3f.png")
