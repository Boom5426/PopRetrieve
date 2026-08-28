"""PopRetrieve Figure 3 panel 3b: per-task Hit@1, and the Frangieh counterexample.

Source data: results/exp08_signature_baselines/summary_by_task.csv (all 8 scorers x 3 tasks).

This panel exists to make one thing unmissable: the distributional advantage does NOT hold on
Frangieh, the only natural real dataset entering the macro-mean, where mean/CMap cosine (0.600)
beats energy (0.578) and is in fact the best of all eight scorers. A colour-scaled heatmap hides a
0.02 reversal; the paired dot-and-gap layout below cannot.

Run standalone: python fig3b.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
FOCAL, COMP, GREY, INK = "#5185C0", "#E99D4E", "#7A7A7A", "#1A1A1A"
LIGHT_GREY = "#D9D9D9"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

TASKS = [("controlled", "controlled"),
         ("crossline", "cross-line"),
         ("frangieh", "Frangieh")]
CONTEXT = ['coverage_mean', 'coverage_worst', 'pca_dist', 'pca_mean', 'cmap_wtcs']

# Within-category x offsets. At 1:1 the "six other scorers" caption is 0.33 in wide and has to sit
# under the grey cloud without touching the energy-to-mean connector, so the cloud and the pair are
# further apart than they were on the 11 in canvas (0.20 / 0.10 -> 0.20 / 0.28).
CLOUD_DX, PAIR_DX = -0.20, 0.28
GAP_LABEL_DX = PAIR_DX + 0.10


def draw_3b(ax):
    """Per-task Hit@1: energy vs mean/CMap cosine, against the other six scorers."""
    sbt = pd.read_csv(f"{REPO}/results/exp08_signature_baselines/summary_by_task.csv")
    pv = sbt.pivot_table(index='method', columns='task', values='hit@1')
    nq = sbt.pivot_table(index='method', columns='task', values='n_queries')
    # mean_cosine and cmap_cosine are numerically identical (Fig. 2d); assert rather than assume
    assert np.allclose(pv.loc['mean_cosine'].values, pv.loc['cmap_cosine'].values), \
        "mean_cosine and cmap_cosine are no longer identical; panel 3b must be relabelled"

    for i, (task, lab) in enumerate(TASKS):
        e = pv.loc['global_energy', task]
        m = pv.loc['mean_cosine', task]
        win = e > m
        col = FOCAL if win else COMP
        # six other scorers, as a quiet context cloud
        ax.scatter([i + CLOUD_DX] * len(CONTEXT), [pv.loc[c, task] for c in CONTEXT],
                   s=11, color=GREY, alpha=0.55, linewidths=0, zorder=2)
        # the pair that carries the claim
        ax.plot([i + PAIR_DX, i + PAIR_DX], [m, e], color=col, lw=1.6, alpha=0.9, zorder=2)
        ax.scatter([i + PAIR_DX], [e], s=34, color=FOCAL, zorder=4, linewidths=0)
        ax.scatter([i + PAIR_DX], [m], s=34, color=COMP, zorder=4, linewidths=0)
        d = e - m
        ax.text(i + GAP_LABEL_DX, (e + m) / 2, f'{d:+.2f}', ha='left', va='center',
                fontsize=6, color=col, fontweight='bold' if not win else 'normal')

    # direct labels instead of a legend (placed in the empty upper/lower bands)
    ax.text(-0.30, pv.loc['global_energy', 'controlled'] + 0.055, 'energy',
            fontsize=6.5, color=FOCAL, ha='left', va='bottom')
    ax.text(-0.30, pv.loc['mean_cosine', 'controlled'] - 0.055, 'mean / CMap cosine',
            fontsize=6.5, color=COMP, ha='left', va='top')
    ax.text(CLOUD_DX, min(pv.loc[c, 'controlled'] for c in CONTEXT) - 0.045,
            'six other\nscorers', fontsize=6, color=GREY, ha='center', va='top',
            linespacing=1.1)
    ax.annotate('mean wins', xy=(2 + PAIR_DX, 0.600), xytext=(1.76, 0.87),
                fontsize=6.5, color=COMP, ha='center', va='bottom',
                arrowprops=dict(arrowstyle='-|>', color=COMP, lw=0.8,
                                shrinkA=1, shrinkB=3))

    # At 1:1 the three category slots are ~0.59 in wide, so the dataset provenance that used to
    # ride on a second tick line ("SciPlex3" / "natural") no longer fits without the three labels
    # colliding. It is stated in the caption and in the panel title instead; only n stays here.
    ax.set_xticks(range(3))
    ax.set_xticklabels([f'{lab}\nn = {int(nq.loc["global_energy", t])}'
                        for t, lab in TASKS], fontsize=6, linespacing=1.35)
    ax.set_xlim(-0.60, 2.95)
    ax.set_ylim(0.18, 1.02)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_ylabel('Hit@1 (per task)')
    ax.tick_params(axis='x', length=0)
    for sp in ['right', 'top']:
        ax.spines[sp].set_visible(False)
    ax.set_title("The advantage does not\nhold on Frangieh", loc='left', linespacing=1.15)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.6, 3.0))
    draw_3b(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "3b.png"), dpi=200, bbox_inches="tight")
    print("wrote 3b.png")
