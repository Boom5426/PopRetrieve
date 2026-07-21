#!/usr/bin/env python
"""Frangieh natural divergence-gate figure. Panel A: per-KO distributional advantage
vs context-divergence (the §8 gate on natural data). Panel B: IFNGR1 as a within-gene
controlled natural experiment -- fails only when the mixed immune contexts diverge."""
from __future__ import annotations
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results/subflow"; FIG = RES / "figures"; FIG.mkdir(parents=True, exist_ok=True)
FILES = {"Control|IFNγ": "frangieh_gate.csv",
         "Control|Co-culture": "frangieh_gate_Control_Co-culture.csv",
         "IFNγ|Co-culture": "frangieh_gate_IFNγ_Co-culture.csv"}
dfs = []
for k, f in FILES.items():
    if (RES / f).exists():
        d = pd.read_csv(RES / f); d["pair"] = k; dfs.append(d)
A = pd.concat(dfs, ignore_index=True)

fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.4))

# Panel A: advantage vs divergence
col = {"Control|IFNγ": "#2980b9", "Control|Co-culture": "#16a085", "IFNγ|Co-culture": "#c0392b"}
for k in FILES:
    s = A[A.pair == k]
    ax[0].scatter(s.cross_cos, s.advantage, s=34, color=col.get(k, "#888"), label=k, alpha=0.8)
for _, r in A[A.ko.isin(["IFNGR1", "JAK1"])].iterrows():
    ax[0].annotate(r.ko, (r.cross_cos, r.advantage), fontsize=7, xytext=(3, 3),
                   textcoords="offset points")
ax[0].axhline(0, color="k", lw=0.7); ax[0].axvline(0.5, color="grey", ls="--", lw=0.8)
lo, hi = A[A.cross_cos < 0.5], A[A.cross_cos >= 0.5]
ax[0].axhline(lo.advantage.mean(), 0, 0.42, color="#7b241c", lw=2)
ax[0].axhline(hi.advantage.mean(), 0.42, 1, color="#555", lw=2)
ax[0].text(0.25, lo.advantage.mean() + 0.04, f"cos<0.5: +{lo.advantage.mean():.2f}",
           fontsize=8, ha="center", color="#7b241c")
ax[0].text(0.75, hi.advantage.mean() - 0.09, f"cos≥0.5: {hi.advantage.mean():+.2f}",
           fontsize=8, ha="center", color="#555")
ax[0].invert_xaxis()
ax[0].set_xlabel("context-divergence: cross-condition response cos (→ more divergent)")
ax[0].set_ylabel("distributional advantage\n(global energy − mean-cosine Hit@1)")
ax[0].set_title("§8 gate on NATURAL data (per KO)\nmore divergent KOs → mean-out failure")
ax[0].legend(fontsize=7, loc="upper left")

# Panel B: IFNGR1 within-gene controlled experiment
g = A[A.ko == "IFNGR1"].copy()
order = ["Control|IFNγ", "Control|Co-culture", "IFNγ|Co-culture"]
g = g.set_index("pair").loc[[p for p in order if p in set(g.pair)]].reset_index()
x = np.arange(len(g)); w = 0.36
ax[1].bar(x - w/2, g.mean_cosine, w, color="#c0392b", label="mean-cosine (incumbent)")
ax[1].bar(x + w/2, g.global_energy, w, color="#2980b9", label="global energy")
ax[1].set_xticks(x)
ax[1].set_xticklabels([f"{p}\ncos={c:.2f}" for p, c in zip(g.pair, g.cross_cos)], fontsize=8)
ax[1].set_ylabel("Hit@1 of correct KO (IFNGR1)"); ax[1].set_ylim(0, 1.05)
ax[1].set_title("IFNGR1: one gene, controlled natural experiment\n"
                "fails only when mixed immune contexts DIVERGE")
ax[1].legend(fontsize=8, loc="upper left")

fig.suptitle("Frangieh melanoma Perturb-seq: natural immune-context divergence and the mean-out failure",
             y=1.02, fontsize=11)
fig.tight_layout()
fig.savefig(FIG / "fig_frangieh_gate.png", dpi=150, bbox_inches="tight")
print("wrote", FIG / "fig_frangieh_gate.png")
