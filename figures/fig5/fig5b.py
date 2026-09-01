"""PopRetrieve Figure 5 panel 5b: predictor-specific retrieval gaps
Source data: results/exp09_predict_then_rank/summary.csv (+ provenance.csv)
             (source_data/fig5b_predictor_gaps.csv is a hand-built per-predictor view, not read here)
Run standalone: python fig5b.py

Fixed 2026-07-12: this panel used to reindex on 'scgen_cpa_linear', but
results/exp09_predict_then_rank/summary.csv keys that predictor as 'scgen'. The reindex
produced NaN, so the predictor was silently dropped and rendered as a blank row labelled
'+nan'. It is the ONE predictor with a POSITIVE gain (+0.027 nDCG@10), which is why the old
panel title, "No predictor gives a positive gain", was falsified by the deck's own source
data. The key is corrected here, the panel now fails loudly rather than plotting NaN, and
bars are coloured by sign so a positive gain cannot be overlooked again.
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
# Palette comes from the house-style module; do NOT re-declare the hex values here. Every
# panel file used to carry its own copy, which made figstyle's "one edit here recolours the
# whole deck" untrue: a recolour meant editing 43 files and missing one was silent.
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from figstyle import FOCAL_SOFT, COMP_SOFT, GREY, INK  # noqa: E402
from fig5_style import PT_SMALL, PT_TICK  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# key in summary.csv -> display label. 'scgen' runs the in-repo CPA-style linear-latent
# backend (see results/exp09_predict_then_rank/provenance.csv), so it is labelled as such.
#
# The wrapping is geometry. Figure 5 is authored at its printed width, which leaves this panel a
# 1.45 in slot with a 0.55 in left gutter; at 6 pt "nearest-neighbour" is 0.71 in and
# "(scGen-family)" 0.58 in, so both used to run out of the gutter and across panel a's boxes.
# Wrapped and abbreviated to "(scGen-fam.)" (the form panel c already uses) they are <= 0.50 in.
PREDICTORS = {
    "average_effect": "avg-effect",
    "scgen": "linear-\nlatent",
    # British spelling, to match the Fig. 5 caption ("-0.071 (nearest-neighbour)") and the rest
    # of the manuscript, which uses "neighbour" throughout.
    "nearest_neighbor": "nearest-\nneighbour",
}


def draw_5b(ax):
    df = pd.read_csv(f"{REPO}/results/exp09_predict_then_rank/summary.csv")
    piv = df.pivot_table(index=["task", "predictor"], columns="retrieval",
                         values="ndcg@10").reset_index()
    piv["delta"] = piv["dart_energy"] - piv["mean_cosine"]
    g = piv.groupby("predictor")["delta"].agg(["mean", "sem"]).reindex(PREDICTORS)
    if g["mean"].isna().any():
        missing = list(g.index[g["mean"].isna()])
        raise KeyError(
            f"predictor(s) {missing} not found in summary.csv "
            f"(present: {sorted(piv.predictor.unique())}). Refusing to plot NaN: a silently "
            f"dropped predictor is exactly the bug this panel was fixed for.")

    ys = np.arange(len(g))[::-1]
    # summary.csv holds ONE task (crossline), so the across-task s.e.m. is undefined. The old
    # code passed that NaN straight to errorbar(), which silently drew nothing: the panel
    # looked like it carried dispersion and did not. Dispersion is drawn only if it exists.
    has_err = bool(g["sem"].notna().all())
    lo = float((g["mean"] - g["sem"].fillna(0)).min())
    hi = float((g["mean"] + g["sem"].fillna(0)).max())
    span = max(abs(lo), abs(hi))
    # Symmetric about 0, so sign reads directly. The half-width is 2.1x rather than 1.85x the
    # largest gain because at the printed panel width (1.45 in) the "-0.071" value label needs
    # 0.25 in to the LEFT of its own marker and 1.85x left it hanging over the y axis.
    ax.set_xlim(-span * 2.1, span * 2.1)

    ax.axvline(0, ls="--", lw=1.0, color=GREY, zorder=1)
    for y, (idx, row) in zip(ys, g.iterrows()):
        c = FOCAL_SOFT if row["mean"] > 0 else COMP_SOFT      # FOCAL_SOFT = distributional retrieval wins
        # stem back to the null, so "how far from no difference" is the visual quantity
        ax.plot([0, row["mean"]], [y, y], lw=1.0, color=c, alpha=0.55, zorder=2)
        if has_err:
            ax.errorbar(row["mean"], y, xerr=row["sem"], fmt="o", color=c, ms=6, capsize=3,
                        lw=1.3, zorder=3)
        else:
            ax.plot([row["mean"]], [y], "o", color=c, ms=6, mec="white", mew=0.6, zorder=3)
        # value label on the OUTER side of the marker, away from zero: on the inner side the
        # stem to the null line runs straight through the digits
        side = -1 if row["mean"] < 0 else 1
        # The dot this label belongs to is 0.13 of the span away and carries the sign colour.
        ax.text(row["mean"] + side * span * 0.13, y, f"{row['mean']:+.3f}".replace('-', '\u2212'),
                ha="left" if side > 0 else "right", va="center", fontsize=PT_SMALL, color=INK)
    ax.set_yticks(ys)
    ax.set_yticklabels([PREDICTORS[i] for i in g.index], fontsize=PT_TICK)
    # Top limit leaves room for the key block, whose text top sits at Y_KEY + 0.17; at len(g)
    # - 0.18 the two direction hints ran 0.019 in above the panel box.
    ax.set_ylim(-0.62, len(g) + 0.02)
    # Three ticks, not five. At 1.45 in a five-tick 0.05 grid puts 0.21 in labels 0.24 in apart.
    ax.set_xticks([-0.1, 0.0, 0.1])
    # SHORT FORM. The full label is 1.55 in at 6 pt against a 1.43 in panel, so it overflowed
    # both sides and its left end landed on panel e's letter one row below. The sign convention
    # it spelled out is already stated ON this panel by the two-sided key below, and again in the
    # caption, so the panel keeps the quantity and drops the restatement.
    ax.set_xlabel("nDCG@10 gain", labelpad=1.5)

    # Direct labels replace a legend: which side of the null means what. "mean-signature better"
    # was 0.72 in at 5.5 pt, wider than the half-axis it had to sit in, and was clipped by the
    # y axis. "mean" is the exact term the x axis label uses, so the short form is unambiguous
    # inside this panel and the full name is in the caption.
    # This pair IS the panel's key and has no mark of its own beside it, so each half gets a
    # swatch and the words stay ink. Everywhere else in this deck a coloured label sits next to
    # a coloured mark and can simply be recoloured; here the mark has to be supplied.
    # Swatch first, reading outward from the null line, then the words. Anchoring both to the
    # null rather than to the text means neither needs the rendered text width in data units.
    Y_KEY = len(g) - 0.30
    for sgn, txt, col, ha in [(-1, "mean\nbetter", COMP_SOFT, "right"),
                              (+1, "distributional\nbetter", FOCAL_SOFT, "left")]:
        x0 = sgn * span * (0.05 if sgn > 0 else 0.10)
        ax.add_patch(Rectangle((x0, Y_KEY), sgn * span * 0.05, 0.17,
                               color=col, lw=0, clip_on=False, zorder=5))
        ax.text(sgn * span * 0.13, Y_KEY + 0.17, txt, ha=ha, va="top",
                fontsize=PT_SMALL, color=INK, linespacing=1.15)
    for sp in ["right", "top"]:
        ax.spines[sp].set_visible(False)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(1.45, 1.80))   # the slot it occupies in fig5_assemble
    draw_5b(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "5b.png"), dpi=200, bbox_inches="tight")
    print("wrote 5b.png")
