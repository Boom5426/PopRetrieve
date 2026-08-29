"""Figure 5 panel 5a: predict-then-rank schematic, with the three conditions named.
Source data: (schematic)
Run standalone: python fig5a.py

Redrawn 2026-07-26 (presentation only). The old version was a five-box horizontal flow whose
title, "Retrieval limited by the predictor", asserted a result the schematic does not show.
The manuscript caption says what this panel is for: "the predict-then-rank design ... and the
two gates are the two properties such a candidate population must have". The flow is now
vertical (it fits the narrow first column without shrinking type) and the gates are drawn
as the chips a candidate must pass, which is what ties the rest of the figure together:
b-d test Gate 1, e-f test Gate 2, g is consistent with Gate 3.

RE-CUT 2026-07-26 for the 1:1 canvas. Figure 5 is now authored at its printed width (6.9 in) and
this panel gets a 1.33 x 1.42 in slot, so a box is 1.30 in wide and holds about 32 characters at
5.8 pt. Every line was rewrapped to that measure rather than shrunk to fit it.

GATE 3 ADDED, and the whole column had to be re-budgeted to take it. Vertical space in a 1.42 in
slot is the binding constraint: one line of 5.8 pt text at linespacing 1.25 is 0.0709 in axes
units, so a three-line box costs 0.213 plus 0.020 of boxstyle pad, and the five-box flow already
spent 1.005 of the 1.0 available. A sixth box therefore had to be paid for, not appended. It was
paid for by rewrapping Gate 1 and Gate 2 from three lines to two ("Gate N: <question>" instead of
"Gate N" on a line of its own), which frees 0.136, plus 0.033 from the query and population boxes.
That is 0.169 against the 0.172 the new box and its tie need, and the column now sums to 0.988.
Shrinking the type instead was rejected: 5.8 pt is already close to the Nature Portfolio 5 pt
floor at this figure's 1.00 scale factor.

GATE 3 IS DRAWN DASHED ON PURPOSE and the manuscript caption states why. Gates 1 and 2 are
measured in panels b-f of this figure. Gate 3, decision relevance, is proposed in the Results and
rests on evidence collected to answer other questions (Fig. 4f, Fig. 3h,i), chief among it a
within-patient correlation dominated by a single patient. Drawing it in the same solid style as
the other two would assert an evidential parity this study does not have. It is also joined to
the decision box by a dashed tie rather than an arrowhead, because it is a question asked OF the
ranking rather than another filter the candidate population passes through.

The only text DELETED is the italic "perturbation / predictor" tag on the right-hand arrow, now
just "predictor"; the caption already says the branch carries "candidate populations that are ...
produced by a perturbation predictor", so the word "perturbation" was the redundant half.
"""
import os, matplotlib as mpl, matplotlib.pyplot as plt

# Palette comes from the house-style module; do NOT re-declare the hex values here. Every
# panel file used to carry its own copy, which made figstyle's "one edit here recolours the
# whole deck" untrue: a recolour meant editing 43 files and missing one was silent.
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from figstyle import FOCAL_SOFT, COMP_SOFT, GREY, INK  # noqa: E402
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def draw_5a(ax):
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    def box(x, y, w, h, txt, ec, fc, fs=6.0, tc=None, lw=0.7, ls="solid"):
        # ``fc`` is accepted and ignored: every node is white with a hairline edge. The filled
        # pastel chips this panel used to draw are a slide idiom, and here they also made the
        # heaviest ink in the panel the boxes rather than the flow they contain. Colour survives
        # on the edge and the text, where it still separates the observed branch from the
        # predicted one, and the dashed Gate-3 node still reads as provisional.
        ax.add_patch(mpl.patches.FancyBboxPatch(
            (x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.010,rounding_size=0.014",
            fc="white", ec=ec, lw=lw, ls=ls, zorder=2))
        # Node text is ink by default, not the edge colour it used to inherit. The hairline
        # edge is the coloured mark and it already separates the observed branch from the
        # predicted one; ``tc`` is still honoured where a node needs to be greyed out.
        ax.text(x, y, txt, ha="center", va="center", fontsize=fs,
                color=tc or INK, zorder=3, linespacing=1.25)

    def arrow(x0, y0, x1, y1, c=GREY, lw=0.7):
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0), zorder=1,
                    arrowprops=dict(arrowstyle="-|>", lw=lw, color=c,
                                    shrinkA=0, shrinkB=0, mutation_scale=7))

    # Vertical budget, in axes units against a 1.42 in tall slot. A line of 5.8 pt text at
    # linespacing 1.25 is 0.0709, and boxstyle pad adds 0.020 to every box, so a two-line box
    # occupies 0.142 of visual height and a one-line box 0.075. Six boxes (0.075 + 0.142 + 0.142
    # + 0.142 + 0.075 + 0.142), four arrow gaps (0.060 + 0.065 + 0.060 + 0.055) and one 0.030 tie
    # sum to 0.988 of the 1.0 available. An arrow gap below 0.055 is shorter than its own 7 pt
    # arrowhead and reads as a blob, which is why the gates were rewrapped to two lines rather
    # than the gaps closed.

    # --- the query -------------------------------------------------------------------------
    box(0.50, 0.9625, 0.46, 0.055, "held-out query", GREY, "white", fs=5.8)
    # Label the predicted branch in the empty top-right corner. The query box is narrow enough
    # (x 0.27-0.73) that this clears it horizontally, which is why it is not beside its own box.
    ax.text(0.995, 0.930, "predictor", ha="right", va="center",
            fontsize=5.5, color=INK, style="italic")

    # --- the two kinds of candidate population ---------------------------------------------
    arrow(0.50, 0.935, 0.28, 0.862)
    arrow(0.50, 0.935, 0.72, 0.862)
    box(0.25, 0.794, 0.46, 0.122, "observed\npopulations", FOCAL_SOFT, "#eaf1f8", fs=5.8)
    box(0.75, 0.794, 0.46, 0.122, "predicted\npopulations", COMP_SOFT, "#fbeee0", fs=5.8)

    # --- the two measured gates -------------------------------------------------------------
    arrow(0.25, 0.733, 0.40, 0.655, c=FOCAL_SOFT)
    arrow(0.75, 0.733, 0.60, 0.655, c=COMP_SOFT)
    box(0.50, 0.587, 0.96, 0.122,
        "Differential response: do\nsubpopulations respond differently?", INK, "#f2f2f2", fs=5.8)
    arrow(0.50, 0.526, 0.50, 0.450, c=INK)
    box(0.50, 0.385, 0.96, 0.122,
        "Recoverability: can that\nstructure be identified?", INK, "#f2f2f2", fs=5.8)
    arrow(0.50, 0.324, 0.50, 0.252, c=INK)

    # --- the decision, and the condition asked OF the decision -------------------------------
    box(0.50, 0.2215, 0.80, 0.055, "rank: distributional vs mean", GREY, "white", fs=5.8)
    # Dashed tie, not an arrow: Gate 3 is a question asked of this ranking, not a further filter
    # the candidate population passes through. Dashed edge and grey ink mark it as proposed here
    # rather than measured, as the two gates above are (see module docstring and the caption).
    ax.plot([0.50, 0.50], [0.194, 0.154], ls=(0, (1.6, 1.4)), lw=0.9, color=GREY, zorder=1)
    box(0.50, 0.083, 0.96, 0.122,
        "Decision relevance (proposed):\ndoes it change the ranking?", GREY, "white", fs=5.8, ls="--")


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(1.33, 1.42))   # the slot it occupies in fig5_assemble
    draw_5a(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "5a.png"), dpi=200, bbox_inches="tight")
    print("wrote 5a.png")
