"""Figure 4 panel c: energy's lead over the magnitude control, under BOTH evaluator forms.

Source: results/upgrade/oracle_shape_test.json (analysis/class_c/oracle_shape_test.py), the same
file panel b draws. No number is written out in this docstring; see fig4_shape.py's note on why.

WHAT THIS PANEL SHOWS, AND WHY IT IS A SEPARATE PANEL
------------------------------------------------------
Panel b shows that the winner swaps when the protein evaluator is rebuilt from a mean into a
distribution. That result is not in question. The question this panel answers is what the swap is
made of, and it is the panel that retired an explanation.

Both distributional objects in panel b are energy distances, and an energy distance tracks a
candidate's own response magnitude. So the swap could be a magnitude-to-magnitude channel with no
distribution ever compared, and the third bar in panel b, a query-dependent magnitude scalar that
compares no distributions at all, is the control that measures it. What matters is how far energy
exceeds that control under EACH evaluator form:

  * if energy's lead is large under the distributional evaluator and small under the mean-shaped
    one, the reversal is distribution-specific and a population-shaped evaluator is rewarding a
    population-shaped scorer;
  * if the two leads are of the same size, magnitude is a channel that is present under both
    forms, and the reversal cannot be attributed to distributional compatibility alone.

Under the V-statistic energy distance the first reading held, by a factor of about eight, and it
is what the manuscript said. Under the unbiased U-statistic the second holds. That is the whole
reason this panel exists as its own panel rather than as a sentence in panel b's caption: the
correction is a positive finding about where the effect comes from, and it is drawn.

WHAT IS DRAWN
-------------
Four rows: the pooled 659 queries and each of the three Perturb-CITE-seq conditions separately.
Two markers per row, one per evaluator form, joined by a connector. The panel is read by how SHORT
each connector is, which is why the two markers share one grey and differ only in shape: colour in
this figure names a scoring family, and the quantity plotted here belongs to neither family.

The per-condition rows are not a robustness afterthought. Pooling three conditions could produce a
similar pair of numbers by averaging one condition where the lead is distribution-specific against
two where it is not, and the rows show that it does not: the two leads track each other inside
every condition.

JUDGEMENT CALLS A READER COULD REASONABLY DISAGREE WITH
-------------------------------------------------------
  1. NO INTERVALS. The source records one correlation per condition per evaluator form, not a
     resampling distribution, so there is nothing here to put an interval on and none is drawn.
     What the panel offers instead of an interval is the three conditions, which is a weaker but
     honest statement about stability. The caption says the panel shows no uncertainty.
  2. THE RATIO IS PRINTED, THE DIFFERENCE IS NOT. "The same order under both forms" is a
     statement about a ratio, and a difference of 0.019 on a quantity of 0.1 would read as small
     for reasons of scale rather than of proportion. Both are computed and returned.
  3. THE POOLED ROW IS DRAWN WITH THE THREE CONDITIONS, not above a rule separating it from them.
     It is the same quantity on the union of the same cells, and the panel's claim is about all
     four rows agreeing.
  4. THE CONDITION THAT DOES NOT FLIP IS NOT MARKED. One of the three conditions has energy
     winning under both evaluator forms, so no reversal happens there at all. That belongs to
     panel b's claim rather than to this one, and marking it here would import panel b's argument
     into a panel about magnitude. It is asserted below and returned for the caption.

Run standalone: python3 fig4_residual.py
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
from matplotlib.backends.backend_agg import RendererAgg

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig4_style import (HAIRLINE, LW_HAIR, LW_LINE, MS_DOT, PT_ANNOT,  # noqa: E402
                        PT_SMALL, PT_TICK, REPO, SHARED, SUBTLE, TEXT)

SRC = f"{REPO}/results/upgrade/oracle_shape_test.json"

# (JSON suffix, marker, the name drawn beside the top row's marker).
# The names are short because the panel is 1.64 in wide and the x axis already says these are
# correlations "with the protein evaluator"; the key only has to say which form.
FORMS = [("MEAN", "o", "mean form"),
         ("DIST", "s", "distribution form")]
POOLED_LABEL = "all conditions"

XLO, XHI = 0.0, 0.205
XTICKS = [0.0, 0.05, 0.10, 0.15, 0.20]
DY = 0.17                # vertical offset of the two markers from their row centre
RATIO_X = 0.985          # right edge of the printed ratio, in axes fraction
KEY_DY = 0.62            # the key's height above the top row, in row units
KEY_X0 = 0.02            # where the key starts, as a fraction of the x range
KEY_GAP = 0.055          # air between the two key entries, as a fraction of the x range
LABEL_DX_PT = 4.0        # marker to its form name, in printed points
# The largest ratio any row may take before "the same order under both evaluator forms" stops
# being what the panel shows. fig4_shape.RESID_RATIO_MAX carries the same bound for the pooled
# row; this panel applies it to every row, which is the stronger statement it draws.
RATIO_MAX = 2.0


def residuals():
    """Energy minus the magnitude scalar, per evaluator form, pooled and per condition.

    Returns a list of (label, n, {suffix: residual}), pooled row first. Every value is computed
    from the two correlations the source records, never read from a summary field, so a summary
    that drifted from its own inputs cannot reach the panel.
    """
    if not os.path.exists(SRC):
        raise FileNotFoundError(f"{SRC} missing. Run analysis/class_c/oracle_shape_test.py.")
    d = json.load(open(SRC))

    def _pair(block):
        return {suf: float(block[f"energy_vs_oracle{suf}"] - block[f"magmatch_vs_oracle{suf}"])
                for suf, _, _ in FORMS}

    rows = [(POOLED_LABEL, int(d["n_queries"]), _pair(d))]
    for name, block in d["per_condition"].items():
        rows.append((name, int(block["n"]), _pair(block)))
    assert len(rows) >= 3, f"{SRC} carries {len(rows) - 1} conditions; the panel is drawn for three"
    assert sum(n for _, n, _ in rows[1:]) == rows[0][1], (
        f"the three conditions hold {sum(n for _, n, _ in rows[1:])} queries and the pooled row "
        f"{rows[0][1]}; they are supposed to partition the same cells.")
    # The pooled row must agree with the summary the file states for itself, which is the same
    # cross-check fig4_shape makes; here it also proves the two panels draw one quantity.
    for suf, _, _ in FORMS:
        stated = float(d["magnitude_confound"][f"energy_minus_magmatch_under_{suf}"])
        assert abs(rows[0][2][suf] - stated) < 1e-9, (
            f"the pooled residual under the {suf} evaluator computes to {rows[0][2][suf]:+.5f} "
            f"and {SRC} records {stated:+.5f}. The file disagrees with its own inputs.")
    flips = {name: bool(block["flips"]) for name, block in d["per_condition"].items()}
    return rows, flips


def draw_residual(ax):
    """Four rows, two evaluator forms each, of energy's lead over the magnitude control."""
    rows, flips = residuals()

    # ---- what the panel claims, asserted before it is drawn ---------------------------------
    for label, _, pair in rows:
        assert min(pair.values()) > 0.0, (
            f"on {label!r} the magnitude scalar matches or beats energy under one evaluator form "
            f"({pair}). The panel draws a positive lead on every row; the caption must change.")
        ratio = max(pair.values()) / min(pair.values())
        assert ratio <= RATIO_MAX, (
            f"on {label!r} the lead is {ratio:.1f} times larger under one evaluator form than "
            f"under the other ({pair}), past the {RATIO_MAX} this panel calls the same order. At "
            f"that separation the retired reading, that the reversal is distribution-specific, "
            f"is arguable again. See docs/phase2/POST_REPAIR_MASTER_RESULTS.md C1.")
    # Judgement call 4: the panel says nothing about which conditions flip, but it must know, so
    # that a caption sentence about them cannot be written from memory.
    assert any(flips.values()) and not all(flips.values()), (
        f"the reversal now holds in every condition or in none ({flips}); panel b's caption "
        f"describes a pooled reversal that holds in some, and this panel returns the counts it "
        f"is written from.")

    ys = np.arange(len(rows))[::-1].astype(float)
    ax.set_xlim(XLO, XHI)
    ax.set_ylim(ys.min() - 0.62, ys.max() + 0.95)

    ax.axvline(0.0, color=TEXT, lw=0.8, zorder=2)
    for y, (label, n, pair) in zip(ys, rows):
        vals = [pair[suf] for suf, _, _ in FORMS]
        # The connector IS the panel's argument: its length is how far the two evaluator forms
        # disagree about the size of the magnitude channel.
        ax.plot([min(vals), max(vals)], [y, y], color=HAIRLINE, lw=LW_LINE, zorder=3,
                solid_capstyle="round")
        for (suf, marker, _), dy in zip(FORMS, (+DY, -DY)):
            ax.scatter([pair[suf]], [y + dy], s=MS_DOT, marker=marker, facecolor=SHARED,
                       edgecolor="white", linewidths=0.5, zorder=5)
        ratio = max(vals) / min(vals)
        ax.text(RATIO_X, y, f"{ratio:.2f}×", transform=ax.get_yaxis_transform(),
                ha="right", va="center", fontsize=PT_SMALL, color=SUBTLE, zorder=6)

    # The key sits in the band above the top row rather than on the top row's own markers. Beside
    # the markers it collided with the row's ratio on one side and with the y tick labels on the
    # other: at 1.64 in of axes there is no horizontal room on a row that already carries two
    # markers, a connector and a number.
    key_y = ys.max() + KEY_DY
    kx = XLO + KEY_X0 * (XHI - XLO)
    r = RendererAgg(int(ax.figure.get_figwidth() * ax.figure.dpi),
                    int(ax.figure.get_figheight() * ax.figure.dpi), ax.figure.dpi)
    inv = ax.transData.inverted()
    for suf, marker, name in FORMS:
        ax.scatter([kx], [key_y], s=MS_DOT, marker=marker, facecolor=SHARED, edgecolor="white",
                   linewidths=0.5, zorder=6, clip_on=False)
        t = ax.annotate(name, xy=(kx, key_y), xytext=(LABEL_DX_PT, 0.0),
                        textcoords="offset points", ha="left", va="center", fontsize=PT_SMALL,
                        color=TEXT, zorder=6)
        x_end = float(inv.transform((t.get_window_extent(renderer=r).x1, 0.0))[0])
        kx = x_end + KEY_GAP * (XHI - XLO)
    assert kx <= XHI, (
        f"the two-entry key runs to {kx:.3f} on an axis that ends at {XHI}; shorten the form "
        f"names rather than letting the key overhang the panel box.")

    ax.set_yticks(ys)
    ax.set_yticklabels([f"{label}\nn = {n}" for label, n, _ in rows], fontsize=PT_TICK,
                       linespacing=1.15)
    ax.tick_params(axis="y", length=0, pad=2.0)
    ax.set_xticks(XTICKS)
    ax.set_xticklabels([f"{t:g}" for t in XTICKS], fontsize=PT_TICK)
    ax.set_xlabel("energy $-$ magnitude scalar,\nSpearman $\\rho$ with the protein evaluator",
                  fontsize=PT_ANNOT, labelpad=1.5, linespacing=1.20)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(HAIRLINE)
    ax.spines["bottom"].set_linewidth(LW_HAIR)
    ax.tick_params(axis="x", length=2.2, width=0.6, color=HAIRLINE, labelcolor=TEXT)

    return {"rows": {label: pair for label, _, pair in rows},
            "n": {label: n for label, n, _ in rows},
            "ratio": {label: max(p.values()) / min(p.values()) for label, _, p in rows},
            "difference": {label: max(p.values()) - min(p.values()) for label, _, p in rows},
            "flips": flips}


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sys.path.insert(0, os.path.join(REPO, "figures"))
    from figstyle import apply_style
    from fig4_style import PT_TITLE

    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    plt.rcParams["savefig.bbox"] = None
    BOX_W, BOX_H, PAD_L, PAD_B, AX_W, AX_H = 2.60, 1.55, 0.86, 0.52, 1.64, 0.97
    fig = plt.figure(figsize=(BOX_W, BOX_H))
    ax = fig.add_axes([PAD_L / BOX_W, PAD_B / BOX_H, AX_W / BOX_W, AX_H / BOX_H])
    out = draw_residual(ax)
    print(json.dumps({k: (v if not isinstance(v, dict) else
                          {kk: (round(vv, 5) if isinstance(vv, float) else vv)
                           for kk, vv in v.items()}) for k, v in out.items()}, indent=1,
                     ensure_ascii=False))
    fig.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "4c.png"), dpi=300)
    print("wrote 4c.png")
