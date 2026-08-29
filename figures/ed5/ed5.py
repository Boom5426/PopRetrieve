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
similarity (main text Fig. 3h,i).

WHAT SURVIVES. The mechanism is real and is worth reporting on its own terms:
  a  response magnitude predicts potency by itself (rho = -0.58 to -0.71 per cell line)
  b  the energy DISTANCE between query and candidate largely tracks the candidate's own
     magnitude (rho = +0.791), because big-response populations sit far from everything
  c  therefore ranking nearest-first systematically returns the smallest-response candidates,
     and every ranking's correlation with potency inverts
This is the confound that makes the magnitude control mandatory for any distributional retrieval
method claiming a functional validation.

Source data: source_data/fig3hi_class_c_potency.csv (the v2 analysis, correct energy sign)
Run standalone: python ed5.py
"""
import os

import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
from figstyle import apply_style, panel_letter, soften_axes  # noqa: E402

# Palette comes from the house-style module; do NOT re-declare the hex values here. Every
# panel file used to carry its own copy, which made figstyle's "one edit here recolours the
# whole deck" untrue: a recolour meant editing 43 files and missing one was silent.
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from figstyle import FOCAL_SOFT, COMP_SOFT, GREY, INK  # noqa: E402
GREEN_SOFT = "#55966B"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = f"{REPO}/figures/source_data/fig3hi_class_c_potency.csv"

ROWS = [
    ("energy_rho",           "energy\n(distributional retrieval)",     FOCAL_SOFT),
    ("mean_cosine_raw_rho",  "mean cosine\n(no control subtraction)",  GREY),
    ("mean_cosine_ctrl_rho", "mean cosine\n(control-subtracted)",      COMP_SOFT),
    ("magnitude_only_rho",   "response magnitude alone\n(no retrieval)", GREEN_SOFT),
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
                color=INK)
    ax.axvline(0, ls="--", lw=0.8, color=INK, zorder=1)
    ax.set_yticks(ys)
    ax.set_yticklabels([r[1] for r in ROWS], fontsize=5.6)
    ax.set_xlabel(r"Spearman $\rho$ with absolute potency (GDSC AUC)", fontsize=6)
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
    ax.hist(v, bins=18, color=FOCAL_SOFT, alpha=0.75, edgecolor="white", lw=0.4)
    m = float(np.median(v))
    ax.axvline(m, color=INK, lw=1.4)
    ax.text(m - 0.01, ax.get_ylim()[1] * 0.94, f"median\n{m:+.3f}", ha="right", va="top",
            fontsize=6, color=INK)
    ax.set_xlabel("Spearman $\\rho$ (energy distance, candidate response magnitude)", fontsize=6)
    ax.set_ylabel("queries", fontsize=6)
    ax.tick_params(labelsize=5.6)
    for sp in ("right", "top"):
        ax.spines[sp].set_visible(False)
    # The magnitude-ranking mechanism is stated in the caption (ED Fig. 5b); the in-panel
    # sentence was 4.9 pt, below the 5 pt Nature production floor.


def build():
    # THE HOUSE STYLE IS APPLIED HERE, and was not before: this figure drew on matplotlib's
    # defaults (10 pt DejaVu Sans, 1.5 pt lines, framed legends, four spines), roughly twice the
    # type size of every other figure in the submission. Same call the main deck makes.
    apply_style(sizes=(8, 7, 6))
    d = pd.read_csv(SRC)
    # Authored at the printed width. The SI text block is 6.93 in and this figure enters with
    # \includegraphics[width=\textwidth], so the previous 9.0 in canvas printed at 0.83x and
    # every nominal point size shrank with it. At 6.9 in the scale factor is 1.0.
    fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.6))
    draw_a(axes[0], d)
    draw_b(axes[1], d)
    for ax, k in zip(axes, "ab"):
        panel_letter(ax, k, dx=-0.16, dy=1.08, case="lower")
    soften_axes(fig)
    fig.subplots_adjust(wspace=0.42, bottom=0.30)
    out = os.path.dirname(os.path.abspath(__file__))
    fig.savefig(os.path.join(out, "edfig5.pdf"), bbox_inches="tight")
    fig.savefig(os.path.join(out, "edfig5.png"), dpi=300, bbox_inches="tight")
    print("wrote edfig5.pdf / .png")


if __name__ == "__main__":
    build()
