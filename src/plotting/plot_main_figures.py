#!/usr/bin/env python
"""Main figures 1-6 for "Distributional Inverse Drug Retrieval for Heterogeneous
Single-Cell Populations" (plan Phase 4).

Turns the reproduced result CSVs (results/exp0*/) into publication figures. Each
figure is written as PDF **and** SVG to results/main_figures/, and the exact plotted
values are exported to results/main_figures/source_data/. No new experiments, no
fabricated data: every data panel reads an existing CSV; schematic panels are clearly
labelled as such. SVG text is kept as editable text (svg.fonttype='none') and PDF uses
TrueType (pdf.fonttype=42) so panels can be refined downstream (Image2). Set
DIDR_FIG_PNG=<dir> to also dump PNG previews.

    python src/plotting/plot_main_figures.py            # all
    python src/plotting/plot_main_figures.py 2 5        # only fig2, fig5
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

PKG = Path(__file__).resolve().parents[2]
RES = PKG / "results"
OUT = RES / "main_figures"
SRC = OUT / "source_data"

# ----------------------------- style -----------------------------
plt.rcParams.update({
    "figure.dpi": 120,
    "savefig.bbox": "tight",
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans"],
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.titleweight": "bold",
    "axes.labelsize": 9.5,
    "axes.linewidth": 0.9,
    "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5,
    "legend.fontsize": 8,
    "legend.frameon": False,
    "svg.fonttype": "none",       # editable text in SVG
    "pdf.fonttype": 42,           # TrueType in PDF
})

COL = {
    "mean_cosine": "#C44E52",     # incumbent (fails under divergence)
    "global_energy": "#4C72B0",   # ours (primary)
    "coverage_mean": "#55A868",
    "coverage_worst": "#8172B3",
    "energy": "#4C72B0",
    "mmd": "#DD8452",
    "sliced_w": "#8C8C8C",
}
LAB = {
    "mean_cosine": "Mean cosine (incumbent)",
    "global_energy": "Global energy (ours)",
    "coverage_mean": "Coverage (mean)",
    "coverage_worst": "Coverage (worst)",
    "energy": "Energy",
    "mmd": "RBF-MMD",
    "sliced_w": "Sliced-Wasserstein",
}
DSCOL = {"cross-line": "#4C72B0", "Frangieh immune": "#DD8452", "CD34+ lineages": "#55A868"}
SC4 = ["mean_cosine", "global_energy", "coverage_mean", "coverage_worst"]
GATE = 0.9


# ----------------------------- helpers -----------------------------

def L(rel):
    return pd.read_csv(RES / rel)


def despine(ax, which=("top", "right")):
    for s in which:
        ax.spines[s].set_visible(False)


def panel(ax, letter):
    ax.text(-0.16, 1.07, letter, transform=ax.transAxes, fontsize=13,
            fontweight="bold", va="top", ha="right")


def save_source(df, name):
    SRC.mkdir(parents=True, exist_ok=True)
    df.to_csv(SRC / name, index=False)


def save_fig(fig, stem):
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "svg"):
        fig.savefig(OUT / f"{stem}.{ext}")
    png = os.environ.get("DIDR_FIG_PNG")
    if png:
        Path(png).mkdir(parents=True, exist_ok=True)
        fig.savefig(Path(png) / f"{stem}.png", dpi=150)
    plt.close(fig)
    print(f"  wrote {stem}.pdf / .svg")


def _cloud(ax, cx, cy, color, n=60, spread=0.20, seed=0):
    r = np.random.default_rng(seed)
    ax.scatter(cx + r.normal(0, spread, n), cy + r.normal(0, spread, n),
               s=7, color=color, alpha=0.55, linewidths=0)


def _schematic_note(ax, txt):
    ax.text(0.5, -0.02, txt, transform=ax.transAxes, ha="center", va="top",
            fontsize=7.5, style="italic", color="#666666")


# ----------------------------- Figure 1 -----------------------------

def fig1():
    fig = plt.figure(figsize=(12.2, 6.4))
    gs = fig.add_gridspec(2, 3, hspace=0.5, wspace=0.42,
                          height_ratios=[1, 1])
    fig.suptitle("Distributional inverse drug retrieval for heterogeneous cellular populations",
                 fontsize=12, fontweight="bold", y=1.0)

    # A forward vs inverse (schematic)
    axA = fig.add_subplot(gs[0, 0]); axA.axis("off"); panel(axA, "A")
    axA.set_title("Forward vs. inverse", loc="left")
    for y, txt, fc in [(0.66, "Forward:  drug + control  →  predicted states", "#EDEDED"),
                       (0.28, "Inverse (this work):  query population  →  ranked drugs", "#DCE6F2")]:
        axA.add_patch(FancyBboxPatch((0.03, y), 0.94, 0.24, transform=axA.transAxes,
                                     boxstyle="round,pad=0.02", fc=fc, ec="#888"))
        axA.text(0.5, y + 0.12, txt, transform=axA.transAxes, ha="center", va="center", fontsize=8.3)
    axA.annotate("", xy=(0.5, 0.55), xytext=(0.5, 0.60), xycoords="axes fraction",
                 arrowprops=dict(arrowstyle="-|>", color="#444"))
    _schematic_note(axA, "schematic")

    # B mean collapse (schematic)
    axB = fig.add_subplot(gs[0, 1]); panel(axB, "B")
    axB.set_title("Mean collapses subpopulations", loc="left")
    _cloud(axB, 0.32, 0.62, COL["mean_cosine"], seed=1)
    _cloud(axB, 0.70, 0.34, COL["global_energy"], seed=2)
    axB.plot(0.51, 0.48, "X", ms=15, color="black")
    axB.text(0.51, 0.40, "mean", ha="center", fontsize=8)
    axB.text(0.32, 0.86, "subpop 1", ha="center", fontsize=7.5, color=COL["mean_cosine"])
    axB.text(0.70, 0.10, "subpop 2", ha="center", fontsize=7.5, color=COL["global_energy"])
    axB.set_xlim(0, 1); axB.set_ylim(0, 1); axB.set_xticks([]); axB.set_yticks([])
    _schematic_note(axB, "schematic")

    # C distributional matching (schematic)
    axC = fig.add_subplot(gs[0, 2]); panel(axC, "C")
    axC.set_title("Distributional matching", loc="left")
    _cloud(axC, 0.32, 0.5, "#666", n=70, spread=0.16, seed=3)
    _cloud(axC, 0.72, 0.5, COL["global_energy"], n=70, spread=0.16, seed=4)
    axC.annotate("", xy=(0.60, 0.5), xytext=(0.44, 0.5), xycoords="axes fraction",
                 arrowprops=dict(arrowstyle="<|-|>", color="#333"))
    axC.text(0.52, 0.60, r"$\mathcal{D}(P_d, Q)$", ha="center", fontsize=10)
    axC.text(0.32, 0.14, "query Q", ha="center", fontsize=8)
    axC.text(0.72, 0.14, "candidate $P_d$", ha="center", fontsize=8)
    axC.set_xlim(0, 1); axC.set_ylim(0, 1); axC.set_xticks([]); axC.set_yticks([])
    _schematic_note(axC, "schematic")

    # D ranking flip (schematic, single column)
    axD = fig.add_subplot(gs[1, 0]); axD.axis("off"); panel(axD, "D")
    axD.set_title("Ranking flip", loc="left")
    axD.text(0.04, 0.80, "Mean cosine picks", fontsize=8.5, color="#555")
    axD.text(0.10, 0.66, "majority-biased drug  ✗", fontsize=9, color=COL["mean_cosine"],
             fontweight="bold")
    axD.text(0.04, 0.44, "Energy picks", fontsize=8.5, color="#555")
    axD.text(0.10, 0.30, "covers-both  ✓", fontsize=9, color=COL["coverage_mean"],
             fontweight="bold")
    axD.text(0.04, 0.08, "→ a real drug decision changes", fontsize=8, color="#333")
    axD.set_xlim(0, 1); axD.set_ylim(0, 1)
    _schematic_note(axD, "schematic (real flip in Fig. 2D)")

    # E dataset ladder on the divergence axis (DATA)
    axE = fig.add_subplot(gs[1, 1:]); panel(axE, "E")
    pos = L("exp02_divergence_gate/dataset_positions_on_gate.csv")
    save_source(pos, "fig1_E_dataset_ladder.csv")
    axE.set_title("Dataset ladder on the response-divergence axis", loc="left")
    axE.axvspan(-0.25, GATE, color="#C44E52", alpha=0.08)
    axE.axvline(GATE, color="#C44E52", ls="--", lw=1)
    axE.text(GATE - 0.02, 1.28, "gate ≈ 0.9", color="#C44E52", ha="right", fontsize=8)
    axE.text((GATE - 0.25) / 2 + 0.0, 1.28, "mean-out fails (divergent)", color="#C44E52",
             ha="center", fontsize=8)
    for _, r in pos.iterrows():
        c = DSCOL.get(r["dataset"], "#333")
        axE.scatter(r["typical_cross_cos"], 1.0, s=120, color=c, zorder=5, edgecolor="white")
        axE.annotate(f"{r['dataset']}\n(cos≈{r['typical_cross_cos']:.2f})",
                     (r["typical_cross_cos"], 1.0), textcoords="offset points",
                     xytext=(0, -34 if r["dataset"] != "Frangieh immune" else 18),
                     ha="center", fontsize=7.6, color=c)
    axE.set_xlim(1.0, -0.25); axE.set_ylim(0.6, 1.5)
    axE.set_yticks([]); axE.set_xlabel("subpopulation response cosine  (homogeneous → divergent)")
    despine(axE, ("top", "right", "left"))
    save_fig(fig, "fig1_problem_formulation")


# ----------------------------- Figure 2 -----------------------------

def fig2():
    ms = L("exp01_sciplex3_controlled/metrics_summary.csv")
    fig = plt.figure(figsize=(11.5, 7.4))
    gs = fig.add_gridspec(2, 2, hspace=0.42, wspace=0.30, height_ratios=[1, 1.05])
    fig.suptitle("Controlled SciPlex3 proof: mean-based retrieval fails, distributional fixes it",
                 fontsize=12, fontweight="bold", y=0.99)

    # A construction schematic
    axA = fig.add_subplot(gs[0, 0]); axA.axis("off"); panel(axA, "A")
    axA.set_title("Heterogeneous query (HDAC vs JAK)", loc="left")
    _cloud(axA, 0.30, 0.62, COL["mean_cosine"], seed=5)
    _cloud(axA, 0.55, 0.40, COL["global_energy"], seed=6, n=25)
    axA.text(0.30, 0.86, "majority (α)", ha="center", fontsize=8, color=COL["mean_cosine"])
    axA.text(0.62, 0.20, "minority (1−α)", ha="center", fontsize=8, color=COL["global_energy"])
    axA.text(0.5, 0.03, "ground truth = drug covering BOTH subpopulations", ha="center", fontsize=8)
    axA.set_xlim(0, 1); axA.set_ylim(0, 1)
    _schematic_note(axA, "schematic")

    # B headline Hit@1 bars (avg over alpha)
    axB = fig.add_subplot(gs[0, 1]); panel(axB, "B")
    agg = ms.groupby("cell_line")[[f"{s}_hit@1" for s in SC4]].mean()
    order = ["K562", "A549", "MCF7"]
    agg = agg.loc[order]
    src = agg.rename(columns={f"{s}_hit@1": s for s in SC4}).reset_index()
    save_source(src, "fig2_B_headline_hit1.csv")
    x = np.arange(len(order)); w = 0.2
    for i, s in enumerate(SC4):
        axB.bar(x + (i - 1.5) * w, agg[f"{s}_hit@1"], w, color=COL[s], label=LAB[s])
    axB.axhline(1 / 43, color="#999", ls=":", lw=1)
    axB.text(2.4, 1 / 43 + 0.02, "random", color="#999", fontsize=7)
    axB.set_xticks(x); axB.set_xticklabels(order)
    axB.set_ylabel("Hit@1 of covers-both  (avg over α)"); axB.set_ylim(0, 1.05)
    axB.set_title("Distribution-aware >> mean-cosine (3 cell lines)", loc="left")
    axB.legend(ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.12))
    despine(axB)

    # C alpha crossover
    axC = fig.add_subplot(gs[1, 0]); panel(axC, "C")
    lw_map = {"K562": 2.2, "A549": 1.1, "MCF7": 1.1}
    for cl in order:
        d = ms[ms.cell_line == cl].sort_values("alpha")
        axC.plot(d.alpha, d["mean_cosine_hit@1"], "o-", color=COL["mean_cosine"],
                 lw=lw_map[cl], ms=4, alpha=1 if cl == "K562" else 0.4)
        axC.plot(d.alpha, d["global_energy_hit@1"], "s-", color=COL["global_energy"],
                 lw=lw_map[cl], ms=4, alpha=1 if cl == "K562" else 0.4)
    save_source(ms[["cell_line", "alpha", "mean_cosine_hit@1", "global_energy_hit@1"]],
                "fig2_C_alpha_crossover.csv")
    axC.set_xlabel("majority ratio α"); axC.set_ylabel("Hit@1 of covers-both")
    axC.set_ylim(-0.02, 1.05)
    axC.set_title("Crossover: mean decays as one subpop dominates", loc="left")
    from matplotlib.lines import Line2D
    axC.legend(handles=[Line2D([0], [0], color=COL["mean_cosine"], marker="o", label="Mean cosine"),
                        Line2D([0], [0], color=COL["global_energy"], marker="s", label="Global energy"),
                        Line2D([0], [0], color="#333", lw=2.2, label="K562 (bold)"),
                        Line2D([0], [0], color="#333", lw=1.1, alpha=0.4, label="A549 / MCF7")],
               loc="lower left")
    despine(axC)

    # D real ranking-flip ladder (K562, alpha=0.5, seed=1000)
    axD = fig.add_subplot(gs[1, 1]); axD.axis("off"); panel(axD, "D")
    pq = L("exp01_sciplex3_controlled/per_query_scores.csv")
    q = pq[(pq.cell_line == "K562") & (pq.alpha == 0.5) & (pq.seed == 1000)].copy()
    def top10(col):
        return q.sort_values(col, ascending=False)["candidate"].head(10).tolist()
    tm, te = top10("mean_cosine"), top10("global_energy")
    src = pd.DataFrame({"rank": np.arange(1, 11), "mean_cosine_top": tm, "global_energy_top": te})
    save_source(src, "fig2_D_ranking_flip_example.csv")
    axD.set_title("A real ranking flip (K562, α=0.5)", loc="left")
    axD.text(0.27, 0.965, "Mean cosine", ha="center", fontsize=8.5, fontweight="bold")
    axD.text(0.78, 0.965, "Global energy", ha="center", fontsize=8.5, fontweight="bold")

    def _clean(n):
        return n.replace("distractor:", "")[:22]

    def _color(n):
        if n == "covers-both":
            return COL["coverage_mean"]
        if n in ("majority-only", "minority-only"):
            return COL["mean_cosine"]
        return "#888"
    for i in range(10):
        y = 0.92 - i * 0.092
        axD.text(0.0, y, f"{i+1}.", fontsize=7.5, color="#555")
        axD.text(0.06, y, _clean(tm[i]), fontsize=7.5, color=_color(tm[i]),
                 fontweight="bold" if tm[i] == "covers-both" else "normal")
        axD.text(0.56, y, _clean(te[i]), fontsize=7.5, color=_color(te[i]),
                 fontweight="bold" if te[i] == "covers-both" else "normal")
    axD.text(0.5, -0.02, "green = covers-both (correct) · red = majority/minority-only",
             ha="center", fontsize=7, color="#666")
    axD.set_xlim(0, 1); axD.set_ylim(0, 1)
    save_fig(fig, "fig2_controlled_sciplex3")


# ----------------------------- Figure 3 -----------------------------

def fig3():
    fig = plt.figure(figsize=(12.4, 7.2))
    gs = fig.add_gridspec(2, 3, hspace=0.55, wspace=0.48)
    fig.suptitle("Divergence gate: when is distribution-aware retrieval necessary?",
                 fontsize=12, fontweight="bold", y=0.99)

    # A response-cosine definition (schematic)
    axA = fig.add_subplot(gs[0, 0]); panel(axA, "A")
    axA.set_title("Response-direction cosine", loc="left")
    axA.annotate("", xy=(0.85, 0.75), xytext=(0.1, 0.15),
                 arrowprops=dict(arrowstyle="-|>", color=COL["mean_cosine"], lw=2))
    axA.annotate("", xy=(0.5, 0.9), xytext=(0.1, 0.15),
                 arrowprops=dict(arrowstyle="-|>", color=COL["global_energy"], lw=2))
    axA.text(0.88, 0.78, r"$\Delta_1$", color=COL["mean_cosine"], fontsize=10)
    axA.text(0.5, 0.94, r"$\Delta_2$", color=COL["global_energy"], fontsize=10)
    axA.text(0.34, 0.42, r"$\cos(\Delta_1,\Delta_2)$", fontsize=9)
    axA.set_xlim(0, 1); axA.set_ylim(0, 1); axA.set_xticks([]); axA.set_yticks([])
    _schematic_note(axA, "schematic")

    # B advantage vs response cosine
    axB = fig.add_subplot(gs[0, 1]); panel(axB, "B")
    dv = L("exp02_divergence_gate/divergence_sweep.csv")
    piv = dv.groupby(["subpop_cos", "scorer"])["hit@1"].mean().unstack()[SC4].sort_index()
    save_source(piv.reset_index(), "fig3_B_divergence_sweep.csv")
    for s in SC4:
        axB.plot(piv.index, piv[s], "o-", color=COL[s], ms=4, label=LAB[s])
    axB.axvline(GATE, color="#C44E52", ls="--", lw=1)
    axB.text(GATE, 1.02, "gate", color="#C44E52", fontsize=7.5, ha="center")
    axB.invert_xaxis()
    axB.set_xlabel("subpop response cosine  (← homogeneous | divergent →)")
    axB.set_ylabel("Hit@1"); axB.set_ylim(-0.02, 1.08)
    axB.set_title("Advantage vs. divergence", loc="left")
    axB.legend(loc="center left", fontsize=7)
    despine(axB)

    # C depth robustness
    axC = fig.add_subplot(gs[0, 2]); panel(axC, "C")
    pw = L("exp02_divergence_gate/depth_sweep.csv")
    pv = pw.groupby(["N", "scorer"])["hit@1"].mean().unstack()[SC4]
    save_source(pv.reset_index(), "fig3_C_depth_sweep.csv")
    axC.axvspan(12, 65, color="#55A868", alpha=0.10)
    axC.text(28, 0.06, "CD34-like depth", fontsize=7, color="#3a7", ha="center")
    for s in ("mean_cosine", "global_energy"):
        axC.plot(pv.index, pv[s], "o-", color=COL[s], ms=4, label=LAB[s])
    axC.set_xscale("log")
    axC.set_xticks([15, 30, 60, 120, 240])
    axC.get_xaxis().set_major_formatter(ScalarFormatter())
    axC.minorticks_off()
    axC.set_xlabel("cells / subpopulation (N)")
    axC.set_ylabel("Hit@1"); axC.set_ylim(-0.02, 1.08)
    axC.set_title("Depth-robust (≈60 suffice)", loc="left")
    axC.legend(loc="center right"); despine(axC)

    # D metric robustness
    axD = fig.add_subplot(gs[1, 0]); panel(axD, "D")
    mr = L("exp02_divergence_gate/metric_robustness.csv")
    metrics = ["mean_cosine", "energy", "mmd", "sliced_w"]
    mpv = mr.groupby(["subpop_cos", "metric"])["hit@1"].mean().unstack()[metrics].sort_index()
    save_source(mpv.reset_index(), "fig3_D_metric_robustness.csv")
    for m in metrics:
        axD.plot(mpv.index, mpv[m], "o-", color=COL[m], ms=4, label=LAB[m])
    axD.axvline(GATE, color="#C44E52", ls="--", lw=1)
    axD.invert_xaxis()
    axD.set_xlabel("subpop response cosine"); axD.set_ylabel("Hit@1"); axD.set_ylim(-0.02, 1.08)
    axD.set_title("Metric-agnostic gate", loc="left")
    axD.legend(loc="center left", fontsize=7); despine(axD)

    # E dataset positions on the gate (DATA)
    axE = fig.add_subplot(gs[1, 1:]); panel(axE, "E")
    pos = L("exp02_divergence_gate/dataset_positions_on_gate.csv")
    save_source(pos, "fig3_E_dataset_positions.csv")
    axE.axvspan(-0.25, GATE, color="#C44E52", alpha=0.08)
    axE.axvline(GATE, color="#C44E52", ls="--", lw=1)
    for _, r in pos.iterrows():
        c = DSCOL.get(r["dataset"], "#333")
        axE.scatter(r["typical_cross_cos"], 1.0, s=140, color=c, zorder=5, edgecolor="white")
        axE.annotate(f"{r['dataset']}\ncos≈{r['typical_cross_cos']:.2f} · {r['regime']}",
                     (r["typical_cross_cos"], 1.0), textcoords="offset points",
                     xytext=(0, -40 if r["dataset"] != "Frangieh immune" else 20),
                     ha="center", fontsize=7.4, color=c)
    axE.text(GATE, 1.42, "gate ≈ 0.9", color="#C44E52", ha="center", fontsize=8)
    axE.set_xlim(1.0, -0.25); axE.set_ylim(0.5, 1.6); axE.set_yticks([])
    axE.set_xlabel("subpopulation response cosine  (homogeneous → divergent)")
    axE.set_title("Where the real datasets sit", loc="left")
    despine(axE, ("top", "right", "left"))
    save_fig(fig, "fig3_divergence_gate")


# ----------------------------- Figure 4 -----------------------------

def fig4():
    fig = plt.figure(figsize=(11.0, 7.2))
    gs = fig.add_gridspec(2, 2, hspace=0.42, wspace=0.30)
    fig.suptitle("Semi-realistic positive (cross-line) and honest negative (CD34+)",
                 fontsize=12, fontweight="bold", y=0.99)
    order = ["K562+A549", "A549+MCF7", "K562+MCF7"]

    # A cross-line response divergence (reliable drugs)
    axA = fig.add_subplot(gs[0, 0]); panel(axA, "A")
    cd = L("exp03_crossline_semireal/crossline_divergence.csv")
    rel = cd[cd["reliable"]].copy()
    save_source(rel[["pair", "drug", "cross_cos", "rel_a", "rel_b"]],
                "fig4_A_crossline_divergence.csv")
    data = [rel[rel.pair == p]["cross_cos"].values for p in order]
    bp = axA.boxplot(data, positions=range(len(order)), widths=0.5, patch_artist=True,
                     showfliers=False)
    for patch in bp["boxes"]:
        patch.set(facecolor="#DCE6F2", edgecolor="#4C72B0")
    for i, p in enumerate(order):
        v = rel[rel.pair == p]["cross_cos"].values
        axA.scatter(np.full(len(v), i) + np.random.default_rng(i).normal(0, 0.05, len(v)),
                    v, s=7, color=COL["global_energy"], alpha=0.4, zorder=3)
    axA.axhline(GATE, color="#C44E52", ls="--", lw=1)
    axA.text(2.4, GATE + 0.02, "gate 0.9", color="#C44E52", fontsize=7, ha="right")
    axA.axhspan(0.78, 0.86, color="#999", alpha=0.15)
    axA.text(-0.4, 0.82, "within-line\nreliability", fontsize=6.6, color="#666", va="center")
    axA.set_xticks(range(len(order))); axA.set_xticklabels(order, fontsize=7.5)
    axA.set_ylabel("cross-line response cosine"); axA.set_ylim(-0.3, 1.0)
    axA.set_title("Same drug → near-orthogonal in two cell types", loc="left")
    despine(axA)

    # B cross-line retrieval (alpha crossover)
    axB = fig.add_subplot(gs[0, 1]); panel(axB, "B")
    cr = L("exp03_crossline_semireal/crossline_retrieval.csv")
    save_source(cr, "fig4_B_crossline_retrieval.csv")
    for cl, lw in zip(order, (2.2, 1.1, 1.1)):
        d = cr[cr.pair == cl].sort_values("alpha")
        al = 1 if cl == order[0] else 0.4
        axB.plot(d.alpha, d["mean_cosine_hit@1"], "o-", color=COL["mean_cosine"], lw=lw, ms=4, alpha=al)
        axB.plot(d.alpha, d["global_energy_hit@1"], "s-", color=COL["global_energy"], lw=lw, ms=4, alpha=al)
    axB.set_xlabel("majority ratio α"); axB.set_ylabel("Hit@1 of covers-both"); axB.set_ylim(0, 1.05)
    axB.set_title("Mean-out failure replicates on real cell types", loc="left")
    from matplotlib.lines import Line2D
    axB.legend(handles=[Line2D([0], [0], color=COL["mean_cosine"], marker="o", label="Mean cosine"),
                        Line2D([0], [0], color=COL["global_energy"], marker="s", label="Global energy")],
               loc="center left")
    despine(axB)

    # C CD34 lineages respond alike (agreement) + noise floor
    axC = fig.add_subplot(gs[1, 0]); panel(axC, "C")
    ag = L("exp04_cd34_negative/cd34_lineage_mean_agreement.csv")
    nc = L("exp04_cd34_negative/cd34_noise_controls.csv")
    save_source(ag, "fig4_C_cd34_lineage_agreement.csv")
    save_source(nc, "fig4_C_cd34_noise_controls.csv")
    xa = np.arange(len(ag))
    cols = [COL["mean_cosine"] if m else COL["coverage_mean"] for m in ag["is_minority"]]
    axC.bar(xa, ag["agree_with_mean"], 0.6, color=cols)
    axC.set_xticks(xa); axC.set_xticklabels(ag["lineage"])
    axC.set_ylabel("lineage vs mean\ndrug-ranking agreement (ρ)"); axC.set_ylim(0, 1)
    axC.axhspan(0.10, 0.26, color="#999", alpha=0.18)
    axC.text(len(ag) - 0.5, 0.18, "matched within≈between\nnoise floor", fontsize=6.6,
             color="#666", ha="right", va="center")
    axC.set_title("CD34+ lineages rank drugs ~like the mean", loc="left")
    despine(axC)

    # D CD34 negative retrieval (mean WINS)
    axD = fig.add_subplot(gs[1, 1]); panel(axD, "D")
    rt = L("exp04_cd34_negative/cd34_retrieval.csv")
    agg = rt.groupby("scorer")["hit@1"].mean().reindex(SC4)
    save_source(agg.reset_index(), "fig4_D_cd34_retrieval.csv")
    axD.bar(np.arange(len(SC4)), agg.values, 0.6, color=[COL[s] for s in SC4])
    axD.axhline(1 / 36, color="#999", ls=":", lw=1); axD.text(3.2, 1 / 36 + 0.01, "random", fontsize=7, color="#999")
    short = {"mean_cosine": "Mean cosine", "global_energy": "Global energy",
             "coverage_mean": "Coverage (mean)", "coverage_worst": "Coverage (worst)"}
    axD.set_xticks(np.arange(len(SC4)))
    axD.set_xticklabels([short[s] for s in SC4], rotation=20, ha="right", fontsize=7.5)
    axD.set_ylabel("self-retrieval Hit@1"); axD.set_ylim(0, 0.65)
    axD.set_title("Honest negative: mean-cosine WINS on real primary cells", loc="left")
    despine(axD)
    save_fig(fig, "fig4_real_validation")


# ----------------------------- Figure 5 -----------------------------

def fig5():
    fig = plt.figure(figsize=(11.0, 7.2))
    gs = fig.add_gridspec(2, 2, hspace=0.44, wspace=0.32)
    fig.suptitle("Frangieh melanoma: natural evidence and the within-gene IFNGR1 instance",
                 fontsize=12, fontweight="bold", y=0.99)
    ifn = L("exp05_frangieh_natural/frangieh_ifngr1_case.csv")

    # A immune-context setup (schematic)
    axA = fig.add_subplot(gs[0, 0]); axA.axis("off"); panel(axA, "A")
    axA.set_title("Immune microenvironments as subpopulations", loc="left")
    for i, (cond, c) in enumerate([("Control", "#8C8C8C"), ("IFNγ", "#DD8452"),
                                   ("Co-culture", "#4C72B0")]):
        _cloud(axA, 0.2 + i * 0.3, 0.55, c, n=35, spread=0.09, seed=10 + i)
        axA.text(0.2 + i * 0.3, 0.30, cond, ha="center", fontsize=8, color=c)
    axA.text(0.5, 0.08, "one tumor mixes immune contexts;\nimmune KOs act differently across them",
             ha="center", fontsize=7.8)
    axA.set_xlim(0, 1); axA.set_ylim(0, 1)
    _schematic_note(axA, "schematic")

    # B IFNGR1 divergence per contrast
    axB = fig.add_subplot(gs[0, 1]); panel(axB, "B")
    save_source(ifn[["contrast", "cross_cos"]], "fig5_B_ifngr1_divergence.csv")
    cols = [COL["global_energy"] if c < GATE else "#999" for c in ifn["cross_cos"]]
    axB.bar(np.arange(len(ifn)), ifn["cross_cos"], 0.6, color=cols)
    axB.axhline(GATE, color="#C44E52", ls="--", lw=1); axB.text(2.3, GATE + 0.02, "gate 0.9", color="#C44E52", fontsize=7, ha="right")
    axB.set_xticks(np.arange(len(ifn)))
    axB.set_xticklabels([c.replace("+", "\n+") for c in ifn["contrast"]], fontsize=7)
    axB.set_ylabel("IFNGR1 cross-context cosine"); axB.set_ylim(0, 1.0)
    axB.set_title("IFNGR1 diverges only vs immune-OFF Control", loc="left")
    despine(axB)

    # C IFNGR1 ranking with CI
    axC = fig.add_subplot(gs[1, 0]); panel(axC, "C")
    save_source(ifn, "fig5_C_ifngr1_ranking.csv")
    x = np.arange(len(ifn)); w = 0.34
    for j, s in enumerate(["mean_cosine", "global_energy"]):
        lo = ifn[s] - ifn[f"{s}_lo"]; hi = ifn[f"{s}_hi"] - ifn[s]
        axC.bar(x + (j - 0.5) * w, ifn[s], w, color=COL[s], label=LAB[s],
                yerr=[lo, hi], capsize=3, error_kw=dict(lw=0.8))
    axC.set_xticks(x); axC.set_xticklabels([c.replace("+", "\n+") for c in ifn["contrast"]], fontsize=7)
    axC.set_ylabel("Hit@1 of covers-both"); axC.set_ylim(0, 1.15)
    axC.set_title("Mean-out fails only when contexts diverge", loc="left")
    axC.legend(loc="upper left"); despine(axC)

    # D gene-level divergence vs advantage
    axD = fig.add_subplot(gs[1, 1]); panel(axD, "D")
    gg = L("exp05_frangieh_natural/frangieh_retrieval_by_gene.csv")
    save_source(gg, "fig5_D_gene_divergence_vs_advantage.csv")
    axD.scatter(gg["cross_cos"], gg["advantage"], s=30, color=COL["global_energy"], alpha=0.7, zorder=3)
    for _, r in gg.iterrows():
        if r["ko"] in ("IFNGR1", "JAK1", "B2M"):
            axD.annotate(r["ko"], (r["cross_cos"], r["advantage"]), fontsize=7.5,
                         xytext=(4, 4), textcoords="offset points")
    axD.axvline(GATE, color="#C44E52", ls="--", lw=1)
    axD.axhline(0, color="#999", lw=0.8)
    axD.set_xlabel("KO cross-context cosine"); axD.set_ylabel("distributional advantage\n(energy − mean Hit@1)")
    axD.set_title("Per-KO: advantage rises with divergence (ρ<0)", loc="left")
    despine(axD)
    save_fig(fig, "fig5_frangieh")


# ----------------------------- Figure 6 -----------------------------

def fig6():
    fig = plt.figure(figsize=(11.0, 7.0))
    gs = fig.add_gridspec(2, 2, hspace=0.42, wspace=0.30)
    fig.suptitle("Theory: distributional score is a strict generalization of mean matching",
                 fontsize=12, fontweight="bold", y=0.99)
    syn = L("exp06_theory_limits/degenerate_limit_synthetic.csv")

    # A mean as zero-variance limit
    axA = fig.add_subplot(gs[0, 0]); panel(axA, "A")
    p1 = syn[syn["prop"] == "prop1_spread"].sort_values("t_spread")
    save_source(p1[["t_spread", "energy", "two_dmu"]], "fig6_A_zero_spread_limit.csv")
    axA.plot(p1["t_spread"], p1["energy"], "o-", color=COL["global_energy"], label="energy distance")
    axA.axhline(p1["two_dmu"].iloc[0], color=COL["mean_cosine"], ls="--", label=r"$2\|\mu_P-\mu_Q\|$ (mean)")
    axA.set_xlabel("within-population spread  t  (→ 0)"); axA.set_ylabel("distance")
    axA.set_title("Mean = zero-spread limit of energy", loc="left")
    axA.legend(loc="center right"); despine(axA)

    # B global == coverage at K=1
    axB = fig.add_subplot(gs[0, 1]); panel(axB, "B")
    p2 = syn[syn["prop"] == "prop2_K1"].dropna(subset=["beta"]).sort_values("beta")
    save_source(p2[["beta", "coverage_K1", "global_energy"]], "fig6_B_global_is_K1.csv")
    axB.plot(p2["beta"], p2["coverage_K1"], "o", color=COL["coverage_mean"], ms=7, label="coverage (K=1)")
    axB.axhline(p2["global_energy"].iloc[0], color=COL["global_energy"], ls="--", label="global energy")
    axB.set_xscale("symlog"); axB.set_xlabel("aggregation temperature β")
    axB.set_ylabel("distance"); axB.set_title("Global energy = coverage at K=1 (any β)", loc="left")
    axB.legend(loc="center right"); despine(axB)

    # C beta interpolation
    axC = fig.add_subplot(gs[1, 0]); panel(axC, "C")
    bi = L("exp06_theory_limits/beta_interpolation.csv")
    save_source(bi, "fig6_C_beta_interpolation.csv")
    axC.plot(bi["beta"], bi["D_beta"], "o-", color=COL["coverage_worst"], ms=4)
    axC.axhline(bi["mean"].iloc[0], color=COL["coverage_mean"], ls="--", label="mean (β→0)")
    axC.axhline(bi["max"].iloc[0], color=COL["coverage_worst"], ls=":", label="worst (β→∞)")
    axC.set_xscale("log"); axC.set_xlabel("aggregation temperature β")
    axC.set_ylabel(r"$D_\beta$"); axC.set_title("One β interpolates mean ↔ worst", loc="left")
    axC.legend(loc="center right"); despine(axC)

    # D hierarchy (schematic)
    axD = fig.add_subplot(gs[1, 1]); axD.axis("off"); panel(axD, "D")
    axD.set_title("Generalization hierarchy", loc="left")
    boxes = [(0.5, 0.5, 0.9, 0.8, "#EAF0F6", "β-family subpopulation coverage"),
             (0.5, 0.47, 0.62, 0.5, "#D3E0EE", "global energy  (= K=1 coverage)"),
             (0.5, 0.44, 0.34, 0.22, "#C44E5233", "mean matching\n(zero-spread)")]
    for cx, cy, w, h, fc, txt in boxes:
        axD.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h, transform=axD.transAxes,
                                     boxstyle="round,pad=0.01", fc=fc, ec="#4C72B0"))
    axD.text(0.5, 0.86, "β-family coverage", ha="center", fontsize=8.5, color="#28527a")
    axD.text(0.5, 0.66, "global energy (K=1 coverage)", ha="center", fontsize=8, color="#28527a")
    axD.text(0.5, 0.44, "mean matching", ha="center", fontsize=8, color=COL["mean_cosine"])
    axD.text(0.5, 0.04, r"mean $\subset$ global energy $\subset$ coverage", ha="center", fontsize=9)
    axD.set_xlim(0, 1); axD.set_ylim(0, 1)
    _schematic_note(axD, "schematic (proven numerically in exp06)")
    save_fig(fig, "fig6_theory")


FIGS = {1: fig1, 2: fig2, 3: fig3, 4: fig4, 5: fig5, 6: fig6}


def main():
    which = [int(a) for a in sys.argv[1:]] or list(FIGS)
    OUT.mkdir(parents=True, exist_ok=True)
    SRC.mkdir(parents=True, exist_ok=True)
    print(f"[figures] -> {OUT}")
    for k in which:
        print(f"Figure {k}:")
        FIGS[k]()
    print(f"[figures] done: {len(which)} figures + source CSVs in {SRC}")


if __name__ == "__main__":
    main()
