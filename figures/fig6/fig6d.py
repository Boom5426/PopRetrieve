"""DART Figure 6 panel 6d: multi-dim structure diagnostics
Source data: source_data/fig6cd_structure_diagnostics.csv
Run standalone: python fig6d.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
from scipy import stats
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"
from matplotlib.colors import LinearSegmentedColormap
DIVMAP = LinearSegmentedColormap.from_list('dart_div', [COMP, '#f7f7f7', FOCAL])
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

PREDS = ["average_effect", "scgen", "nearest_neighbor"]
PLABS = ["avg-effect", "latent", "NN"]
REAL = "real_blend"          # the alpha-blended candidate a scorer actually ranks
SYNTH = "cells"              # the faithful synthesizer; 'gaussian' is the retracted legacy one


def draw_6d(ax):
    """predicted/real ratio per structure diagnostic, under the FAITHFUL synthesizer.

    A ratio near 1 means the predictor preserves that property of the real candidate
    population. Under the legacy 'gaussian' synthesizer every ratio collapsed toward 0, but
    that measured the synthesizer (an isotropic cloud), not the predictor. Rows are selected
    on synth='cells' and the panel fails loudly if those rows are absent.
    """
    sd = pd.read_csv(f"{REPO}/results/exp09_structure_diagnostics/"
                     f"exp09_structure_diagnostics_summary.csv")

    def row(pred, synth):
        sub = sd[(sd.predictor == pred) & (sd.synth == synth)]
        if sub.empty:
            raise KeyError(f"no row predictor={pred!r} synth={synth!r}; re-run "
                           f"exp09_structure_diagnostics.py --synth both")
        return sub.iloc[0]

    real = row(REAL, "real")
    mets = [("subpop_variance_ratio_mean", "subpop\nvar ratio"),
            ("response_diversity_mean", "response\ndiversity"),
            ("isotropy_index_mean", "isotropy")]
    M = np.array([[row(p, SYNTH)[col] / real[col] for col, _ in mets] for p in PREDS])

    im = ax.imshow(M, cmap=DIVMAP, vmin=0, vmax=2, aspect="auto")
    ax.set_xticks(range(len(mets))); ax.set_xticklabels([m[1] for m in mets], fontsize=5.5)
    ax.set_yticks(range(len(PREDS))); ax.set_yticklabels(PLABS, fontsize=6)
    for i in range(len(PREDS)):
        for j in range(len(mets)):
            ax.text(j, i, f"{M[i,j]:.2f}", ha="center", va="center", fontsize=6,
                    color="white" if abs(M[i, j] - 1) > 0.6 else "k")
    cb = ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cb.set_label("predicted / real", fontsize=6); cb.ax.tick_params(labelsize=5)
    ax.set_title("Structure diagnostics, real vs predicted", loc="left")


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.4,3.0))
    draw_6d(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "6d.png"), dpi=200, bbox_inches="tight")
    print("wrote 6d.png")
