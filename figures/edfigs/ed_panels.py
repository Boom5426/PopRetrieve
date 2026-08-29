"""PopRetrieve Extended Data figures (ED1-ED4), each blocking one anticipated reviewer attack.

PANEL LIBRARY ONLY SINCE 2026-08-29. The four figures assembled by FIGS at the bottom of this file
are superseded: edfigs/ed_consolidated.py now draws the whole Extended Data deck, importing the
draw functions here. Where each one went:
    draw_ed1c -> ED1a    draw_ed1d -> ED1b    draw_ed1e -> ED1c
    draw_ed2a -> ED1d    draw_ed2b -> ED1e
    draw_ed3a -> ED2a    draw_ed3b -> ED2b    draw_ed3d -> ED2c
    draw_ed1a, draw_ed1b, draw_ed2c, draw_ed3c   DELETED, see ed_consolidated.py for what carries
                                                 each one instead
    draw_ed4a-c   never deployed; the real ED4 was always ed4/ed4_zhao_robustness.py
Running this file still writes its own previews, which nothing references. Keep FIGS in step with
the draw functions or delete it; do not treat its output as the shipped figures.

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
  low divergence the effect runs against PopRetrieve.

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

from figstyle import FOCAL_SOFT, COMP_SOFT, GREY, INK, PT_MATH, apply_style, panel_letter, DIVMAP_SOFT, soften_axes, META  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

# The divergent map is imported, not rebuilt. Two local copies of it existed, and a
# recolour of FOCAL/COMP moved the figures that imported it while leaving these two
# behind: the same failure the palette itself had.
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
    # The two GMM columns are stored as gmm2_*, not gmm_k2, so they matched nothing and the
    # `.get(key, key)` fallback silently printed the raw dataframe column names "ari_gmm2_raw" and
    # "ari_gmm2_pca50" onto ED3a's y axis in the shipped figure (audited 2026-07-27).
    "gmm2_raw": "GMM k=2", "gmm2_pca50": "PCA-50 + GMM",
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

    # ED1d/ED1e are the two panels that used to be main-text Figure 2. They read exp06
    # (the degenerate-limit experiment) directly from results/, which is the source of truth;
    # no source_data mirror is introduced for them.
    d["deg"] = _read(f"{RES}/exp06_theory_limits/degenerate_limit_synthetic.csv", "ED1d")
    d["beta"] = _read(f"{RES}/exp06_theory_limits/beta_interpolation.csv", "ED1e")

    d["enr"] = _read(f"{SD}/ed4_enrichment_summary.csv", "ED4a")
    d["mrk"] = _read(f"{SD}/ed4_marker_enrichment.csv", "ED4b")
    d["resc"] = _read(f"{SD}/ed4_minority_rescue.csv", "ED4c")
    return d


# ── ED1 ──────────────────────────────────────────────────────────────────────

def draw_ed1a(ax, D):
    d = D["dataset_scale"].dropna(subset=["cells"]).sort_values("cells")
    y = np.arange(len(d))
    ax.barh(y, d["cells"], color=FOCAL_SOFT, alpha=0.85, height=0.6)
    ax.set_yticks(y); ax.set_yticklabels(d["dataset"], fontsize=6)
    # PT_MATH on a log axis: LogFormatter writes each tick as mathtext ("$10^{4}$") and
    # matplotlib prints the exponent at 0.7x nominal, so the deck's 6 pt ticks printed their
    # exponents at 4.2 pt, under the 5 pt floor. Same rule as figure 2e.
    ax.set_xscale("log"); ax.set_xlabel("cells (log)")
    ax.tick_params(axis="x", labelsize=PT_MATH)
    for i, (_, r) in enumerate(d.iterrows()):
        pert = (f"{int(r['perturbations'])} {r['type']}"
                if pd.notna(r["perturbations"]) else r["type"])
        ax.text(r["cells"] * 1.15, i, f"{int(r['cells']):,}\n{pert}", va="center",
                fontsize=5.2, color=INK)
    ax.set_xlim(1e4, 1e7)


def draw_ed1b(ax, D):
    ax.axis("off")
    # The colour is assigned per metric, not inferred from the label text. The rule used to be
    # `COMP_SOFT if "mean" in name or "CMap" in name`, which painted "coverage (mean/worst)" orange
    # because the word "mean" appears in its name. Coverage is a population score, and orange is
    # reserved deck-wide for the mean/collapse family, so the
    # substring rule contradicted the rest of the deck about what kind of score this is.
    defs = [("mean cosine", "cos(mean_treated - mean_ctrl)", COMP_SOFT),
            ("energy", "E-distance between distributions", FOCAL_SOFT),
            ("coverage (mean/worst)", "state-level NN coverage", FOCAL_SOFT),
            ("CMap cosine", "= mean cosine (identity)", COMP_SOFT),
            ("CMap WTCS", "rank-based connectivity (simplified)", COMP_SOFT)]
    # Swatch, then the name in ink. This panel is a key, so the family binding has to be visible
    # somewhere; the deck rule puts it on a mark rather than on the letterforms, which is also
    # what keeps every glyph here above the contrast floor.
    for i, (name, defn, col) in enumerate(defs):
        yy = 0.92 - i * 0.20
        ax.add_patch(Rectangle((0.0, yy - 0.018), 0.045, 0.038, color=col, lw=0,
                               transform=ax.transAxes, clip_on=False))
        ax.text(0.065, yy, name, fontsize=6.0, color=INK, fontweight="bold",
                transform=ax.transAxes)
        ax.text(0.085, yy - 0.082, defn, fontsize=5.2, color=META, transform=ax.transAxes,
                style="italic")


def draw_ed1c(ax, D):
    corr = D["corr"]
    lab = [METRIC_LABELS.get(m, m) for m in corr.columns]
    im = ax.imshow(corr.values, cmap=DIVMAP_SOFT, vmin=-1, vmax=1, aspect="equal")
    # Vertical, not 45 degrees. Six columns share about 2 in, i.e. 0.33 in each, and "CMap WTCS"
    # is 0.42 in at 5.2 pt: at 45 degrees consecutive labels overlapped by up to 39% of their
    # own width. Rotated fully upright a label costs only its glyph height horizontally.
    ax.set_xticks(range(len(lab)))
    ax.set_xticklabels(lab, rotation=90, ha="center", va="top", fontsize=5.2)
    ax.set_yticks(range(len(lab))); ax.set_yticklabels(lab, fontsize=5.2)
    for i in range(len(lab)):
        for j in range(len(lab)):
            v = corr.values[i, j]
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=5.5,
                    color="white" if abs(v) > 0.6 else INK)
    cb = ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cb.set_label("Spearman $\\rho$", fontsize=5.5); cb.ax.tick_params(labelsize=5)


def draw_ed1d(ax, D):
    """Population distance converges to its mean-only endpoint as the residual vanishes.

    Was main-text Fig. 2c, with Fig. 2b surviving as the schematic inset. Source:
    results/exp06_theory_limits/degenerate_limit_synthetic.csv, rows prop1_spread. The dashed
    rule is the two_dmu column (the mean-to-mean distance), constant by construction; the claim
    of the panel is that the measured energy distance MEETS it at lambda = 0.
    """
    sp = (D["deg"].query("prop == 'prop1_spread'").dropna(subset=["t_spread"])
          .sort_values("t_spread"))
    floor = float(sp["two_dmu"].iloc[0])
    lam, energy = sp["t_spread"].to_numpy(), sp["energy"].to_numpy()

    ax.axhline(floor, ls="--", lw=0.7, color=COMP_SOFT, zorder=1)
    ax.plot(lam, energy, "-", color=FOCAL_SOFT, lw=1.0, zorder=3)
    ax.plot(lam[1:], energy[1:], "o", color=FOCAL_SOFT, ms=2.8, zorder=3)
    # the lambda = 0 endpoint carries the claim, so it is the emphasised marker
    ax.plot([lam[0]], [energy[0]], "o", color=FOCAL_SOFT, ms=4.2, mec="white", mew=0.7, zorder=5)

    ax.text(1.02, floor + 1.4, f"mean-distance endpoint  {floor:.2f}", ha="right", va="bottom",
            fontsize=5.6, color=INK)
    ax.annotate(f"$\\lambda=0$:  {energy[0]:.2f}",
                xy=(lam[0], energy[0]), xytext=(0.30, energy[0] - 8.0),
                fontsize=5.6, color=INK, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", lw=0.6, color=FOCAL_SOFT, shrinkA=2, shrinkB=4))

    # NO SCHEMATIC INSET. Main-text Fig. 2b (seeded gaussian clouds at four values of lambda,
    # sharing one mean) was tried here as an inset and removed: unframed schematic points sitting
    # inside a data axes read as stray measurements, and framing them costs more space than the
    # cartoon is worth. What lambda does is defined in the main text and in Methods, and the x
    # axis of this panel is lambda itself.

    ax.set_xlabel(r"residual scale $\lambda$")
    ax.set_ylabel("energy distance")
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(28, 108)
    ax.set_yticks([40, 60, 80, 100])
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)


def draw_ed1e(ax, D):
    """One temperature interpolates mean aggregation to worst-case emphasis.

    Was main-text Fig. 2e. Source: results/exp06_theory_limits/beta_interpolation.csv. The two
    dashed rules are the mean and max columns, which are the analytic beta -> 0 and beta -> inf
    endpoints of coverage_aggregate; the plotted curve is the measured D_beta between them.
    """
    b = D["beta"].sort_values("beta")
    mlo, mhi = float(b["mean"].iloc[0]), float(b["max"].iloc[0])

    ax.axhline(mlo, ls="--", lw=0.7, color=COMP_SOFT, zorder=1)
    ax.axhline(mhi, ls="--", lw=0.7, color="0.45", zorder=1)
    ax.plot(np.clip(b["beta"], 1e-3, 1e3), b["D_beta"], "-o", color=FOCAL_SOFT, ms=2.6, lw=1.0,
            zorder=3)

    ax.text(1.1e-3, mhi + 0.012, f"worst case, $\\beta\\to\\infty$   {mhi:.3f}",
            ha="left", va="bottom", fontsize=5.6, color="0.35")
    ax.text(1.1e-3, mlo - 0.028, f"mean aggregation, $\\beta\\to0$   {mlo:.4f}",
            ha="left", va="top", fontsize=5.6, color=INK)

    ax.set_xscale("log")
    ax.set_xlim(8e-4, 2.2e3)
    ax.set_xticks([1e-3, 1e-1, 1e1, 1e3])
    # PT_MATH on this axis for the same reason as ED1a: LogFormatter emits mathtext and
    # matplotlib prints an exponent at 0.7x nominal.
    ax.tick_params(axis="x", labelsize=PT_MATH)
    ax.set_ylim(mlo - 0.095, mhi + 0.055)
    ax.set_yticks([0.7, 0.9, 1.1, 1.3])
    ax.set_xlabel(r"coverage temperature $\beta$")
    ax.set_ylabel(r"aggregate distance $D_\beta$", fontsize=PT_MATH)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)


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
    labels = ["minority coverage\n(task-proximal)", "MoA-nDCG\n(mechanism recovery)"]
    pows = [float(_pw_row(pw, m)["achieved_power"]) for m in metrics]
    ax.bar(np.arange(2), pows, color=[FOCAL_SOFT, COMP_SOFT], alpha=0.85, width=0.6)
    ax.axhline(0.8, ls="--", lw=0.8, color=GREY)
    ax.text(1.45, 0.82, "80% power", fontsize=5.2, color=GREY, ha="right")
    for i, p in enumerate(pows):
        ax.text(i, p + 0.02 if p < 0.9 else p - 0.08, f"{p:.2f}", ha="center", fontsize=5.6,
                color="white" if p > 0.9 else INK)
    ax.set_xticks(np.arange(2)); ax.set_xticklabels(labels, fontsize=5.4)
    ax.set_ylabel("achieved power (Q4)"); ax.set_ylim(0, 1.05)


def draw_ed2b(ax, D):
    pw = D["pw"]
    metrics = ["minority_state_coverage", "moa_ndcg"]
    rows = [_pw_row(pw, m) for m in metrics]
    ns = [float(r["n_for_80pct_power"]) for r in rows]
    obs = [int(r["n"]) for r in rows]
    ax.bar(np.arange(2), ns, color=[FOCAL_SOFT, COMP_SOFT], alpha=0.85, width=0.6)
    for i, (n, o) in enumerate(zip(ns, obs)):
        ax.axhline(o, ls="--", lw=0.7, color=GREY, xmin=i / 2 + 0.06, xmax=i / 2 + 0.44)
        ax.text(i, n * 1.5 if n < 1000 else n * 1.05, f"{n:,.0f}", ha="center", fontsize=5.6,
                color=INK)
        ax.text(i, o * 0.62, f"observed n={o}", ha="center", fontsize=5.6, color=GREY)
    ax.set_yscale("log"); ax.set_xticks(np.arange(2))
    ax.tick_params(axis="y", labelsize=PT_MATH)   # see the note on the log axis in ed1a
    ax.set_xticklabels(["minority\ncoverage", "MoA-nDCG"], fontsize=5.6)
    # Upper limit 6e4, not 1e5: the largest value is 20,844, so the 10^5 decade held no data and
    # its tick label sat under panel b's own letter.
    ax.set_ylabel("n for 80% power (log)"); ax.set_ylim(10, 6e4)


def draw_ed2c(ax, D):
    """MoA-nDCG gap by divergence stratum. The annotation now matches the bars."""
    d = D["strat"]
    d = d[(d.metric == "moa_ndcg") & (d.stratum.isin(["Q1", "Q2", "Q3", "Q4"]))]
    x = np.arange(len(d))
    vals = d["mean_gap"].values
    qs = d["bh_qvalue"].values
    cols = [COMP_SOFT if v < 0 else GREY for v in vals]
    ax.bar(x, vals, color=cols, alpha=0.85, width=0.62)
    ax.axhline(0, lw=0.6, color=INK)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{s}\ndiv={dm:.2f}" for s, dm in zip(d["stratum"], d["divergence_median"])],
                       fontsize=5.0)
    ax.set_ylabel("MoA-nDCG gain\n(distributional $-$ mean)")
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
    # THE FOOTER LINE IS IN THE CAPTION. ED2c: this sentence is already the last sentence of this figure's own caption, and it was set at
    # 5.0 pt, sitting exactly on the production floor.


# ── ED3: identifiability ─────────────────────────────────────────────────────

def draw_ed3a(ax, D):
    med = D["med"].sort_values()
    y = np.arange(len(med))
    ax.barh(y, med.values, color=FOCAL_SOFT, alpha=0.8, height=0.62)
    ax.axvline(0.5, ls="--", lw=0.9, color=COMP_SOFT)
    ax.text(0.5, len(med) - 0.3, "ARI 0.5\n(reliable)", fontsize=5.0, color=INK, ha="center")
    ax.set_yticks(y)
    # No silent fallback: an unmapped key used to be printed verbatim as a tick label, which is
    # how "ari_gmm2_raw" reached the published figure. Fail instead, and say which key is missing.
    keys = [str(c).replace("ari_", "") for c in med.index]
    unmapped = [k for k in keys if k not in METHOD_DISP]
    if unmapped:
        raise KeyError(
            f"ED3a: no display name for {unmapped} in METHOD_DISP. Add them rather than letting "
            f"the raw column name be printed on the axis.")
    ax.set_yticklabels([METHOD_DISP[k] for k in keys], fontsize=5.0)
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
            pc.set_facecolor(FOCAL_SOFT); pc.set_alpha(0.5)
        for key in ["cmedians", "cbars", "cmins", "cmaxes"]:
            if key in parts:
                parts[key].set_color(INK); parts[key].set_linewidth(0.8)
    ax.axhline(0.1, ls="--", lw=0.8, color=COMP_SOFT)
    ax.text(1.45, 0.11, "sil 0.1", fontsize=5.0, color=INK, ha="right")
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
    ax.bar(x - 0.19, var, width=0.36, color=FOCAL_SOFT, alpha=0.85, label="subpop var ratio")
    ax.bar(x + 0.19, cos, width=0.36, color=COMP_SOFT, alpha=0.85,
           label=r"induced $\cos(d_{maj},d_{min})$")
    ax.axhline(var[0], ls="--", lw=0.8, color=FOCAL_SOFT, alpha=0.7)
    ax.axhline(cos[0], ls=":", lw=0.8, color=COMP_SOFT, alpha=0.7)
    ax.set_xticks(x); ax.set_xticklabels(disp, fontsize=5.4)
    ax.set_ylabel("value")
    ax.legend(fontsize=5.5, loc="upper left")
    # THE FOOTER LINE IS IN THE CAPTION. ED3c: a colour key in words, now stated in the caption's entry c, and it was set at
    # 5.0 pt, sitting exactly on the production floor.


def draw_ed3d(ax, D):
    g = D["pd_grid"].groupby(["separation_scale", "cells_per_source"])["ari_kmeans_k2"] \
        .mean().reset_index()
    piv = g.pivot(index="separation_scale", columns="cells_per_source", values="ari_kmeans_k2")
    im = ax.imshow(piv.values, cmap=DIVMAP_SOFT, vmin=0, vmax=1, aspect="auto", origin="lower")
    ax.set_xticks(range(len(piv.columns))); ax.set_xticklabels(piv.columns, fontsize=5.0)
    ax.set_yticks(range(len(piv.index)))
    ax.set_yticklabels([f"{s:g}" for s in piv.index], fontsize=5.0)
    ax.set_xlabel("cells per source"); ax.set_ylabel("separation scale")
    if 1.0 in list(piv.index):
        ry = list(piv.index).index(1.0)
        ax.add_patch(plt.Rectangle((-0.5, ry - 0.5), len(piv.columns), 1, fill=False,
                                   edgecolor=INK, lw=1.2))
        # right-aligned INSIDE the highlighted row: set to its left with a leading space it
        # started at the last cell's right edge and was clipped by the axes.
        ax.text(len(piv.columns) - 0.62, ry, "real", fontsize=5.0, color=INK, va="center",
                ha="right")
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
    cols = [FOCAL_SOFT if v > 0 else COMP_SOFT for v in vals]
    ax.barh(y, vals, color=cols, alpha=0.85, height=0.6)
    ax.axvline(0, lw=0.6, color=INK)
    ax.set_yticks(y)
    ax.set_yticklabels([disp.get(p, p) for p in d["program"]], fontsize=5.4)
    ax.set_xlabel("enrichment (high $-$ low divergence)")
    for i, (v, p) in enumerate(zip(vals, d["mannwhitney_p"])):
        star = "***" if p < 1e-3 else ("**" if p < 1e-2 else ("*" if p < 0.05 else "ns"))
        ax.text(v + (0.003 if v > 0 else -0.003), i, star, va="center",
                ha="left" if v > 0 else "right", fontsize=5.2, color=INK)
    # Room for the stars on both flanks. The quiescence bar is the longest and negative, so its
    # "***" was set past the left end of the data range and printed on top of the tick labels.
    ax.margins(x=0.14)
    # CAVEAT MOVED TO CAPTION, NOT DROPPED. The quiescence program carries the largest-magnitude
    # enrichment and its sign here is negative; the exploratory status of every signal, and the
    # fact that the quiescence sign is not stable across runs (Supplementary Note 3), must be
    # stated in the ED Fig. 4 caption. The in-panel sentence was 4.8 pt, below the 5 pt floor.


def draw_ed4b(ax, D):
    from scipy.stats import pearsonr
    d = D["mrk"].dropna(subset=["response_divergence"])
    cc = "prog_AXL_mesenchymal_minority_minus_majority"
    ax.scatter(d["response_divergence"], d[cc], s=4, color=FOCAL_SOFT, alpha=0.35, edgecolors="none")
    r, pv = pearsonr(d["response_divergence"], d[cc])
    z = np.polyfit(d["response_divergence"], d[cc], 1)
    xs = np.linspace(d["response_divergence"].min(), d["response_divergence"].max(), 50)
    ax.plot(xs, np.polyval(z, xs), color=INK, lw=1.0)
    ax.text(0.05, 0.92, f"Pearson r={r:.3f}\np={pv:.1e}", transform=ax.transAxes,
            fontsize=5.4, color=INK, va="top")
    ax.set_xlabel("response divergence"); ax.set_ylabel("AXL/mesenchymal enrichment")


def draw_ed4c(ax, D):
    d = D["resc"].dropna(subset=["mean_top_minority_cov", "dart_top_minority_cov"])
    ax.scatter(d["mean_top_minority_cov"], d["dart_top_minority_cov"], s=10, color=FOCAL_SOFT,
               alpha=0.7, edgecolors="none")
    lim = [0, max(d["mean_top_minority_cov"].max(), d["dart_top_minority_cov"].max()) * 1.1]
    ax.plot(lim, lim, ls="--", lw=0.8, color=GREY)
    ax.set_xlabel("mean-pick minority coverage"); ax.set_ylabel("distributional-pick\nminority coverage")
    ax.set_xlim(lim); ax.set_ylim(lim); ax.set_aspect("equal")
    ax.text(0.05, 0.9, f"n={len(d)} queries\nnear-null rescue", transform=ax.transAxes,
            fontsize=5.2, color=GREY, va="top")


# ── assemble ─────────────────────────────────────────────────────────────────

# AUTHORED AT THE PRINTED WIDTH, like the main deck. The SI text block is 6.93 in and every
# Extended Data figure enters with \includegraphics[width=\textwidth], so a canvas wider than that
# is silently scaled DOWN and every nominal point size shrinks with it. These four were declared at
# 10.2-12.6 in, i.e. printed at 0.55-0.68x, which put 5 pt source text at 2.75-3.39 pt on the page,
# far under the Nature Portfolio 5 pt floor, and no gate reported it because assert_min_fontsize
# measures the NOMINAL size. At 6.9 in the scale factor is 1.0 and nominal size == printed size.
#
# Width had to be paid for in height and, for ED3, in structure: four panels across a 6.9 in canvas
# leaves 1.7 in each, which is narrower than several of that figure's own axis labels, so ED3 is a
# 2 x 2 grid. The other three keep one row and gain height instead.
#
# name: (letters, draw functions, figsize, (nrows, ncols)[, spans])
#
# ED1 carries an optional fifth element. It has five panels in two rows of UNEQUAL width (three
# across the top, two across the bottom), which plt.subplots cannot express: a (2, 3) grid would
# leave a hole at the bottom right, and a (1, 5) row gives each panel 1.38 in, narrower than
# several of ED1a's own labels. The spans list places each panel on a shared 6-column gridspec,
# so the top row is three 2-column panels and the bottom row is two 3-column panels.
FIGS = {
    "ed1_reproducibility": (["a", "b", "c", "d", "e"],
                            [draw_ed1a, draw_ed1b, draw_ed1c, draw_ed1d, draw_ed1e],
                            (6.9, 4.62), (2, 6),
                            [(0, slice(0, 2)), (0, slice(2, 4)), (0, slice(4, 6)),
                             (1, slice(0, 3)), (1, slice(3, 6))]),
    "ed2_classB_robustness": (["a", "b", "c"], [draw_ed2a, draw_ed2b, draw_ed2c], (6.9, 2.6),
                              (1, 3)),
    "ed3_identifiability": (["a", "b", "c", "d"],
                            [draw_ed3a, draw_ed3b, draw_ed3c, draw_ed3d], (6.9, 4.6), (2, 2)),
    # NOT Extended Data Fig. 4, and not deployed. Until 2026-08-29 build_ed.py shipped this
    # figure under the ED4 caption, which describes compartment-assignment validation and
    # threshold robustness in ZhaoSims2021; that figure is ed4/ed4_zhao_robustness.py and is now
    # what ED4 builds. Nothing in the manuscript or the SI references the content below, so it
    # is kept buildable and unreferenced rather than deleted.
    "ed4_resistance_exploratory": (["a", "b", "c"],
                                   [draw_ed4a, draw_ed4b, draw_ed4c], (6.9, 2.6), (1, 3)),
}


def main():
    apply_style(sizes=(8, 7, 6))
    D = load()
    for stem, spec in FIGS.items():
        letters, fns, figsize, (nr, nc) = spec[:4]
        spans = spec[4] if len(spec) > 4 else None
        fig = plt.figure(figsize=figsize)
        if spans is None:
            axes = fig.subplots(nr, nc)
            axes = list(np.asarray(axes).ravel())
        else:
            gs = fig.add_gridspec(nr, nc)
            axes = [fig.add_subplot(gs[r, cs]) for r, cs in spans]
        assert len(axes) == len(letters) == len(fns), \
            f"{stem}: {len(axes)} axes for {len(letters)} letters and {len(fns)} draw functions"
        for ax, letter, fn in zip(axes, letters, fns):
            fn(ax, D)
            panel_letter(ax, letter, case="lower")
        soften_axes(fig)
        fig.tight_layout()
        fig.savefig(os.path.join(OUT, f"{stem}.png"), dpi=300, bbox_inches="tight")
        fig.savefig(os.path.join(OUT, f"{stem}.pdf"), bbox_inches="tight")
        plt.close(fig)
        print(f"wrote {stem}.{{png,pdf}}")


if __name__ == "__main__":
    main()
