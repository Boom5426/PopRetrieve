"""DART Figure 6 panel 6b: predictor-specific retrieval gaps
Source data: source_data/fig6b_predictor_gaps.csv
Run standalone: python fig6b.py

Fixed 2026-07-12: this panel used to reindex on 'scgen_cpa_linear', but
results/exp09_predict_then_rank/summary.csv keys that predictor as 'scgen'. The reindex
produced NaN, so the predictor was silently dropped and rendered as a blank row labelled
'+nan'. It is the ONE predictor with a POSITIVE gain (+0.027 nDCG@10), which is why the old
panel title, "No predictor gives a positive gain", was falsified by the deck's own source
data. The key is corrected here, the panel now fails loudly rather than plotting NaN, and
bars are coloured by sign so a positive gain cannot be overlooked again.
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# key in summary.csv -> display label. 'scgen' runs the in-repo CPA-style linear-latent
# backend (see results/exp09_predict_then_rank/provenance.csv), so it is labelled as such.
PREDICTORS = {
    "average_effect": "avg-effect",
    "scgen": "latent-linear\n(scGen-family)",
    "nearest_neighbor": "nearest-neighbor",
}


def draw_6b(ax):
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
    ax.axvline(0, ls="--", lw=1.0, color=GREY, zorder=1)
    for y, (idx, row) in zip(ys, g.iterrows()):
        c = FOCAL if row["mean"] > 0 else COMP      # FOCAL = distributional retrieval wins
        ax.errorbar(row["mean"], y, xerr=row["sem"], fmt="o", color=c, ms=6, capsize=3,
                    lw=1.3, zorder=3)
        ax.text(row["mean"], y + 0.24, f"{row['mean']:+.3f}", ha="center", fontsize=6, color=c)
    ax.set_yticks(ys)
    ax.set_yticklabels([PREDICTORS[i] for i in g.index], fontsize=6)
    ax.set_ylim(-0.6, len(g) - 0.3)
    ax.set_xlabel("nDCG@10 gain (DART $-$ mean)")
    for sp in ["right", "top"]:
        ax.spines[sp].set_visible(False)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.4, 3.0))
    draw_6b(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "6b.png"), dpi=200, bbox_inches="tight")
    print("wrote 6b.png")
