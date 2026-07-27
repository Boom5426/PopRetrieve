"""EvalShift Figure 6 panel 6c: Gate 1 — structure is preserved, DIVERGENCE is not.
Source data: results/exp09_structure_diagnostics/
Run standalone: python fig6c.py

Rewritten 2026-07-12. The old panel plotted "predictors collapse subpopulation variance,
5.1x collapse, real 0.046". That claim is retracted: it was an artifact of the repository's
own population synthesizer on both sides of the comparison (predicted populations were built
as control_mean + delta + iid Gaussian noise, which is unimodal by construction, so their
variance ratio was just the null value of the statistic; and the "real" reference was a
single-context population rather than the blended candidate a scorer actually ranks).

With the effect applied to real control cells instead, predicted populations retain as much
baseline structure as real ones. What they lack is DIVERGENCE: the two subpopulations respond
in nearly the same direction. This panel shows both facts at once, which is the finding.
"""
import os, numpy as np, pandas as pd, matplotlib.pyplot as plt
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

DIAG = f"{REPO}/results/exp09_structure_diagnostics"
ORDER = ["real_blend", "average_effect", "scgen", "nearest_neighbor"]
# "avg-effect" is wrapped for geometry only: Figure 6 is authored at its printed width, so this
# panel is 1.86 in wide and one x category is 0.465 in, while "avg-effect" is 0.42 in at 6 pt and
# butted against its neighbour. Wrapped, the widest single line here is "(scGen-fam.)".
LABS = {"real_blend": "real", "average_effect": "avg-\neffect",
        "scgen": "latent\n(scGen-fam.)", "nearest_neighbor": "nearest\nneighbour"}


def _pick(df, pred, col):
    """Row for a predictor under the faithful ('cells') synthesizer; real under 'real'."""
    synth = "real" if pred.startswith("real") else "cells"
    sub = df[(df.predictor == pred) & (df.synth == synth)]
    if sub.empty:
        raise KeyError(f"no row for predictor={pred!r} synth={synth!r} in {DIAG}. "
                       f"Re-run exp09_structure_diagnostics.py --synth both.")
    return float(sub[col].iloc[0])


def draw_6c(ax):
    sd = pd.read_csv(f"{DIAG}/exp09_structure_diagnostics_summary.csv")
    g1 = pd.read_csv(f"{DIAG}/gate1_response_divergence_summary.csv")

    xs = np.arange(len(ORDER))
    var = [_pick(sd, p, "subpop_variance_ratio_mean") for p in ORDER]
    verr = [_pick(sd, p, "subpop_variance_ratio_std") for p in ORDER]
    cos = [_pick(g1, p, "mean") for p in ORDER]
    cerr = [_pick(g1, p, "std") for p in ORDER]

    # A quiet band separates the one observed reference from the three predicted candidates,
    # so the reader does not have to read four x-labels to see which is which. This replaces
    # three leader-line annotations that used to cross the error bars.
    ax.axvspan(0.5, len(ORDER) - 0.5, color="#F2F2F2", zorder=0, lw=0)

    # left axis: baseline structure — flat across real and predicted (structure IS preserved)
    ax.errorbar(xs - 0.09, var, yerr=verr, fmt="o", color=FOCAL, ms=6, capsize=3, lw=1.3,
                zorder=3, label="subpop variance ratio")
    ax.axhline(var[0], ls="--", lw=1.0, color=FOCAL, alpha=0.7, zorder=1)
    ax.set_ylabel("subpop variance ratio", color=FOCAL)
    ax.tick_params(axis="y", colors=FOCAL)
    ax.set_ylim(0, max(var) * 1.25)

    # right axis: induced response cosine — the thing that actually fails.
    #
    # The scale must run to 1, because 1 is where the algebra puts an additive predictor:
    # if the same delta is added to every cell then d_maj = d_min, so cos = 1 EXACTLY and the
    # divergence a distributional score could exploit is exactly zero. Plotting this axis on a
    # 0-0.6 range hides that ceiling and invites the reader to confuse "cosine 0.19" with
    # "divergence zero". Real candidate populations sit near cos = 0 (orthogonal responses,
    # maximal divergence); predicted ones sit between, below the ceiling only because a scorer
    # must estimate the subpopulation partition and estimates it imperfectly (Gate 2).
    ax2 = ax.twinx()
    ax2.axhline(1.0, ls="-", lw=1.0, color=COMP, alpha=0.55, zorder=1)
    # Short label only: this marks the algebraic ceiling so the line is not mistaken for data.
    # The full statement (additive predictor => identical subpopulation responses => cosine
    # exactly 1, divergence exactly zero) belongs in the caption, where it already is.
    ax2.text(len(ORDER) - 0.58, 1.025, "additive limit, $\\cos = 1$",
             ha="right", va="bottom", fontsize=5.5, color=COMP, style="italic")
    ax2.errorbar(xs + 0.09, cos, yerr=cerr, fmt="s", color=COMP, ms=5, capsize=3, lw=1.3,
                 zorder=3, label=r"induced $\cos(d_{maj}, d_{min})$")
    ax2.axhline(cos[0], ls=":", lw=1.0, color=COMP, alpha=0.7, zorder=1)
    ax2.text(-0.44, cos[0] + 0.02, "real", ha="left", va="bottom", fontsize=5.5, color=COMP)
    ax2.set_ylabel(r"induced response cosine", color=COMP)
    ax2.tick_params(axis="y", colors=COMP)
    ax2.set_ylim(-0.05, 1.20)
    ax2.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax2.spines["top"].set_visible(False)

    ax.set_xticks(xs)
    ax.set_xticklabels([LABS[p] for p in ORDER], fontsize=6)
    ax.set_xlim(-0.5, len(ORDER) - 0.5)
    ax.set_ylim(0, max(var) * 1.42)
    for sp in ["right", "top"]:
        ax.spines[sp].set_visible(False)

    # Group headers, inside the axes (above every marker) so they cannot hit the panel title.
    ax.text(0.125, 0.955, "observed", transform=ax.transAxes,
            ha="center", va="center", fontsize=5.8, color=GREY)
    ax.text(0.625, 0.955, "predicted", transform=ax.transAxes,
            ha="center", va="center", fontsize=5.8, color=GREY)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(1.86, 1.80))   # the slot it occupies in fig6_assemble
    draw_6c(ax)
    ax.set_title("Structure survives; divergence does not", loc="left")
    fig.savefig(os.path.join(os.path.dirname(__file__), "6c.png"), dpi=200, bbox_inches="tight")
    print("wrote 6c.png")
