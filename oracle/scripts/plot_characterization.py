#!/usr/bin/env python
"""Characterization figure: WHEN does 'population-in, mean-out' fail?
Panel A = power axis (robust); Panel B = divergence axis (the gate). CD34+ annotated."""
from __future__ import annotations
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results/subflow"; FIG = RES / "figures"; FIG.mkdir(parents=True, exist_ok=True)
SC = ["mean_cosine", "global_energy", "coverage_mean", "coverage_worst"]
LAB = {"mean_cosine": "mean-cosine (incumbent)", "global_energy": "global energy",
       "coverage_mean": "coverage (mean)", "coverage_worst": "coverage (worst)"}
COL = {"mean_cosine": "#c0392b", "global_energy": "#2980b9",
       "coverage_mean": "#27ae60", "coverage_worst": "#f39c12"}

pw = pd.read_csv(RES / "power_sweep.csv")
dv = pd.read_csv(RES / "divergence_sweep.csv")
fig, ax = plt.subplots(1, 2, figsize=(12.5, 4.6))

# Panel A: power
g = pw.groupby(["N", "scorer"])["hit@1"].mean().unstack()[SC]
for s in SC:
    ax[0].plot(g.index, g[s], "o-", color=COL[s], label=LAB[s])
ax[0].set_xscale("log"); ax[0].set_xticks(g.index); ax[0].set_xticklabels(g.index)
ax[0].axvspan(12, 65, color="red", alpha=0.08)
ax[0].text(28, 0.30, "CD34+ minority\n(~60 cells/subpop)", fontsize=8, ha="center", color="#7b241c")
ax[0].set_xlabel("cells per subpopulation"); ax[0].set_ylabel("Hit@1 of correct 'covers-both'")
ax[0].set_title("Power axis — advantage is depth-robust\n(divergent subpops, cos≈−0.05)")
ax[0].set_ylim(-0.03, 1.05); ax[0].legend(fontsize=7.5, loc="center right")

# Panel B: divergence
g = dv.groupby(["subpop_cos", "scorer"])["hit@1"].mean().unstack()[SC].sort_index()
for s in SC:
    ax[1].plot(g.index, g[s], "o-", color=COL[s], label=LAB[s])
ax[1].invert_xaxis()  # divergent (low cos) on the right
ax[1].axvspan(0.95, 1.01, color="red", alpha=0.08)
ax[1].text(0.98, 0.55, "CD34+ natural\nlineages (alike)", fontsize=8, ha="center", color="#7b241c")
ax[1].annotate("controlled\nHDAC⟂JAK", xy=(-0.05, 0.98), xytext=(-0.4, 0.72), fontsize=8,
               ha="center", color="#1b4f72",
               arrowprops=dict(arrowstyle="->", color="#1b4f72", lw=1))
ax[1].set_xlabel("subpopulation response similarity (cosine; 1 = identical)")
ax[1].set_title("Divergence axis — the gate\n(fixed well-powered N=240)")
ax[1].set_ylim(-0.03, 1.05)

fig.suptitle("When does 'population-in, mean-out' fail? Divergence-gated, depth-robust "
             "(CD34+ natural heterogeneity sits below the gate)", y=1.02, fontsize=11)
fig.tight_layout()
fig.savefig(FIG / "fig_characterization.png", dpi=150, bbox_inches="tight")
print("wrote", FIG / "fig_characterization.png")

# ---- metric-robustness figure (divergence gate is metric-agnostic) ----
mr_path = RES / "metric_robustness.csv"
if mr_path.exists():
    mr = pd.read_csv(mr_path)
    MM = ["mean_cosine", "energy", "mmd", "sliced_w"]
    MLAB = {"mean_cosine": "mean-cosine", "energy": "energy",
            "mmd": "RBF-MMD", "sliced_w": "sliced-Wasserstein"}
    MCOL = {"mean_cosine": "#c0392b", "energy": "#2980b9",
            "mmd": "#8e44ad", "sliced_w": "#16a085"}
    g = mr.groupby(["subpop_cos", "metric"])["hit@1"].mean().unstack()[MM].sort_index()
    fig2, axm = plt.subplots(figsize=(6.2, 4.5))
    for m in MM:
        axm.plot(g.index, g[m], "o-", color=MCOL[m], label=MLAB[m])
    axm.invert_xaxis()
    axm.set_xlabel("subpopulation response similarity (cosine; 1 = identical)")
    axm.set_ylabel("Hit@1 of correct 'covers-both'")
    axm.set_title("The divergence gate is metric-agnostic\n"
                  "(energy / MMD / sliced-Wasserstein agree; mean-cosine ≈ 0)")
    axm.set_ylim(-0.03, 1.03); axm.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(FIG / "fig_metric_robustness.png", dpi=150, bbox_inches="tight")
    print("wrote", FIG / "fig_metric_robustness.png")
