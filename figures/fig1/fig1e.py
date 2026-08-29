"""PopRetrieve Figure 1 panel 1e: what makes an evaluator independent of the score it grades.

Schematic (no external data). It states the manuscript's sharpest structural claim about
retrieval evaluation: the candidate is chosen by MAXIMIZING a score, and an objective-aligned
metric then measures that same score's ground truth on those same candidates, so the ranking
function and the evaluation function are one function evaluated once, with no estimation error
to expose and no way to lose. A more independent judge can overturn the ranking; a coupled one
cannot.

The claim is carried by a shape contrast: a CLOSED loop for the coupled case, an OPEN chain that
ends in two possible verdicts for the independent case.

Design notes (presentation only, no data involved):
  * No boxes and no fills. The nodes were filled, rounded, coloured cards; that is a slide idiom,
    and at this panel's size the fills were also the heaviest ink in a panel whose argument is a
    line shape. Text sits directly on the canvas, delimited by whitespace, and the only strokes
    are the connectors themselves.
  * No hue. This panel is drawn in ink and grey alone, and that is a correctness fix rather than a
    taste one: the deck's two hues are defined in figstyle as FOCAL_SOFT = distributional/population
    signal and COMP_SOFT = mean/collapse. Coupled-versus-independent evaluation is a different
    distinction entirely, so painting the coupled case orange and the independent judge blue gave
    both hues a second, contradictory meaning inside the same figure. Panels a-d use colour where
    it means what the palette says it means; e and f do not need it and no longer claim it.
  * Weight is structural only. Section labels are bold because they name the two halves of the
    panel; the conclusions ("the gain cannot be overturned") are set plain, because bolding a
    conclusion is emphasis, not information, and the panel already has too much of it.

Run standalone: python fig1e.py
"""
import os

import matplotlib as mpl
import matplotlib.pyplot as plt

GREY, INK = "#7A7A7A", "#1A1A1A"
HAIRLINE = "#DCDCDC"

Y_COUPLED, Y_SPLIT, Y_CHAIN = 0.760, 0.470, 0.205


def _edges(ax, artist):
    """(left, right) x of a drawn Text, in data coordinates."""
    fig = ax.figure
    fig.canvas.draw()
    bb = artist.get_window_extent(renderer=fig.canvas.get_renderer())
    inv = ax.transData.inverted()
    return inv.transform((bb.x0, 0))[0], inv.transform((bb.x1, 0))[0]


def _left_edge(ax, artist):
    return _edges(ax, artist)[0]


def _right_edge(ax, artist):
    return _edges(ax, artist)[1]


def _arrow(ax, p0, p1, color=INK, lw=0.7, rad=0.0, z=4, ms=6):
    ax.add_patch(mpl.patches.FancyArrowPatch(
        p0, p1, arrowstyle="-|>", mutation_scale=ms, lw=lw, color=color, zorder=z,
        connectionstyle=f"arc3,rad={rad}"))


def draw_1e(ax):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # ============ upper half: a closed loop ============
    ax.text(0.0, 0.960, "Coupled evaluation", ha="left", va="center",
            fontsize=6.4, color=INK, fontweight="bold")
    ax.text(1.0, 0.960, "response matching", ha="right", va="center", fontsize=5.8, color=GREY)

    left = ax.text(0.175, Y_COUPLED, "retrieval score\nranks the candidates", ha="center",
                   va="center", fontsize=6.0, color=INK, linespacing=1.25)
    right = ax.text(0.820, Y_COUPLED, "evaluation metric\ngrades that ranking", ha="center",
                    va="center", fontsize=6.0, color=INK, linespacing=1.25)
    # The loop closes between the two nodes, so its endpoints have to clear the text they attach
    # to. They are read off the drawn extents rather than guessed: the guessed version put the
    # lower arrowhead on top of "ranks the candidates".
    x_l, x_r = _right_edge(ax, left) + 0.028, _left_edge(ax, right) - 0.028
    _arrow(ax, (x_l, Y_COUPLED + 0.030), (x_r, Y_COUPLED + 0.030), rad=-0.42)
    _arrow(ax, (x_r, Y_COUPLED - 0.030), (x_l, Y_COUPLED - 0.030), rad=-0.42)

    # The mechanism ("one function, evaluated once" / "two functions, evaluated separately") is
    # in the caption; the panel keeps only the consequence, which is what the loop and the open
    # chain are drawn to show.
    ax.text(0.500, 0.572, "the gain cannot be overturned", ha="center", va="center",
            fontsize=5.8, color=INK)

    ax.plot([0.0, 1.0], [Y_SPLIT, Y_SPLIT], lw=0.5, color=HAIRLINE, zorder=1)

    # ============ lower half: an open chain with two ends ============
    ax.text(0.0, 0.385, "Independent evaluation", ha="left", va="center",
            fontsize=6.4, color=INK, fontweight="bold")
    ax.text(1.0, 0.385, "biological / functional", ha="right", va="center",
            fontsize=5.8, color=GREY)

    ax.text(0.088, Y_CHAIN, "the same\nranking", ha="center", va="center", fontsize=6.0,
            color=INK, linespacing=1.25)
    _arrow(ax, (0.178, Y_CHAIN), (0.258, Y_CHAIN), color=GREY)
    ax.text(0.400, Y_CHAIN, "outside judge\nMoA, viability", ha="center", va="center",
            fontsize=6.0, color=INK, linespacing=1.25)
    _arrow(ax, (0.545, Y_CHAIN + 0.026), (0.660, Y_CHAIN + 0.088), color=GREY, rad=-0.14)
    _arrow(ax, (0.545, Y_CHAIN - 0.026), (0.660, Y_CHAIN - 0.088), color=GREY, rad=0.14)
    ax.text(0.676, Y_CHAIN + 0.094, "confirmed", ha="left", va="center", fontsize=6.0, color=INK)
    ax.text(0.676, Y_CHAIN - 0.094, "overturned", ha="left", va="center", fontsize=6.0, color=INK)

    # deliberately parallel to the line above the rule, so the contrast is read as one sentence
    # with one word changed rather than as two unrelated captions
    ax.text(0.500, 0.040, "the gain can fail", ha="center", va="center",
            fontsize=5.8, color=INK)


if __name__ == "__main__":
    # Same axes geometry the composite gives this panel, so a position tuned here is correct there.
    fig, ax = plt.subplots(figsize=(2.610, 1.639))
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    draw_1e(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "1e.png"), dpi=300)
    print("wrote 1e.png")
