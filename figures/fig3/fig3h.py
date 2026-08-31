"""PopRetrieve Figure 3 panel 3h: the Class-C benchmark ladder, and what energy keeps once the
response-magnitude channel is partialled out.

WHAT THIS PANEL CLAIMS
----------------------
Five scores are ranked against ONE external oracle, drug-drug functional similarity, and the
panel makes two statements about them:

  1. Among the scores that compare a perturbation response representation, the distributional
     one leads: energy +0.276 against the pre-specified mean-signature incumbent +0.083. This is
     the only oracle-independent criterion in the study on which the population representation
     wins, and the figure's third skeleton number.
  2. That lead is not a distributional achievement. A query-dependent SCALAR that compares no
     representation at all, preferring candidates whose response magnitude is close to the
     query's, reaches +0.232, and the phrase over the panel says so. Partialling that channel out
     of energy and out of the oracle leaves energy at +0.097, the figure's fourth skeleton number,
     drawn as an arrow leaving the energy dot and landing on a row of its own directly beneath.

The transition is the panel's reason to exist. A reader who takes only the energy dot away from
this panel has taken a stronger claim than the data carry, which is why the dot is not allowed to
sit alone on its row.

SOURCE
------
figures/source_data/fig3hi_class_c_functional.csv, written by
analysis/class_c/class_c_functional_oracle.py. 103 leave-one-drug-out queries, SciPlex3 x GDSC2 at
10 uM, 34 A549, 34 K562, 35 MCF7. Columns drawn, all as COLUMN MEDIANS over the 103 queries:

    energy_rho                     distributional retrieval                          POP, filled
    mean_cosine_ctrl_rho           mean-signature retrieval, control-subtracted      MEAN, filled
    mean_cosine_raw_rho            mean signature, no control subtraction            MEAN, open
    magnitude_match_rho            rank by -|mag(c) - mag(q)|, no representation      EXT, open
    potency_match_rho              rank by -|AUC(c) - AUC(q)|, oracle-side            EXT, open
    energy_rho_partial_magmatch    energy, rank-residualised on magnitude match       POP, diamond

The oracle is Spearman correlation between GDSC2 dose-response AUC profiles across 966 cell lines
with the three SciPlex3 lines held out, double-centred on cell-line mean AUC. It is NOT measured
potency; the absolute-potency scoring of the same rankings is the endpoint audit in panels l and m,
a control rather than a competitor.

THE VOCABULARY, AS APPLIED HERE
-------------------------------
Hue names the family, fill names the role, and the two are independent. POP blue is energy because
energy IS the population-level object and this is a panel where methods are genuinely compared;
MEAN orange is both mean-cosine variants for the same reason; EXT green is the magnitude scalar
and the potency match, which fig3_style names by example. No half-plane wash is drawn: the x axis
carries an alignment with an external oracle, not a signed population-minus-mean advantage, so the
blue/orange half-plane idiom would be a category error here. Zero is drawn as a datum because
rho = 0 is the null of no alignment, not because any value is negative; none is.

JUDGEMENT CALLS A READER COULD REASONABLY DISAGREE WITH
-------------------------------------------------------
1. "mean cosine, raw" SITS UNDER "Simple controls" THOUGH IT DOES RANK CANDIDATES. Every one of
   the five scores produces a candidate ranking, so "performs no retrieval" would be false of any
   of them and is not what the open marker is claimed to mean here. Open means: not one of the two
   methods this study set out to compare. The control-subtracted mean cosine is the pre-specified
   incumbent; the raw variant is a mis-specification kept because it shows what leaks in when the
   control is not subtracted. A reader who wants the raw variant counted as a third method should
   read its dot at the same value either way, +0.241; only the fill changes.
2. "potency match" IS LABELLED A DIAGNOSTIC RATHER THAN A BASELINE. It ranks candidates by the
   query's own GDSC2 viability AUC, information no retriever has, and in this table its column is
   numerically IDENTICAL to oracle_vs_potencymatch_rho; the code asserts that identity. It
   measures whether the oracle re-encodes potency level, so reading its +0.399 as "the best
   method" would be a mistake the grouping exists to prevent.
3. THE INTERVAL IS A QUERY-LEVEL BOOTSTRAP AND IS THEREFORE NOMINAL. 4000-draw seeded percentile
   bootstrap of each column median over the 103 queries. Queries within a cell line share a
   candidate library, so they are not independent and the interval is anticonservative, exactly as
   panel i says of its Wilcoxon. It also UNDERSTATES between-line spread on four of the five rows:
   the per-cell-line medians of potency match run 0.195 to 0.679 against an interval of 0.232 to
   0.457, and energy, raw mean cosine and magnitude match each put one line's median outside their
   own interval too. Only the control-subtracted mean cosine holds all three lines inside it. Those per-line medians are cut to the caption; at 2.66 x 0.84 in, fifteen extra marks
   and an x axis stretched to 0.70 to hold them would cost the transition its legibility.
4. THE PANEL DRAWS COLUMN MEDIANS, SO IT DOES NOT CLAIM A FRACTION REMOVED. Median energy falls
   from +0.276 to +0.097, but the median of the PER-QUERY drop is only +0.053 (95% bootstrap
   +0.007 to +0.122; Wilcoxon p = 1.3e-4, nominal for the same clustering reason), and the partial
   is the higher of the two on 38% of queries. "Most of energy's score is magnitude" would be a
   statement about the difference of two medians read as if it were the median difference, and
   picking that denominator is the error this paper exists to criticise. Neither the title nor any
   drawn label states a ratio.
5. THE PARTIAL LANDS DIRECTLY ABOVE THE INCUMBENT, AND THAT COMPARISON IS NOT LICENSED. +0.097
   is energy after residualisation; every other dot on the panel is unresidualised, and there is
   no partialled mean-cosine column to put beside it, so reading +0.097 against +0.083 sets two
   different quantities side by side. The layout cannot stop a reader trying. The partial has to
   sit under the row it is derived from, mean cosine is the other member of that group, and the
   two therefore print on adjacent rows about 0.014 apart with overlapping intervals: they are
   the closest pair on the panel. An earlier version of this docstring claimed that nothing on
   the panel invited the comparison, which was simply false of what is drawn. What the panel can
   do it does: only the derived row carries a diamond, a grey label and an incoming arrow. The
   caption must state that the two numbers are not commensurable.
6. THE PARTIAL GETS A ROW, WHICH RISKS READING AS A SIXTH COMPETITOR. It was first drawn on the
   energy row itself, where its interval, energy's interval and the connector became three
   overlapping blue horizontals that no reader could separate, and where its label had nowhere
   to go but a band under the title that read as a second title line. It therefore has a row,
   and three things say it is not a method: a diamond rather than a circle, so its marker is not
   one of the circles the filled/open contrast sorts into methods and controls; a label set small
   and grey rather than in ink; and an arrow that starts on the energy dot, so the row is visibly
   derived from the row above rather than measured beside it.
7. THE CONNECTOR IS BOWED HARD RATHER THAN TAKING THE SHORT WAY ROUND. The partial's interval
   reaches well to the RIGHT of its own dot, across the ground a gentle arc would cross, and at
   the curvature this panel first used the connector ran along that interval within a third of a
   printed point. The two blue horizontals merged, the arrowhead read as a feature of the
   interval, and the interval's upper end could not be found at all. ARC_RAD now takes the
   connector down through the gap between the rows, and _arc_clearance_pt asserts printed air
   against every interval it passes over, so a change in the data cannot quietly lay the shaft
   back down on top of a bar.

WHAT WAS CUT INTO THE CAPTION
-----------------------------
The GDSC2 provenance, the per-cell-line medians, the bootstrap and its clustering caveat, the
definition of each score, the fact that open means "not one of the two compared methods", and
the warning that +0.097 and +0.083 are not commensurable because only the first is residualised.

Run standalone: python fig3h.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig3_style import (EXT, LW_HAIR, MEAN, MS_DOT, POP,  # noqa: E402
                        PT_ANNOT, PT_SMALL, REPO, SUBTLE, TEXT, bare_axes, boot_ci, title,
                        zero_rule)

SRC = os.path.join(REPO, "figures", "source_data", "fig3hi_class_c_functional.csv")

N_QUERIES = 103
CELL_LINES = {"A549", "K562", "MCF7"}

# (group tag, [(column, row label, hue, filled), ...]). Rows inside a group are ordered at draw
# time by their own median, descending, so the ladder cannot disagree with the file.
GROUPS = [
    ("Retrieval methods", [("energy_rho", "energy", POP, True),
                           ("mean_cosine_ctrl_rho", "mean cosine", MEAN, True)]),
    ("Simple controls", [("mean_cosine_raw_rho", "mean cosine, raw", MEAN, False),
                         ("magnitude_match_rho", "magnitude match", EXT, False)]),
    ("Diagnostic only", [("potency_match_rho", "potency match", EXT, False)]),
]
ENERGY_COL = "energy_rho"
MEAN_COL = "mean_cosine_ctrl_rho"
SCALAR_COL = "magnitude_match_rho"
POTENCY_COL = "potency_match_rho"
PARTIAL_COL = "energy_rho_partial_magmatch"
# The derived row's label. Set at PT_SMALL in SUBTLE grey, unlike every method label,
# because it names an ADJUSTMENT of the row above rather than a sixth thing to rank.
PARTIAL_LABEL = "after magnitude adjustment"

# The phrase over the panel. It states the comparison the transition does NOT state, and it is
# asserted below: the no-representation scalar must reach at least three quarters of the
# distributional score, and must sit above the mean-signature incumbent.
TITLE_3H = "A scalar control nearly matches energy"
SCALAR_NEAR_FRAC = 0.75

# ------------------------------------------------------------------------------ geometry, inches
# Resolved against the axes' real printed width at draw time, so the ledger in fig3_assemble.py
# stays the single place panel widths are set.
LANE_W = 0.76          # the group-tag lane, right of every datum; holds "Retrieval methods"
LANE_GAP = 0.10        # clear space between the last datum and the lane
ZERO_IN = 0.16         # where rho = 0 sits, in from the axes left edge; far enough in to read
                       # as a datum rather than as a second spine
TOP_Y = 0.845          # centre of the top row, in axes fraction
BOT_Y = 0.075          # centre of the bottom row
VAL_DY = 0.098         # a value label sits this far above its own marker, clear of that row's
                       # interval, of the transition arrow, and of the marker itself: at 0.075
                       # the diamond's top vertex touched the digits of its own label
ARC_RAD = -0.50        # curvature of the energy -> partial connector. Large on purpose; see
                       # judgement call 7. The sign takes the arc DOWN into the gap between the
                       # two rows instead of flattening it along the partial's own interval
ARROW_CLEAR_PT = 1.5   # printed points of air demanded between that arc and any interval bar it
                       # passes over, asserted at draw time
MARKER_SKIP_PT = 4.0   # the arc is trimmed by shrinkA/shrinkB at each end, so clearance is not
                       # measured within this radius of either endpoint


def _arc_clearance_pt(a_in, b_in, rad, bar_y_in, bar_x0_in, bar_x1_in):
    """Least vertical air, in printed points, between an arc3 connector and one interval bar.

    Every argument is inches on the printed page: ``a_in`` and ``b_in`` are the connector's two
    endpoints, ``bar_*`` the horizontal bar it may run along. matplotlib builds
    ``connectionstyle="arc3,rad=r"`` as the quadratic Bezier whose control point is the chord
    midpoint displaced by ``r * (dy, -dx)``; reproducing that here keeps the check independent of
    a renderer, so it can run inside the draw call rather than after a canvas exists.
    """
    (ax_in, ay_in), (bx_in, by_in) = a_in, b_in
    dx, dy = bx_in - ax_in, by_in - ay_in
    cx, cy = 0.5 * (ax_in + bx_in) + rad * dy, 0.5 * (ay_in + by_in) - rad * dx
    t = np.linspace(0.0, 1.0, 2001)
    px = (1 - t) ** 2 * ax_in + 2 * (1 - t) * t * cx + t ** 2 * bx_in
    py = (1 - t) ** 2 * ay_in + 2 * (1 - t) * t * cy + t ** 2 * by_in
    skip = MARKER_SKIP_PT / 72.0
    keep = ((px >= bar_x0_in) & (px <= bar_x1_in)
            & (np.hypot(px - ax_in, py - ay_in) > skip)
            & (np.hypot(px - bx_in, py - by_in) > skip))
    if not keep.any():
        return float("inf")
    return 72.0 * float(np.min(np.abs(py[keep] - bar_y_in)))


def draw_3h(ax):
    if not os.path.exists(SRC):
        raise FileNotFoundError(
            f"{SRC} does not exist. Run analysis/class_c/class_c_functional_oracle.py and export "
            f"the per-query table; this panel will not render placeholder correlations.")
    d = pd.read_csv(SRC)
    if len(d) != N_QUERIES:
        raise ValueError(f"{SRC} holds {len(d)} queries; this panel is written for {N_QUERIES}.")
    if set(d["cell_line"]) != CELL_LINES:
        raise ValueError(f"{SRC} cell lines are {sorted(set(d['cell_line']))}, expected "
                         f"{sorted(CELL_LINES)}.")

    cols = [c for _, members in GROUPS for c, _, _, _ in members] + [PARTIAL_COL]
    med = {c: float(d[c].median()) for c in cols}
    ci = {c: boot_ci(d[c].values) for c in cols}

    # ---- the claims, asserted so no drawn label can outlive the data --------------------------
    assert med[ENERGY_COL] > med[MEAN_COL], (
        "panel h draws energy above the mean-signature incumbent; the file no longer says that "
        f"({med[ENERGY_COL]:+.4f} vs {med[MEAN_COL]:+.4f}).")
    assert (SCALAR_NEAR_FRAC * med[ENERGY_COL] <= med[SCALAR_COL] <= med[ENERGY_COL]
            and med[SCALAR_COL] > med[MEAN_COL]), (
        f"the phrase over this panel says a scalar control NEARLY MATCHES energy, which bounds "
        f"the scalar on BOTH sides: at or above {SCALAR_NEAR_FRAC:.2f} of energy, and not past "
        f"it. The scalar is {med[SCALAR_COL]:+.4f} against energy {med[ENERGY_COL]:+.4f} and "
        f"incumbent {med[MEAN_COL]:+.4f}.")
    assert med[PARTIAL_COL] < med[ENERGY_COL], (
        f"the transition is drawn leftward and downward; the partial is {med[PARTIAL_COL]:+.4f} "
        f"against energy {med[ENERGY_COL]:+.4f}.")
    # The drawn move is between two column medians; its DIRECTION is defended per query, paired.
    paired = boot_ci((d[ENERGY_COL] - d[PARTIAL_COL]).values)
    assert paired[1] > 0.0, (
        f"the per-query drop from energy to the partial no longer excludes zero: {paired}.")
    # The x axis begins AT zero and the bottom spine is cut back to the data, so the panel reads
    # rho = 0 as an untouched null. That is a claim about the file, not a drawing choice: an
    # interval reaching below zero would be clipped by the view rather than shown.
    _worst = min(ci, key=lambda c: ci[c][1])
    assert ci[_worst][1] >= 0.0, (
        f"{_worst} has a lower bound of {ci[_worst][1]:+.4f}. Panel h starts its axis at zero and "
        f"treats zero as an untouched null; a negative bound would be drawn outside the view.")
    # Potency match is a property of the oracle, which is why it is grouped as a diagnostic.
    assert np.allclose(d[POTENCY_COL], d["oracle_vs_potencymatch_rho"]), (
        "potency_match_rho and oracle_vs_potencymatch_rho have diverged; the 'Diagnostic only' "
        "grouping rests on them being the same quantity.")

    # ---- rows: methods ordered inside their group by the medians just computed, and the
    # ---- partial pinned directly under the row it is derived from -----------------------------
    rows, tags = [], []
    for tag, members in GROUPS:
        i0 = len(rows)
        for col, label, hue, filled in sorted(members, key=lambda m: med[m[0]], reverse=True):
            rows.append((col, label, hue, filled, False))
            if col == ENERGY_COL:
                rows.append((PARTIAL_COL, PARTIAL_LABEL, POP, True, True))
        tags.append((tag, i0, len(rows) - 1))
    pitch = (TOP_Y - BOT_Y) / (len(rows) - 1)
    ys = [TOP_Y - pitch * i for i in range(len(rows))]
    assert rows[1][0] == PARTIAL_COL, "the partial must sit on the row under energy."

    # ---- the x mapping, resolved from the axes' real printed width ----------------------------
    axw = ax.get_position().width * ax.figure.get_figwidth()
    assert axw >= 2.30, (f"panel h is {axw:.2f} in wide; the group-tag lane needs about 0.86 in "
                         f"of it and the ladder cannot be read in what is left.")
    data_r = axw - LANE_W - LANE_GAP
    axis_end = float(np.ceil(max(hi for _, _, hi in ci.values()) / 0.02) * 0.02)
    scale = (data_r - ZERO_IN) / axis_end                       # inches per unit of rho
    xlo = -ZERO_IN / scale
    ax.set_xlim(xlo, xlo + axw / scale)
    ax.set_ylim(0.0, 1.0)

    def x_at(inches):
        """Data x of a point ``inches`` in from the axes' left edge."""
        return xlo + inches / scale

    # ---- the connector must not lie down on any interval it crosses ---------------------------
    axh = ax.get_position().height * ax.figure.get_figheight()
    a_in = ((med[ENERGY_COL] - xlo) * scale, ys[0] * axh)
    b_in = ((med[PARTIAL_COL] - xlo) * scale, ys[1] * axh)
    for (col, label, _, _, _), y in zip(rows, ys):
        _, lo, hi = ci[col]
        gap = _arc_clearance_pt(a_in, b_in, ARC_RAD, y * axh,
                                (lo - xlo) * scale, (hi - xlo) * scale)
        assert gap >= ARROW_CLEAR_PT, (
            f"the transition arrow passes within {gap:.2f} pt of the interval on the "
            f"{label!r} row, and two blue horizontals that close together read as one. Retune "
            f"ARC_RAD; {ARROW_CLEAR_PT:.1f} pt is the floor.")

    zero_rule(ax, 0.0, vertical=True, color=SUBTLE, lw=0.8, zorder=2)

    # ---- the ladder ---------------------------------------------------------------------------
    for (col, label, hue, filled, derived), y in zip(rows, ys):
        m, lo, hi = ci[col]
        ax.plot([lo, hi], [y, y], color=hue, lw=1.0, alpha=0.45 if derived else 0.55,
                solid_capstyle="butt", zorder=3)
        ax.scatter([m], [y], s=MS_DOT - 6 if derived else MS_DOT, marker="D" if derived else "o",
                   facecolor=hue if filled else "white", edgecolor=hue, linewidths=0.9,
                   zorder=6 if derived else 5)
        ax.text(-0.020, y, label, transform=ax.transAxes, ha="right", va="center",
                fontsize=PT_SMALL if derived else PT_ANNOT,
                color=SUBTLE if derived else TEXT)

    # ---- the transition, and the two values it moves between ----------------------------------
    y_energy, y_partial = ys[0], ys[1]
    ax.annotate("", xy=(med[PARTIAL_COL], y_partial), xytext=(med[ENERGY_COL], y_energy),
                arrowprops=dict(arrowstyle="-|>,head_width=0.10,head_length=0.26", color=POP,
                                lw=0.9, alpha=0.6, shrinkA=4.0, shrinkB=4.4,
                                connectionstyle=f"arc3,rad={ARC_RAD}"), zorder=4)
    for col, y in ((ENERGY_COL, y_energy), (PARTIAL_COL, y_partial)):
        ax.text(med[col], y + VAL_DY, f"{med[col]:+.3f}", ha="center", va="center",
                fontsize=PT_ANNOT, color=TEXT)

    # ---- group brackets and tags, in the lane no datum reaches --------------------------------
    x_brk, x_tag = x_at(data_r + 0.06), x_at(data_r + LANE_GAP)
    for tag, i0, i1 in tags:
        y0, y1 = ys[i1] - 0.045, ys[i0] + 0.045
        ax.plot([x_brk, x_brk], [y0, y1], color=SUBTLE, lw=LW_HAIR, alpha=0.8, zorder=3)
        ax.text(x_tag, 0.5 * (y0 + y1), tag, ha="left", va="center", fontsize=PT_SMALL,
                color=SUBTLE)

    # ---- axes ---------------------------------------------------------------------------------
    bare_axes(ax, keep=("bottom",))
    ax.spines["bottom"].set_bounds(0.0, axis_end)   # the scale stops where the data stop
    ax.set_yticks([])
    ax.set_xticks([t for t in np.arange(0.0, 0.85, 0.1) if t <= axis_end + 1e-9])
    ax.set_xlabel(r"Spearman $\rho$ with drug-drug functional similarity", fontsize=PT_ANNOT,
                  labelpad=1.6)
    title(ax, TITLE_3H)
    return {"medians": med, "ci": ci, "paired_energy_minus_partial": paired}


if __name__ == "__main__":
    from figstyle import apply_style
    from fig3_style import PT_TICK, PT_TITLE

    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    W, H = 4.10, 1.44                                   # the panel box h occupies in Figure 3
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([1.34 / W, 0.36 / H, 2.66 / W, 0.84 / H])
    out = draw_3h(ax)
    for k, v in out["medians"].items():
        print(f"{k:32s} {v:+.4f}   95% CI {out['ci'][k][1]:+.4f} to {out['ci'][k][2]:+.4f}")
    print(f"per-query energy minus partial: median {out['paired_energy_minus_partial'][0]:+.4f}, "
          f"95% CI {out['paired_energy_minus_partial'][1]:+.4f} to "
          f"{out['paired_energy_minus_partial'][2]:+.4f}")
    fig.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "3h.png"), dpi=300)
    print("wrote 3h.png")
