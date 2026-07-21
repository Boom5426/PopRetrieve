"""DART Figure 6 panel 6c: Gate 1 — structure is preserved, DIVERGENCE is not.
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
LABS = {"real_blend": "real", "average_effect": "avg-effect",
        "scgen": "latent\n(scGen-fam.)", "nearest_neighbor": "nearest\nneighbor"}


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
    ax2.text(-0.42, 0.955,
             "additive limit:  $\\cos = 1$",
             ha="left", va="top", fontsize=5.5, color=COMP, style="italic")
    ax2.errorbar(xs + 0.09, cos, yerr=cerr, fmt="s", color=COMP, ms=5, capsize=3, lw=1.3,
                 zorder=3, label=r"induced $\cos(d_{maj}, d_{min})$")
    ax2.axhline(cos[0], ls=":", lw=1.0, color=COMP, alpha=0.7, zorder=1)
    ax2.set_ylabel(r"induced response cosine", color=COMP)
    ax2.tick_params(axis="y", colors=COMP)
    ax2.set_ylim(-0.05, 1.12)
    ax2.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax2.spines["top"].set_visible(False)

    ax.set_xticks(xs)
    ax.set_xticklabels([LABS[p] for p in ORDER], fontsize=6)
    ax.set_xlim(-0.5, len(ORDER) - 0.5)
    for sp in ["right", "top"]:
        ax.spines[sp].set_visible(False)

    ax.annotate("structure preserved", xy=(2.0, var[0]), xytext=(1.15, var[0] * 0.45),
                fontsize=5.5, color=FOCAL,
                arrowprops=dict(arrowstyle="->", lw=0.7, color=FOCAL))
    ax2.annotate("no differential response\nto exploit", xy=(3.09, cos[3]),
                 xytext=(1.35, 0.62), fontsize=5.3, color=COMP,
                 arrowprops=dict(arrowstyle="->", lw=0.7, color=COMP))
    ax2.annotate("real: responses\nnear-orthogonal", xy=(0.09, cos[0]), xytext=(0.02, 0.30),
                 fontsize=5.3, color=COMP,
                 arrowprops=dict(arrowstyle="->", lw=0.7, color=COMP))


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.8, 3.0))
    draw_6c(ax)
    ax.set_title("Structure survives; divergence does not", loc="left")
    fig.savefig(os.path.join(os.path.dirname(__file__), "6c.png"), dpi=200, bbox_inches="tight")
    print("wrote 6c.png")
