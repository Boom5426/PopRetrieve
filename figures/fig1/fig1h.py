"""PopRetrieve Figure 1 panel 1h: population scoring is itself a continuum.

WHAT THE PANEL HAS TO SAY, AND WHY IT IS TWO AXES
-------------------------------------------------
The measured object is a monotone curve of the interpolated distance against a temperature, and
a reader who meets it cold reads "a parameter was swept". That is not the claim. The claim is
about what the temperature DECIDES: whether the score averages the discrepancy over every
response state, or reports the single worst-matched one. Those are two different questions about
a drug, and they sit at the two ends of one score family rather than in two method classes.

So the intuition is drawn, not described. The cartoon strip holds four query subpopulations that
one candidate matches (three well, one badly) and shows the weight each state receives in the two
regimes; the curve underneath shows that the measured aggregate really does travel between those
two regimes, and lands on the analytic endpoints at both ends.

One direction runs through both axes: mean aggregation is orange and sits low and left,
worst-state emphasis is blue and sits high and right. That holds for the pair of bars inside
every state's column, for the order of the key beneath them, and for the curve, which starts on
the orange rule at low temperature and ends on the blue one at high temperature. The strip names
the two regimes and the curve names the two temperatures that produce them, so the same two
phrases carry the reader from the cartoon into the measurement.

DATA
----
results/exp06_theory_limits/beta_interpolation.csv. Nothing here is typed in: the two dashed
rules are the file's own ``mean`` and ``max`` columns, the y ticks are those same two numbers,
and the axis window is solved from them so the rules land where the layout wants them.

The file's first and last rows carry beta = 1e-9 and 1e9, and their D_beta equals the mean and
the max EXACTLY. They are the analytic limits written as rows, not measurements: plotting them
would ask a log axis to span eighteen decades to show two points that are already on the page as
the dashed rules. They are therefore identified by that exact equality (not by a hard-coded beta
cut), asserted to be the first and last rows, and drawn as the rules.

The K = 1 line at the foot is a second, separate identity, from degenerate_limit_real.csv. It is
checked against the file before it is drawn, because the sentence asserts an exact equality and a
panel must not assert one the data has stopped showing.

A NOTE ON PT_EQ, RESOLVED 2026-08-31
-----------------------------------------------------------
This panel names its y axis in words rather than as "$D_\\beta$", and the reason survived being
re-tested. Mathtext renders a sub/superscript at 0.7x, an axis label is set at PT_ANNOT (7.2), and
7.2 x 0.7 = 5.04 pt, well under this figure's 6.5 pt floor. Correcting PT_EQ from 9.0 to 9.3 on
2026-08-31 did not help: the rule is that any label carrying mathtext goes at PT_EQ, and a 9.3 pt
y label would be the largest in the figure and half again the size of panel g's, which sits
directly beside it. The caption carries the symbol instead. Everything else here has no
sub/superscript: "$\\beta$" and the two limit arrows print at PT_EQ in full.

Run standalone: python fig1h.py
"""
from __future__ import annotations

import csv
import os
import re
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig1_style import (FAINT, LW_HAIR, LW_LINE, MEAN, POP, PT_ANNOT, PT_EQ,  # noqa: E402
                        PT_SMALL, SHARED, TEXT, blank, cells)

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(os.path.dirname(os.path.dirname(HERE)), "results", "exp06_theory_limits")
BETA_CSV = os.path.join(RESULTS, "beta_interpolation.csv")
DEGEN_CSV = os.path.join(RESULTS, "degenerate_limit_real.csv")

# ---------------------------------------------------------------------------------- cartoon
# One column per query subpopulation, shared by the population glyph, its number and its two
# weight bars, so "state 4" is a vertical reading rather than something the caption has to say.
N_STATE = 4
COL_PITCH = 0.240
COL_X = np.array([0.5 + (i - (N_STATE - 1) / 2) * COL_PITCH for i in range(N_STATE)])
CLOUD_RX, CLOUD_N = 0.072, 15
CLOUD_AR = 0.896                 # x spans 0.896 in and y 1.00 in, so ry is scaled to stay round
# The candidate is drawn as a BAND rather than a line. Three states falling inside it and one
# sitting clear above it is a containment judgement, which needs no scale and no second glance;
# the same states strung along a line read as four points at four heights.
BAND_LO, BAND_HI = 0.666, 0.804
CY_OK, CY_BAD = 0.735, 0.928
Y_NUM = 0.650                    # state numbers, hung under the populations they name
BAR_BASE, BAR_FULL = 0.395, 0.140   # a track is one unit of weight, so the four sum to one track
TRACK_W, BAR_W, BAR_DX = 0.170, 0.075, 0.045
# Two key rows, left aligned, one swatch each. Side by side they do not fit: "aggregation" and
# "emphasis" together leave 0.007 in between them at 0.896 in and read as one run of letters.
Y_KEY_MEAN, Y_KEY_WORST = 0.345, 0.205
SWATCH, SWATCH_GAP = 0.040, 0.022

# ---------------------------------------------------------------------------------- curve
# The two rules are pinned to these heights and the y window is solved backwards from them, so
# the band under the mean rule is a reserved text band rather than whatever the data left over.
F_MEAN, F_MAX = 0.315, 0.955
X_PAD = 1.6                      # one factor, applied in log space to both ends
DASH = (0, (2.6, 1.6))
EQ_FRAC = 0.067                  # one PT_EQ line, as a fraction of the 1.95 in curve axes


def _beta_interpolation():
    """(finite betas, their D_beta, the mean endpoint, the max endpoint) from the measured file."""
    with open(BETA_CSV, newline="") as fh:
        rows = list(csv.DictReader(fh))
    beta = np.array([float(r["beta"]) for r in rows])
    dist = np.array([float(r["D_beta"]) for r in rows])
    mean_col = np.array([float(r["mean"]) for r in rows])
    max_col = np.array([float(r["max"]) for r in rows])
    if np.ptp(mean_col) or np.ptp(max_col):
        raise ValueError(f"{BETA_CSV}: mean/max are the analytic endpoints and must be constant "
                         f"down the file; got {set(mean_col)} and {set(max_col)}.")
    lo, hi = float(mean_col[0]), float(max_col[0])

    at_limit = (dist == lo) | (dist == hi)
    if not (at_limit[0] and at_limit[-1] and at_limit.sum() == 2):
        raise ValueError(f"{BETA_CSV}: expected exactly the first and last rows to sit on the "
                         f"analytic endpoints; rows on a limit: {np.flatnonzero(at_limit)}.")
    return beta[~at_limit], dist[~at_limit], lo, hi


def _k1_identity_holds():
    """True only if coverage at K = 1 equals the global distance in every row of the real file."""
    with open(DEGEN_CSV, newline="") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise ValueError(f"{DEGEN_CSV} is empty; the K = 1 identity has no evidence behind it.")
    return all(float(r["global_energy"]) == float(r["coverage_K1"]) for r in rows)


def _key_row(ax, y, colour, words):
    """One legend row: a coloured mark, then the phrase in ink. Letters never carry the colour."""
    ax.add_patch(mpl.patches.Rectangle((0.005, y - 0.055), SWATCH, SWATCH, facecolor=colour,
                                       edgecolor="none", zorder=3))
    # PT_SMALL, not PT_ANNOT: "worst-state emphasis" is 0.97 in at 7.2 pt against a 0.896 in
    # panel, so PT_ANNOT would break it into three lines and spend the strip on a legend. The
    # floor is what it may not go under, and it stops there.
    ax.text(0.005 + SWATCH + SWATCH_GAP, y, words, ha="left", va="top", fontsize=PT_SMALL,
            color=TEXT, linespacing=1.15)


def _cartoon(ax):
    """Four subpopulations, one candidate, and the weight each state gets in the two regimes."""
    blank(ax)
    ry = CLOUD_RX * CLOUD_AR

    # ---- the query, and how well the candidate matches each of its states ----
    # FAINT at part opacity, because at full strength a band this size is the heaviest ink in
    # the strip and the populations inside it stop being the thing the eye lands on.
    ax.add_patch(mpl.patches.Rectangle((0.02, BAND_LO), 0.96, BAND_HI - BAND_LO, facecolor=FAINT,
                                       edgecolor="none", alpha=0.55, zorder=1))
    ax.text(0.005, 1.0, "state mismatch", ha="left", va="top", fontsize=PT_ANNOT, color=TEXT)

    for i, cx in enumerate(COL_X):
        cy = CY_BAD if i == N_STATE - 1 else CY_OK
        if cy - ry > BAND_HI:                       # only a state OUTSIDE the band has a gap
            ax.plot([cx, cx], [BAND_HI, cy - ry], lw=LW_HAIR, color=SHARED, zorder=2)
        # A separate stream per state, so four populations drawn by one helper do not read as
        # four copies of one population.
        cells(ax, cx, cy, CLOUD_N, CLOUD_RX, ry, color=SHARED,
              rng=np.random.default_rng(11 + i), s=3.4, alpha=0.9)
        ax.text(cx, Y_NUM, str(i + 1), ha="center", va="top", fontsize=PT_ANNOT, color=TEXT)

    # ---- what the temperature does to the weights ----
    # One track per state, and the track is one whole unit of weight, so "a quarter each" and
    # "all of it on state 4" are read off the same scale instead of two.
    w_mean = np.full(N_STATE, 1.0 / N_STATE)
    w_worst = np.zeros(N_STATE)
    w_worst[-1] = 1.0
    ax.bar(COL_X, BAR_FULL, TRACK_W, bottom=BAR_BASE, color=FAINT, lw=0, zorder=2, alpha=0.55)
    for dx, weights, colour in ((-BAR_DX, w_mean, MEAN), (BAR_DX, w_worst, POP)):
        ax.bar(COL_X + dx, weights * BAR_FULL, BAR_W, bottom=BAR_BASE, color=colour, lw=0,
               zorder=3)

    _key_row(ax, Y_KEY_MEAN, MEAN, "mean aggregation")
    _key_row(ax, Y_KEY_WORST, POP, "worst-state\nemphasis")


def _curve(ax, beta, dist, lo, hi):
    """The measured interpolation, between the two endpoints it is asserted to reach."""
    span = (hi - lo) / (F_MAX - F_MEAN)
    y_lo = lo - F_MEAN * span
    ax.set_ylim(y_lo, y_lo + span)
    ax.set_xscale("log")
    ax.set_xlim(beta.min() / X_PAD, beta.max() * X_PAD)

    ax.axhline(lo, color=MEAN, lw=LW_HAIR, ls=DASH, zorder=2)
    ax.axhline(hi, color=POP, lw=LW_HAIR, ls=DASH, zorder=2)
    ax.plot(beta, dist, color=POP, lw=LW_LINE, marker="o", ms=2.3, mfc=POP, mec="white",
            mew=0.35, zorder=4)

    # Each rule is named twice, by the temperature that produces it and by what that temperature
    # does. The limits live here rather than in the strip above: at 0.896 in the strip cannot
    # hold both the two phrases and the two limits, and here they cost the empty top-left corner.
    for y_top, token, phrase in ((F_MAX - 0.012, r"$\beta \rightarrow \infty$", "worst case"),
                                 (F_MEAN - 0.012, r"$\beta \rightarrow 0$", "mean aggregation")):
        ax.text(0.0, y_top, token, transform=ax.transAxes, ha="left", va="top", fontsize=PT_EQ,
                color=TEXT)
        ax.text(0.0, y_top - EQ_FRAC, phrase, transform=ax.transAxes, ha="left", va="top",
                fontsize=PT_ANNOT, color=TEXT)

    ax.set_yticks([lo, hi])
    ax.set_yticklabels([f"{lo:.3f}", f"{hi:.3f}"])
    ax.set_xticks([0.1, 1, 10, 100])
    # Written out rather than left to LogFormatter, which sets the decades as mathtext
    # superscripts: at PT_TICK those print at 4.76 pt, under this figure's floor.
    ax.set_xticklabels(["0.1", "1", "10", "100"])
    ax.xaxis.set_minor_locator(mpl.ticker.NullLocator())
    ax.tick_params(axis="both", pad=1.8)
    ax.set_xlabel(r"temperature $\beta$", fontsize=PT_EQ, labelpad=2.0)
    # WORDS, NOT THE SYMBOL, AND THIS WAS RE-DERIVED THE HARD WAY. Putting "$D_\beta$" here
    # was tried on 2026-08-31 after PT_EQ was corrected to 9.3, and the figure's own floor gate
    # rejected it: an axis label is set at PT_ANNOT (7.2), the rule is that ANY label carrying
    # mathtext goes at PT_EQ, and 7.2 x 0.7 = 5.04 pt. Setting the axis label at PT_EQ instead
    # would make it the largest y label in the figure and half again the size of panel g's,
    # which sits directly beside it. So the axis is named in words and the caption carries the
    # symbol, which is the one place the translation costs the reader nothing.
    ax.set_ylabel("interpolated distance", fontsize=PT_ANNOT, labelpad=2.0)
    # The left spine spans the family, from the mean endpoint to the worst one, so the band that
    # holds the K = 1 line reads as text under the plot rather than as unused axis.
    ax.spines["left"].set_bounds(lo, hi)

    if _k1_identity_holds():
        ax.text(0.0, 0.008, "K = 1: coverage\nreduces exactly to\nthe global distance",
                transform=ax.transAxes, ha="left", va="bottom", fontsize=PT_SMALL, color=TEXT,
                linespacing=1.15)
    else:
        raise ValueError(
            f"{DEGEN_CSV}: coverage_K1 no longer equals global_energy, so panel h may not state "
            f"the identity. Drop the line from the panel rather than softening its wording.")


def draw_1h(ax, ax_top):
    """Panel h: the population score is a continuum, and beta says what it aggregates over."""
    beta, dist, lo, hi = _beta_interpolation()
    _cartoon(ax_top)
    _curve(ax, beta, dist, lo, hi)


# ------------------------------------------------------------------------------------------
# Preview and self-check
# ------------------------------------------------------------------------------------------
# Mirrors the geometry fig1_assemble gives a DATA panel: the axes themselves are the sizes the
# composite hands panel h, and the margins are the gutters it reserves around them (LETTER_GUTTER
# + Y_FURNITURE on the left for the y axis, DATA_BELOW under the curve for the x axis). Written
# out rather than imported, because importing fig1_assemble pulls in every other panel module.
AX_W, CARTOON_H, CARTOON_GAP, CURVE_H = 0.896, 1.00, 0.20, 1.95
PAD_L, PAD_R, PAD_T, PAD_B = 0.44, 0.08, 0.10, 0.55

_SUBSUP = re.compile(r"\$[^$]*[\^_][^$]*\$")   # fig1_assemble's rule, applied before it is asked


def _effective_sizes(fig):
    """(effective pt, string) for every drawn Text, a mathtext sub/superscript at its real 0.7x."""
    out = []
    for t in fig.findobj(mpl.text.Text):
        s = str(t.get_text())
        if not s.strip() or not t.get_visible():
            continue
        out.append((t.get_fontsize() * (0.7 if _SUBSUP.search(s) else 1.0), s.replace("\n", "/")))
    return out


def _overhangs(ax, renderer, label):
    """Print how far each artist leaves `ax`, in inches. Axis furniture is reported separately."""
    box = ax.get_window_extent(renderer)
    dpi = ax.figure.dpi
    content, furniture = [], []
    for art in ax.get_children():
        if isinstance(art, mpl.spines.Spine) or art is ax.patch:
            continue
        if not art.get_visible() or (art in (ax.xaxis, ax.yaxis) and not ax.axison):
            continue      # a blank() strip draws no axis, whatever its tick artists still claim
        bb = art.get_tightbbox(renderer)
        if bb is None or bb.width <= 0:
            continue
        out = max((box.x0 - bb.x0) / dpi, (bb.x1 - box.x1) / dpi,
                  (box.y0 - bb.y0) / dpi, (bb.y1 - box.y1) / dpi)
        row = (out, f"{label}: {type(art).__name__} "
                    f"{getattr(art, 'get_text', lambda: '')()!r}".strip())
        (furniture if art in (ax.xaxis, ax.yaxis) else content).append(row)
    return content, furniture


if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
    from figstyle import apply_style, pin_canvas, soften_axes  # noqa: E402
    from fig1_style import PT_FLOOR, PT_TICK, PT_TITLE  # noqa: E402

    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    figw = PAD_L + AX_W + PAD_R
    figh = PAD_T + CARTOON_H + CARTOON_GAP + CURVE_H + PAD_B
    fig = plt.figure(figsize=(figw, figh))
    pin_canvas(fig)                       # the canvas is the page, so "tight" cannot rescale it
    ax_top = fig.add_axes([PAD_L / figw, 1 - (PAD_T + CARTOON_H) / figh, AX_W / figw,
                           CARTOON_H / figh])
    ax = fig.add_axes([PAD_L / figw, PAD_B / figh, AX_W / figw, CURVE_H / figh])
    draw_1h(ax, ax_top)
    soften_axes(fig)

    for a, want in ((ax, (AX_W, CURVE_H)), (ax_top, (AX_W, CARTOON_H))):
        got = (a.get_position().width * figw, a.get_position().height * figh)
        assert np.allclose(got, want, atol=1e-9), f"axes is {got}, composite gives it {want}"

    fig.canvas.draw()                     # every tick label exists only once the figure is drawn
    rend = fig.canvas.get_renderer()

    smallest = min(_effective_sizes(fig))
    assert smallest[0] >= PT_FLOOR - 1e-6, f"below the {PT_FLOOR} pt floor: {smallest}"
    print(f"smallest effective size {smallest[0]:.2f} pt  ({smallest[1]!r})")

    content, furniture = [], []
    for a, name in ((ax_top, "strip"), (ax, "curve")):
        c, f = _overhangs(a, rend, name)
        content += c
        furniture += f
    outside = [r for r in content if r[0] > 1e-4]
    for out, who in sorted(furniture, reverse=True):
        print(f"axis furniture leaves the axes by {out:+.3f} in  {who}  "
              f"(composite reserves {PAD_L:.2f} in left, {PAD_B:.2f} in below)")
    for out, who in sorted(outside, reverse=True):
        print(f"HANGS OUT by {out:.4f} in  {who}")
    assert not outside, "panel content must stay inside its axes; see the list above"
    print("all panel content is inside its axes")

    fig.savefig(os.path.join(HERE, "1h.png"), dpi=400)
    print("wrote 1h.png")
