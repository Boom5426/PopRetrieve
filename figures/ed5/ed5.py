"""Extended Data Fig. 5: the absolute-potency confounder audit.

This is the analysis that USED to be the paper's headline Class-C result, reported as "retrieval
similarity is anti-aligned with therapeutic utility". That claim has been withdrawn, and this
figure exists to show why, and to preserve the one thing the analysis genuinely establishes: the
magnitude channel.

THE MISMATCH. A similarity retriever is asked which candidate RESEMBLES the query. Absolute
potency asks which candidate kills hardest. These are different questions, and a correctly working
retriever handed a weak query SHOULD return other weak drugs. So grading retrieval on absolute
potency is not a neutral test: it is close to guaranteed to produce a negative correlation, and
close to guaranteed to be won by a scalar that sorts candidates by response magnitude, because
potency is largely driven by magnitude. The semantically matched oracle is drug-drug functional
similarity (main text Fig. 4h,i).

WHAT SURVIVES. The mechanism is real and is worth reporting on its own terms:
  a  response magnitude predicts potency by itself (rho = -0.58 to -0.71 per cell line)
  b  the energy DISTANCE between query and candidate largely tracks the candidate's own
     magnitude (rho = +0.791), because big-response populations sit far from everything
  c  therefore ranking nearest-first systematically returns the smallest-response candidates,
     and every ranking's correlation with potency inverts
This is the confound that makes the magnitude control mandatory for any distributional retrieval
method claiming a functional validation.

Source data: source_data/fig4hi_class_c_potency.csv (the v2 analysis, correct energy sign)
Run standalone: python ed5.py
"""
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

FOCAL, COMP, GREY, INK = "#5185C0", "#E99D4E", "#7A7A7A", "#1A1A1A"
GREEN = "#55966B"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = f"{REPO}/figures/source_data/fig4hi_class_c_potency.csv"

ROWS = [
    ("energy_rho",           "energy\n(distributional retrieval)",     FOCAL),
    ("mean_cosine_raw_rho",  "mean cosine\n(no control subtraction)",  GREY),
    ("mean_cosine_ctrl_rho", "mean cosine\n(control-subtracted)",      COMP),
    ("magnitude_only_rho",   "response magnitude alone\n(NO retrieval)", GREEN),
]
LINES, MARKS = ["A549", "K562", "MCF7"], ["o", "s", "^"]


def draw_a(ax, d):
    """The mismatched oracle: every ranking inverts and the trivial scalar wins."""
    ys = np.arange(len(ROWS))[::-1]
    for y, (col, _l, c) in zip(ys, ROWS):
        med = float(d[col].median())
        for ln, mk in zip(LINES, MARKS):
            ax.plot(float(d[d.cell_line == ln][col].median()), y, mk, ms=3.2,
                    mfc="none", mec=c, mew=0.8, zorder=3)
        ax.plot([med, med], [y - 0.28, y + 0.28], color=c, lw=2.6, zorder=4,
                solid_capstyle="butt")
        ax.text(med, y + 0.37, f"{med:+.2f}", ha="center", va="bottom", fontsize=6,
                color=c, fontweight="bold")
    ax.axvline(0, ls="--", lw=0.8, color=INK, zorder=1)
    ax.set_yticks(ys)
    ax.set_yticklabels([r[1] for r in ROWS], fontsize=5.6)
    ax.set_xlabel(r"Spearman $\rho$ with ABSOLUTE potency (GDSC AUC)", fontsize=6)
    ax.set_xlim(-0.95, 0.95)
    ax.set_ylim(-0.8, len(ROWS) - 0.25)
    for sp in ("right", "top"):
        ax.spines[sp].set_visible(False)
    ax.legend(handles=[plt.Line2D([], [], ls="", marker=mk, ms=3.2, mfc="none", mec=INK,
                                  mew=0.8, label=ln) for ln, mk in zip(LINES, MARKS)],
              loc="lower right", fontsize=5.2, frameon=False)
    # The mismatched-oracle caveat lives in the Extended Data Fig. 5 caption, which already
    # carries it in full. It was set at 4.9 pt here, below the 5 pt Nature production floor.


def draw_b(ax, d):
    """Why it inverts: the energy DISTANCE is largely a candidate-magnitude ranking."""
    v = d.energydist_vs_candmag_rho.values
    ax.hist(v, bins=18, color=FOCAL, alpha=0.75, edgecolor="white", lw=0.4)
    m = float(np.median(v))
    ax.axvline(m, color=INK, lw=1.4)
    ax.text(m - 0.01, ax.get_ylim()[1] * 0.94, f"median\n{m:+.3f}", ha="right", va="top",
            fontsize=6, fontweight="bold", color=INK)
    ax.set_xlabel("Spearman $\\rho$ (energy DISTANCE, candidate response magnitude)", fontsize=6)
    ax.set_ylabel("queries", fontsize=6)
    ax.tick_params(labelsize=5.6)
    for sp in ("right", "top"):
        ax.spines[sp].set_visible(False)
    # The magnitude-ranking mechanism is stated in the caption (ED Fig. 5b); the in-panel
    # sentence was 4.9 pt, below the 5 pt Nature production floor.


def build():
    d = pd.read_csv(SRC)
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.1))
    draw_a(axes[0], d)
    draw_b(axes[1], d)
    for ax, k in zip(axes, "ab"):
        ax.text(-0.16, 1.06, k, transform=ax.transAxes, fontsize=10, fontweight="bold")
    fig.subplots_adjust(wspace=0.42, bottom=0.30)
    out = os.path.dirname(os.path.abspath(__file__))
    fig.savefig(os.path.join(out, "edfig5.pdf"), bbox_inches="tight")
    fig.savefig(os.path.join(out, "edfig5.png"), dpi=300, bbox_inches="tight")
    print("wrote edfig5.pdf / .png")


if __name__ == "__main__":
    build()
