"""DART Extended Data figures (ED1-ED4), each blocking one anticipated reviewer attack.

ED1 reproducibility basis  | "your data/metrics are non-standard"
ED2 Class B robustness     | "the null is just underpowered"  (the most important one for a
                             paper whose core result is negative)
ED3 identifiability robust | "you clustered badly; another method would find the subpops"
ED4 resistance exploratory | a transparent home for the exploratory signal, kept out of the
                             main deck

FIXED 2026-07-12. This module previously defined thirteen draw functions that referenced
fifteen module-level names which were never assigned (dataset_scale, corr, pw, strat, med,
sd, subpop, pd_grid, enr, mrk, resc, ...), and it had no loader, no assemble step, no
savefig and no __main__. The four ED figures on disk could therefore not be rebuilt by any
code in the repository. It now loads its own data from results/, draws, and writes the PDFs
and PNGs.

Two panels also asserted things their own source data contradict, and both are corrected:

  ED2c said "gain stays <= 0 across all divergence strata". The Q4 mean gap is positive
  (+0.003, not significant), and after the -1 sentinel fix the Q1 gap is significantly
  NEGATIVE (median -0.030, q=5.8e-5). The honest statement is stronger than the old one:
  the null is not a power artifact because at high divergence there is no effect, and at
  low divergence the effect runs against DART.

  ED3c said "predictors collapse subpopulation variance 5.1x". That is retracted. It
  compared a single-context real population against populations we had synthesized as an
  isotropic Gaussian around one mean, so it measured our own synthesizer. Predicted
  populations in fact PRESERVE structure; what they lack is differential response.

    PYTHONPATH=src python figures/edfigs/ed_panels.py
"""
import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "figures"))

from figstyle import FOCAL, COMP, GREY, INK, apply_style, panel_letter  # noqa: E402

DIVMAP = LinearSegmentedColormap.from_list("dart_div", [COMP, "#f7f7f7", FOCAL])
RES = os.path.join(REPO, "results")
SD = os.path.join(REPO, "figures", "source_data")
OUT = os.path.dirname(os.path.abspath(__file__))

METRIC_LABELS = {
    "mean_cosine": "mean cos", "global_energy": "energy", "coverage_mean": "cov-mean",
    "coverage_worst": "cov-worst", "cmap_cosine": "CMap cos", "cmap_wtcs": "CMap WTCS",
}
METHOD_DISP = {
    "raw_kmeans_k2": "k-means k=2", "raw_kmeans_k3": "k-means k=3",
    "raw_kmeans_k4": "k-means k=4", "raw_kmeans_k5": "k-means k=5",
    "raw_kmeans_bestk3": "k-means best-k", "raw_kmeans_bestk4": "k-means best-k",
    "raw_kmeans_bestk5": "k-means best-k", "response_kmeans_k2": "k-means k=2 (response)",
    "gmm_k2": "GMM k=2", "pca10_kmeans_k2": "PCA-10 + k-means",
    "pca50_kmeans_k2": "PCA-50 + k-means",
}


def _read(path, what):
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"{what} needs {path}, which does not exist. Run the experiment that writes it "
            f"before rebuilding the Extended Data figures; this module will not invent a "
            f"number.")
    return pd.read_csv(path)


def load():
    """Bind every table the draw functions need, from results/ (the source of truth)."""
    d = {}
    d["dataset_scale"] = _read(f"{SD}/ed1_dataset_scale.csv", "ED1a")
    d["corr"] = _read(f"{SD}/ed1_metric_correlation.csv", "ED1c").set_index(
        _read(f"{SD}/ed1_metric_correlation.csv", "ED1c").columns[0])

    # ED2 comes from the CORRECTED exp17 (sentinel-masked), not from the stale export.
    strat = _read(f"{RES}/exp17_true_divergence_subset/divergence_stratified.csv", "ED2c")
    d["strat"] = strat
    d["pw"] = _read(f"{RES}/exp17_true_divergence_subset/power_analysis.csv", "ED2a/b")

    d["med"] = _read(f"{SD}/ed3_method_ari.csv", "ED3a").set_index(
        _read(f"{SD}/ed3_method_ari.csv", "ED3a").columns[0])["median_ari"]
    d["subpop"] = _read(f"{SD}/ed3_silhouette.csv", "ED3b")
    # ED3c comes from the CORRECTED structure diagnostics, not the retracted export.
    d["sd"] = _read(f"{RES}/exp09_structure_diagnostics/"
                    f"exp09_structure_diagnostics_summary.csv", "ED3c")
    d["g1"] = _read(f"{RES}/exp09_structure_diagnostics/"
                    f"gate1_response_divergence_summary.csv", "ED3c")
    d["pd_grid"] = _read(f"{REPO}/results/upgrade/identifiability_phase_diagram.csv", "ED3d")

    d["enr"] = _read(f"{SD}/ed4_enrichment_summary.csv", "ED4a")
    d["mrk"] = _read(f"{SD}/ed4_marker_enrichment.csv", "ED4b")
    d["resc"] = _read(f"{SD}/ed4_minority_rescue.csv", "ED4c")
    return d


# ── ED1 ──────────────────────────────────────────────────────────────────────

def draw_ed1a(ax, D):
    d = D["dataset_scale"].dropna(subset=["cells"]).sort_values("cells")
    y = np.arange(len(d))
    ax.barh(y, d["cells"], color=FOCAL, alpha=0.85, height=0.6)
    ax.set_yticks(y); ax.set_yticklabels(d["dataset"], fontsize=6)
    ax.set_xscale("log"); ax.set_xlabel("cells (log)")
    for i, (_, r) in enumerate(d.iterrows()):
        pert = (f"{int(r['perturbations'])} {r['type']}"
                if pd.notna(r["perturbations"]) else r["type"])
        ax.text(r["cells"] * 1.15, i, f"{int(r['cells']):,}\n{pert}", va="center",
                fontsize=5.2, color=INK)
    ax.set_xlim(1e4, 1e7)


def draw_ed1b(ax, D):
    ax.axis("off")
    defs = [("mean cosine", "cos(mean_treated - mean_ctrl)"),
            ("energy", "E-distance between distributions"),
            ("coverage (mean/worst)", "state-level NN coverage"),
            ("CMap cosine", "= mean cosine (identity)"),
            ("CMap WTCS", "rank-based connectivity (simplified)")]
    for i, (name, defn) in enumerate(defs):
        yy = 0.92 - i * 0.20
        col = COMP if ("mean" in name or "CMap" in name) else FOCAL
        ax.text(0.0, yy, name, fontsize=6.0, color=col, fontweight="bold",
                transform=ax.transAxes)
        ax.text(0.02, yy - 0.082, defn, fontsize=5.2, color=INK, transform=ax.transAxes,
                style="italic")


def draw_ed1c(ax, D):
    corr = D["corr"]
    lab = [METRIC_LABELS.get(m, m) for m in corr.columns]
    im = ax.imshow(corr.values, cmap=DIVMAP, vmin=-1, vmax=1, aspect="equal")
    ax.set_xticks(range(len(lab))); ax.set_xticklabels(lab, rotation=45, ha="right", fontsize=5.2)
    ax.set_yticks(range(len(lab))); ax.set_yticklabels(lab, fontsize=5.2)
    for i in range(len(lab)):
        for j in range(len(lab)):
            v = corr.values[i, j]
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=5.5,
                    color="white" if abs(v) > 0.6 else INK)
    cb = ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cb.set_label("Spearman rho", fontsize=5.5); cb.ax.tick_params(labelsize=5)


# ── ED2: the power defence ───────────────────────────────────────────────────

def _pw_row(pw, metric):
    sub = pw[(pw.metric == metric) & (pw.stratum == "Q4")] if "stratum" in pw.columns \
        else pw[pw.metric == metric]
    if sub.empty:
        raise KeyError(f"no Q4 power row for {metric!r}")
    return sub.iloc[0]


def draw_ed2a(ax, D):
    pw = D["pw"]
    metrics = ["minority_state_coverage", "moa_ndcg"]
    labels = ["minority coverage\n(task-proximal)", "MoA-nDCG\n(oracle-independent)"]
    pows = [float(_pw_row(pw, m)["achieved_power"]) for m in metrics]
    ax.bar(np.arange(2), pows, color=[FOCAL, COMP], alpha=0.85, width=0.6)
    ax.axhline(0.8, ls="--", lw=0.8, color=GREY)
    ax.text(1.45, 0.82, "80% power", fontsize=5.2, color=GREY, ha="right")
    for i, p in enumerate(pows):
        ax.text(i, p + 0.02 if p < 0.9 else p - 0.08, f"{p:.2f}", ha="center", fontsize=5.6,
                color="white" if p > 0.9 else INK, fontweight="bold")
    ax.set_xticks(np.arange(2)); ax.set_xticklabels(labels, fontsize=5.4)
    ax.set_ylabel("achieved power (Q4)"); ax.set_ylim(0, 1.05)


def draw_ed2b(ax, D):
    pw = D["pw"]
    metrics = ["minority_state_coverage", "moa_ndcg"]
    rows = [_pw_row(pw, m) for m in metrics]
    ns = [float(r["n_for_80pct_power"]) for r in rows]
    obs = [int(r["n"]) for r in rows]
    ax.bar(np.arange(2), ns, color=[FOCAL, COMP], alpha=0.85, width=0.6)
    for i, (n, o) in enumerate(zip(ns, obs)):
        ax.axhline(o, ls="--", lw=0.7, color=GREY, xmin=i / 2 + 0.06, xmax=i / 2 + 0.44)
        ax.text(i, n * 1.5 if n < 1000 else n * 1.05, f"{n:,.0f}", ha="center", fontsize=5.6,
                color=INK, fontweight="bold")
        ax.text(i, o * 0.62, f"observed n={o}", ha="center", fontsize=5.6, color=GREY)
    ax.set_yscale("log"); ax.set_xticks(np.arange(2))
    ax.set_xticklabels(["minority\ncoverage", "MoA-nDCG"], fontsize=5.6)
    ax.set_ylabel("n for 80% power (log)"); ax.set_ylim(10, 1e5)


def draw_ed2c(ax, D):
    """MoA-nDCG gap by divergence stratum. The annotation now matches the bars."""
    d = D["strat"]
    d = d[(d.metric == "moa_ndcg") & (d.stratum.isin(["Q1", "Q2", "Q3", "Q4"]))]
    x = np.arange(len(d))
    vals = d["mean_gap"].values
    qs = d["bh_qvalue"].values
    cols = [COMP if v < 0 else GREY for v in vals]
    ax.bar(x, vals, color=cols, alpha=0.85, width=0.62)
    ax.axhline(0, lw=0.6, color=INK)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{s}\ndiv={dm:.2f}" for s, dm in zip(d["stratum"], d["divergence_median"])],
                       fontsize=5.0)
    ax.set_ylabel("MoA-nDCG gain (DART $-$ mean)")
    lo, hi = float(min(vals)), float(max(vals))
    pad = max(abs(lo), abs(hi)) * 0.30
    ax.set_ylim(lo - pad, hi + pad)
    for i, (v, q) in enumerate(zip(vals, qs)):
        star = "*" if q < 0.05 else "ns"
        # keep the value label on the ZERO side of the bar tip, so it can never collide
        # with the x tick labels below the axis
        off = pad * 0.18
        ax.text(i, v + off if v < 0 else v + off, f"{v:+.3f} {star}", ha="center",
                va="bottom" if v < 0 else "bottom", fontsize=5.0, color=INK)
    ax.text(0.5, -0.40,
            "significantly negative at low divergence; no positive effect at any stratum",
            transform=ax.transAxes, ha="center", fontsize=5.0, color=GREY)


# ── ED3: identifiability ─────────────────────────────────────────────────────

def draw_ed3a(ax, D):
    med = D["med"].sort_values()
    y = np.arange(len(med))
    ax.barh(y, med.values, color=FOCAL, alpha=0.8, height=0.62)
    ax.axvline(0.5, ls="--", lw=0.9, color=COMP)
    ax.text(0.5, len(med) - 0.3, "ARI 0.5\n(reliable)", fontsize=5.0, color=COMP, ha="center")
    ax.set_yticks(y)
    ax.set_yticklabels([METHOD_DISP.get(str(c).replace("ari_", ""), str(c)) for c in med.index],
                       fontsize=5.0)
    ax.set_xlabel("median ARI vs true labels"); ax.set_xlim(0, 0.6)
    # The asterisk footnote (response-space k=2 is bit-identical to raw k=2 because k-means is
    # translation-invariant) is in the ED Fig. 3a caption; at 4.6 pt it broke the 5 pt floor.
    ax.text(float(med.max()) + 0.02, len(med) - 1, f"best {float(med.max()):.3f}",
            fontsize=5.2, color=INK, va="center")


def draw_ed3b(ax, D):
    subpop = D["subpop"]
    for i, ds in enumerate(["SciPlex3", "Frangieh"]):
        vals = subpop[subpop.dataset == ds]["sil_raw_k2"].dropna()
        if not len(vals):
            continue
        parts = ax.violinplot([vals], positions=[i], widths=0.7, showmedians=True)
        for pc in parts["bodies"]:
            pc.set_facecolor(FOCAL); pc.set_alpha(0.5)
        for key in ["cmedians", "cbars", "cmins", "cmaxes"]:
            if key in parts:
                parts[key].set_color(INK); parts[key].set_linewidth(0.8)
    ax.axhline(0.1, ls="--", lw=0.8, color=COMP)
    ax.text(1.45, 0.11, "sil 0.1", fontsize=5.0, color=COMP, ha="right")
    ax.set_xticks([0, 1]); ax.set_xticklabels(["SciPlex3\n(n=529)", "Frangieh\n(n=231)"], fontsize=5.4)
    ax.set_ylabel("silhouette (raw, k=2)"); ax.set_ylim(-0.15, 0.35)


def draw_ed3c(ax, D):
    """Structure is preserved; divergence is not. Replaces the retracted 5.1x panel."""
    sd, g1 = D["sd"], D["g1"]
    order = ["real_blend", "average_effect", "scgen", "nearest_neighbor"]
    disp = ["real", "avg-effect", "latent", "NN"]

    def pick(df, pred, col):
        synth = "real" if pred.startswith("real") else "cells"
        sub = df[(df.predictor == pred) & (df.synth == synth)]
        if sub.empty:
            raise KeyError(f"no row predictor={pred!r} synth={synth!r}; re-run "
                           f"exp09_structure_diagnostics.py --synth both")
        return float(sub[col].iloc[0])

    var = [pick(sd, p, "subpop_variance_ratio_mean") for p in order]
    cos = [pick(g1, p, "mean") for p in order]
    x = np.arange(len(order))
    ax.bar(x - 0.19, var, width=0.36, color=FOCAL, alpha=0.85, label="subpop var ratio")
    ax.bar(x + 0.19, cos, width=0.36, color=COMP, alpha=0.85,
           label=r"induced $\cos(d_{maj},d_{min})$")
    ax.axhline(var[0], ls="--", lw=0.8, color=FOCAL, alpha=0.7)
    ax.axhline(cos[0], ls=":", lw=0.8, color=COMP, alpha=0.7)
    ax.set_xticks(x); ax.set_xticklabels(disp, fontsize=5.4)
    ax.set_ylabel("value")
    ax.legend(fontsize=5.5, loc="upper left")
    ax.text(0.5, -0.34,
            "structure preserved (blue, flat); divergence lost (orange, rises)",
            transform=ax.transAxes, ha="center", fontsize=5.0, color=GREY)


def draw_ed3d(ax, D):
    g = D["pd_grid"].groupby(["separation_scale", "cells_per_source"])["ari_kmeans_k2"] \
        .mean().reset_index()
    piv = g.pivot(index="separation_scale", columns="cells_per_source", values="ari_kmeans_k2")
    im = ax.imshow(piv.values, cmap=DIVMAP, vmin=0, vmax=1, aspect="auto", origin="lower")
    ax.set_xticks(range(len(piv.columns))); ax.set_xticklabels(piv.columns, fontsize=5.0)
    ax.set_yticks(range(len(piv.index)))
    ax.set_yticklabels([f"{s:g}" for s in piv.index], fontsize=5.0)
    ax.set_xlabel("cells per source"); ax.set_ylabel("separation scale")
    if 1.0 in list(piv.index):
        ry = list(piv.index).index(1.0)
        ax.add_patch(plt.Rectangle((-0.5, ry - 0.5), len(piv.columns), 1, fill=False,
                                   edgecolor=INK, lw=1.2))
        ax.text(len(piv.columns) - 0.5, ry, " real", fontsize=5.0, color=INK, va="center")
    cb = ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cb.set_label("ARI", fontsize=5.2); cb.ax.tick_params(labelsize=5)


# ── ED4: exploratory ─────────────────────────────────────────────────────────

def draw_ed4a(ax, D):
    d = D["enr"].sort_values("high_minus_low")
    disp = {"IFN_response": "IFN response", "AXL_mesenchymal": "AXL/mesenchymal",
            "antigen_presentation": "antigen present.", "antigen_presentation_loss": "antigen loss",
            "quiescence": "quiescence"}
    y = np.arange(len(d))
    vals = d["high_minus_low"].values
    cols = [FOCAL if v > 0 else COMP for v in vals]
    ax.barh(y, vals, color=cols, alpha=0.85, height=0.6)
    ax.axvline(0, lw=0.6, color=INK)
    ax.set_yticks(y)
    ax.set_yticklabels([disp.get(p, p) for p in d["program"]], fontsize=5.4)
    ax.set_xlabel("enrichment (high $-$ low divergence)")
    for i, (v, p) in enumerate(zip(vals, d["mannwhitney_p"])):
        star = "***" if p < 1e-3 else ("**" if p < 1e-2 else ("*" if p < 0.05 else "ns"))
        ax.text(v + (0.003 if v > 0 else -0.003), i, star, va="center",
                ha="left" if v > 0 else "right", fontsize=5.2, color=INK)
    # CAVEAT MOVED TO CAPTION, NOT DROPPED. The quiescence program carries the largest-magnitude
    # enrichment and its sign here is negative; the exploratory status of every signal, and the
    # fact that the quiescence sign is not stable across runs (Supplementary Note 3), must be
    # stated in the ED Fig. 4 caption. The in-panel sentence was 4.8 pt, below the 5 pt floor.


def draw_ed4b(ax, D):
    from scipy.stats import pearsonr
    d = D["mrk"].dropna(subset=["response_divergence"])
    cc = "prog_AXL_mesenchymal_minority_minus_majority"
    ax.scatter(d["response_divergence"], d[cc], s=4, color=FOCAL, alpha=0.35, edgecolors="none")
    r, pv = pearsonr(d["response_divergence"], d[cc])
    z = np.polyfit(d["response_divergence"], d[cc], 1)
    xs = np.linspace(d["response_divergence"].min(), d["response_divergence"].max(), 50)
    ax.plot(xs, np.polyval(z, xs), color=INK, lw=1.0)
    ax.text(0.05, 0.92, f"Pearson r={r:.3f}\np={pv:.1e}", transform=ax.transAxes,
            fontsize=5.4, color=INK, va="top")
    ax.set_xlabel("response divergence"); ax.set_ylabel("AXL/mesenchymal enrichment")


def draw_ed4c(ax, D):
    d = D["resc"].dropna(subset=["mean_top_minority_cov", "dart_top_minority_cov"])
    ax.scatter(d["mean_top_minority_cov"], d["dart_top_minority_cov"], s=10, color=FOCAL,
               alpha=0.7, edgecolors="none")
    lim = [0, max(d["mean_top_minority_cov"].max(), d["dart_top_minority_cov"].max()) * 1.1]
    ax.plot(lim, lim, ls="--", lw=0.8, color=GREY)
    ax.set_xlabel("mean-pick minority coverage"); ax.set_ylabel("DART-pick minority coverage")
    ax.set_xlim(lim); ax.set_ylim(lim); ax.set_aspect("equal")
    ax.text(0.05, 0.9, f"n={len(d)} queries\nnear-null rescue", transform=ax.transAxes,
            fontsize=5.2, color=GREY, va="top")


# ── assemble ─────────────────────────────────────────────────────────────────

FIGS = {
    "ed1_reproducibility": (["a", "b", "c"], [draw_ed1a, draw_ed1b, draw_ed1c], (10.2, 3.0)),
    "ed2_classB_robustness": (["a", "b", "c"], [draw_ed2a, draw_ed2b, draw_ed2c], (10.2, 3.2)),
    "ed3_identifiability": (["a", "b", "c", "d"],
                            [draw_ed3a, draw_ed3b, draw_ed3c, draw_ed3d], (12.6, 3.2)),
    "ed4_resistance_exploratory": (["a", "b", "c"],
                                   [draw_ed4a, draw_ed4b, draw_ed4c], (10.2, 3.2)),
}


def main():
    apply_style(sizes=(8, 7, 6))
    D = load()
    for stem, (letters, fns, figsize) in FIGS.items():
        fig, axes = plt.subplots(1, len(fns), figsize=figsize)
        for ax, letter, fn in zip(np.atleast_1d(axes), letters, fns):
            fn(ax, D)
            panel_letter(ax, letter, case="lower")
        fig.tight_layout()
        fig.savefig(os.path.join(OUT, f"{stem}.png"), dpi=300, bbox_inches="tight")
        fig.savefig(os.path.join(OUT, f"{stem}.pdf"), bbox_inches="tight")
        plt.close(fig)
        print(f"wrote {stem}.{{png,pdf}}")


if __name__ == "__main__":
    main()
