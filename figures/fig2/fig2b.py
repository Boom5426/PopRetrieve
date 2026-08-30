"""PopRetrieve Figure 2 panel 2b: per-task Hit@1, and the Frangieh counterexample.

Source data: results/exp08_signature_baselines/summary_by_task.csv (all 8 scorers x 3 tasks).

This panel exists to make one thing unmissable: the distributional advantage does NOT hold on
Frangieh, the only natural real dataset entering the macro-mean, where mean/CMap cosine (0.600)
beats energy (0.578) and is in fact the best of all eight scorers. A colour-scaled heatmap hides a
0.02 reversal; the paired dot-and-gap layout below cannot.

Run standalone: python fig2b.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
# Palette comes from the house-style module; do NOT re-declare the hex values here. Every
# panel file used to carry its own copy, which made figstyle's "one edit here recolours the
# whole deck" untrue: a recolour meant editing 43 files and missing one was silent.
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from figstyle import FOCAL_SOFT, COMP_SOFT, LIGHT_GREY, RULE, META, INK  # noqa: E402
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


def draw_2b(ax):
    """Per-task Hit@1: energy vs mean/CMap cosine, against the other six scorers."""
    sbt = pd.read_csv(f"{REPO}/results/exp08_signature_baselines/summary_by_task.csv")
    pv = sbt.pivot_table(index='method', columns='task', values='hit@1')
    nq = sbt.pivot_table(index='method', columns='task', values='n_queries')
    # mean_cosine and cmap_cosine are numerically identical (panel g of this figure, Spearman
    # rho = 1.000 over 54,180 query-candidate scores; it was Extended Data Fig. 1 until the ED
    # deck was retired, and it now sits in the same float as the claim); assert rather than assume
    assert np.allclose(pv.loc['mean_cosine'].values, pv.loc['cmap_cosine'].values), \
        "mean_cosine and cmap_cosine are no longer identical; panel 2b must be relabelled"

    for i, (task, lab) in enumerate(TASKS):
        e = pv.loc['global_energy', task]
        m = pv.loc['mean_cosine', task]
        win = e > m
        # six other scorers, as a quiet context cloud
        ax.scatter([i + CLOUD_DX] * len(CONTEXT), [pv.loc[c, task] for c in CONTEXT],
                   s=9, color=LIGHT_GREY, linewidths=0, zorder=2)
        # The connector is a thin neutral rule, not a coloured one: which end is higher is
        # already carried by the two endpoint markers, and a 1.6 pt coloured stem was the
        # heaviest ink in the panel.
        ax.plot([i + PAIR_DX, i + PAIR_DX], [m, e], color=RULE, lw=2.4, solid_capstyle='round',
                zorder=2)
        ax.scatter([i + PAIR_DX], [e], s=26, color=FOCAL_SOFT, zorder=4, linewidths=0)
        ax.scatter([i + PAIR_DX], [m], s=26, color=COMP_SOFT, zorder=4, linewidths=0)
        d = e - m
        # The gap reading is ink, and the one reversal is what bold marks. Colour is left to
        # the markers.
        # The one reversal is marked by weight, not by hue: this figure's rule is that the marks
        # carry the colour and the text does not, and bold already singles the value out. It also
        # keeps the last small coloured glyph off the panel, which is what the contrast floor wants.
        ax.text(i + GAP_LABEL_DX, (e + m) / 2, f'{d:+.2f}', ha='left', va='center',
                fontsize=6, color=INK, fontweight='normal' if win else 'bold')

    # direct labels instead of a legend, in ink with a colour swatch to bind them to the markers
    for y, col, lab, va in [(pv.loc['global_energy', 'controlled'] + 0.055, FOCAL_SOFT, 'energy',
                             'bottom'),
                            (pv.loc['mean_cosine', 'controlled'] - 0.055, COMP_SOFT,
                             'mean / CMap cosine', 'top')]:
        ax.scatter([-0.34], [y + (0.012 if va == 'bottom' else -0.012)], s=16, color=col,
                   linewidths=0, zorder=4, clip_on=False)
        ax.text(-0.26, y, lab, fontsize=6.5, color=INK, ha='left', va=va)
    ax.text(CLOUD_DX, min(pv.loc[c, 'controlled'] for c in CONTEXT) - 0.045,
            'six other\nscorers', fontsize=5.8, color=META, ha='center', va='top',
            linespacing=1.1)
    ax.annotate('mean wins', xy=(2 + PAIR_DX, 0.600), xytext=(1.74, 0.87),
                fontsize=6.5, color=INK, ha='center', va='bottom',
                arrowprops=dict(arrowstyle='-|>', color=META, lw=0.7, shrinkA=1, shrinkB=3))

    # Name on the tick in ink, n on a grey line below it. The single middle-dot line this style
    # prefers needs about 0.55 in per slot and there are three slots in a 1.9 in panel, so the
    # three labels overlapped by more than half their width; the reference figure splits the same
    # pair the same way wherever its slots are narrow.
    ax.set_xticks(range(3))
    ax.set_xticklabels([lab for _, lab in TASKS], fontsize=6, color=INK)
    for i, (t, _) in enumerate(TASKS):
        # y is in axes fraction along the x-axis transform, so it must be NEGATIVE to sit below
        # the tick labels; at +0.128 it was 13% up the axes, on top of the controlled-task data.
        ax.text(i, -0.115, f'n = {int(nq.loc["global_energy", t])}',
                transform=ax.get_xaxis_transform(), ha='center', va='top', fontsize=5.6,
                color=META)
    ax.set_xlim(-0.60, 2.95)
    ax.set_ylim(0.18, 1.02)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_ylabel('Hit@1 (per task)')
    ax.tick_params(axis='x', length=0)
    ax.tick_params(axis='y', length=2.2, color=RULE, labelcolor=INK)
    for sp in ['right', 'top']:
        ax.spines[sp].set_visible(False)
    ax.spines['left'].set_color(RULE)
    ax.spines['bottom'].set_color(RULE)
    ax.set_title("The advantage does not\nhold on Frangieh", loc='left', linespacing=1.15)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.6, 3.0))
    draw_2b(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "2b.png"), dpi=200, bbox_inches="tight")
    print("wrote 2b.png")
