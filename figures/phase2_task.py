"""The Phase-II intervention-retrieval task, drawn once and used by Figures 5 and 6.

WHY ONE MODULE AND NOT TWO PANELS
----------------------------------
Figure 5 measures the task with candidate responses OBSERVED; Figure 6 measures the same task with
them PREDICTED. That is the only difference between the two pages, and it has to be the only
difference between the two schematics, or a reader comparing them cannot tell which contrasts are
the experiment and which are the drawing. So the two panels are one function with one switch: same
station centres, same box sizes, same arrows, same ranking card, same seeded clouds. ``mode``
changes exactly two things, the third station and the rule beneath it, and ``draw_task`` asserts
that it was given one of the two.

WHAT THE PANEL HAS TO SAY, IN BOTH MODES
-----------------------------------------
Every earlier version of this figure could be read as response matching: retrieve the drug whose
observed response looks most like a query response. It is not that task. The retriever is given a
held-out cell line's untreated cells and a desired treated population, and must rank all 92
compounds by how well each carries one into the other. The distinction decides what the rest of
both figures means, and no measured quantity states it, so it is drawn.

THE TWO-BRANCH FLOW, AND THE SENTENCE IT REPLACES
--------------------------------------------------
An earlier draft drew one left-to-right chain ending at the target, under the line "no observed
treated response from the held-out line reaches the predictor or the ranker". That sentence is
false as written, and the layout is what made it easy to write. The target IS an observed treated
population from the held-out line, and it MUST reach the ranker: it is the query. What may not
appear in the predicted mode is any observed response of a CANDIDATE drug in that line, which is
the whole content of the leave-one-cell-line-out rule.

The flow is therefore drawn as two branches that converge on the scorer. The upper branch carries
the candidates; the observed branch carries the target and joins only at the matching step. Read
off the figure, the rule is a property of the arrows rather than a claim under them.

Nothing here is measured. The clouds are seeded draws and the three ranked names are illustrative;
``draw_task`` asserts that the only digits it prints are the two the task freeze fixes, the 92
compounds and the 43 fitted lines, so no result can arrive on a schematic.

LAYOUT NOTE
-----------
Captions sit directly beneath their own stage on one baseline per branch, so no two labels share a
band. Stage centres are far enough apart that a caption line may run to about eleven characters;
the full wording is in the legend.
"""
import os as _os
import sys as _sys

import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from phase2_style import INK, MEAN, POP, PT_SMALL, SHARED, TISSUE  # noqa: E402

TOP, BOT = 0.780, 0.300           # the two branch centres
CAP_TOP = 0.640                   # one caption baseline for the candidate branch
H = 0.220                         # common box height

# The two counts the task freeze fixes, and the only digits either mode may print.
N_DRUGS, N_FIT_LINES = 92, 43

# The one station that differs, and the one line beneath the panel that differs with it.
def _wash(colour, frac):
    """``colour`` at ``frac`` strength against white, as a hex.

    The predictor box is derived from the active POP colour at a low opacity rather than typed as
    a second blue. That keeps the light fill in step with the Figure 1 reference palette if the
    family colour changes later.
    """
    import matplotlib.colors as mcolors

    rgb = mcolors.to_rgb(colour)
    return mcolors.to_hex(tuple(frac * v + (1.0 - frac) for v in rgb))


STATION = {
    "oracle": dict(edge=SHARED, fill="white", text="observed\nresponses",
                   caption="held-out\nline"),
    "predicted": dict(edge=POP, fill=_wash(POP, 0.055), text="forward\npredictor",
                      caption=f"fitted on\n{N_FIT_LINES} lines"),
}
RULE = {
    "oracle": "candidate outcomes in the held-out line are observed, not predicted;\n"
              "the target population is given to the scorer only",
    "predicted": "candidate outcomes in the held-out line are predicted, not observed;\n"
                 "the target population is given to the scorer only",
}


def _cloud(ax, rng, cx, cy, n, spread, colour, elong=1.0, tilt=0.0):
    a = rng.normal(0, spread * elong, n)
    b = rng.normal(0, spread, n)
    ax.scatter(cx + a * np.cos(tilt) - b * np.sin(tilt),
               cy + a * np.sin(tilt) + b * np.cos(tilt),
               s=1.5, color=colour, lw=0, alpha=0.8, zorder=3)


def _box(ax, x, y, w, h, colour, fc="white"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.004,rounding_size=0.02",
                                lw=0.8, ec=colour, fc=fc, zorder=2))


def _arrow(ax, p0, p1, colour=SHARED, lw=0.9, rad=0.0):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", lw=lw, color=colour,
                                 mutation_scale=7, shrinkA=0, shrinkB=0, zorder=4,
                                 connectionstyle=f"arc3,rad={rad}"))


def _cap(ax, x, y, txt, colour=INK):
    ax.text(x, y, txt, ha="center", va="top", fontsize=PT_SMALL, color=colour, linespacing=1.1)


def draw_task(ax, mode):
    """Draw the task into ``ax``. ``mode`` is "oracle" or "predicted"; nothing else is drawn."""
    if mode not in STATION:
        raise ValueError(f"draw_task takes mode 'oracle' or 'predicted', not {mode!r}; the two "
                         f"figures differ by this switch and by nothing else.")
    rng = np.random.default_rng(11)   # seeded: illustrative, identical on every run and in both modes
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    MID = (TOP + BOT) / 2

    # ================= candidate branch: where the two modes differ ===========================
    _box(ax, 0.005, TOP - H / 2, 0.100, H, SHARED)
    _cloud(ax, rng, 0.055, TOP, 65, 0.024, SHARED)
    _cap(ax, 0.055, CAP_TOP, "source\nuntreated")

    _box(ax, 0.135, TOP - H / 2, 0.090, H, SHARED)
    for i, lab in enumerate((f"drug 1", ".\n.\n.", f"drug {N_DRUGS}")):
        ax.text(0.180, TOP + 0.068 - i * 0.068, lab, ha="center", va="center",
                fontsize=PT_SMALL, color=INK, linespacing=0.55)
    _cap(ax, 0.180, CAP_TOP, f"{N_DRUGS} drugs\nfixed")

    st = STATION[mode]
    _box(ax, 0.255, TOP - H / 2, 0.120, H, st["edge"], fc=st["fill"])
    ax.text(0.315, TOP, st["text"], ha="center", va="center",
            fontsize=PT_SMALL, color=INK, linespacing=1.1)
    _cap(ax, 0.315, CAP_TOP, st["caption"])

    for i, cx in enumerate((0.442, 0.470, 0.498)):
        _cloud(ax, rng, cx, TOP - 0.018 + 0.020 * i, 28, 0.018, POP, elong=1.0 + 0.6 * i,
               tilt=0.5 * i)
    _cap(ax, 0.470, CAP_TOP, "candidate\npopulations")

    # ================= observed branch: the query, which is allowed and required ==============
    _box(ax, 0.390, BOT - H / 2, 0.105, H, TISSUE)
    _cloud(ax, rng, 0.4425, BOT, 65, 0.022, TISSUE, elong=1.9, tilt=0.5)
    # Labelled to its LEFT, not below: the band below it carries the rule, and the whole left
    # half of this branch's row is empty because the candidate branch sits a row above.
    # Ink. The box it names is drawn with a TISSUE edge one glyph away, so the edge is already
    # carrying the hue; the letters therefore stay in dark ink rather than reusing the softened
    # tissue colour as a small text colour.
    ax.text(0.378, BOT, "target\nwanted state", ha="right", va="center",
            fontsize=PT_SMALL, color=INK, linespacing=1.1)

    # ================= the two branches meet at the scorer, and only there ====================
    _box(ax, 0.578, MID - H / 2, 0.120, H, SHARED)
    ax.text(0.638, MID, "response\nmatching", ha="center", va="center",
            fontsize=PT_SMALL, color=INK, linespacing=1.1)

    _box(ax, 0.733, MID - 0.150, 0.150, 0.300, SHARED)
    # THE RANKING IS NOT COLOURED, and it used to be. Rank 1 was set in MEAN orange and rank 3 in
    # POP blue. Blue at least meant something, it marked the correct answer, but the softened blue
    # is intentionally not used as a small text colour. Orange meant nothing at all: this
    # schematic draws ONE scorer and ONE ranking, so there is no mean route for a mean-level hue
    # to belong to, and "drug 47" is a filler entry sitting above the true one. Spending the
    # deck's mean-signature colour on a filler is how a hue stops meaning anything.
    #
    # The true drug stays bold, which is the channel that was doing the work.
    for i, (r, nm, bold) in enumerate((("1", "drug 47", False), ("2", "drug 12", False),
                                       ("3", "true drug", True), (".\n.\n.", "", False))):
        y = MID + 0.108 - i * 0.068
        ax.text(0.760, y, r, ha="center", va="center", fontsize=PT_SMALL, color=SHARED,
                linespacing=0.55)
        if nm:
            ax.text(0.836, y, nm, ha="center", va="center", fontsize=PT_SMALL,
                    color=INK if bold else SHARED,
                    fontweight="bold" if bold else "normal")
    _cap(ax, 0.808, MID - 0.165, "drug ranking")

    # ---- flow ----
    _arrow(ax, (0.105, TOP), (0.133, TOP))
    _arrow(ax, (0.225, TOP), (0.253, TOP))
    _arrow(ax, (0.375, TOP), (0.424, TOP))
    _arrow(ax, (0.520, TOP - 0.012), (0.576, MID + 0.050), rad=-0.18)
    _arrow(ax, (0.497, BOT), (0.576, MID - 0.050), colour=TISSUE, rad=0.18)
    _arrow(ax, (0.698, MID), (0.731, MID))

    # ---- the rule, stated as what it is ----
    # The earlier wording said no observed treated response from the held-out line reaches the
    # predictor or the ranker. The target is exactly that and reaches the ranker by design, so
    # the sentence names CANDIDATE outcomes rather than treated responses in general.
    ax.text(0.5, 0.085, RULE[mode], ha="center", va="center", fontsize=PT_SMALL,
            color=INK, linespacing=1.2)

    # A schematic carries no result. The only digits either mode may print are the two the task
    # freeze fixes; anything else on this panel would be a measurement drawn where it cannot be
    # given its n or its interval.
    allowed = {str(N_DRUGS), str(N_FIT_LINES), "1", "2", "3", "47", "12"}
    for t in ax.texts:
        for tok in "".join(ch if ch.isdigit() else " " for ch in str(t.get_text())).split():
            if tok not in allowed:
                raise AssertionError(
                    f"the task schematic printed {tok!r} in {str(t.get_text())[:40]!r}. It is a "
                    f"schematic: a measured value belongs in a panel that can carry its n.")
    return ax
