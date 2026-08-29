"""PopRetrieve Extended Data Fig. 6 panel c: distributional-advantage phase diagram
Source data: results/exp11_synthetic_phase_diagram/dart_advantage_grid.csv
Run standalone: python ed6_panel_c.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
# Palette comes from the house-style module; do NOT re-declare the hex values here. Every
# panel file used to carry its own copy, which made figstyle's "one edit here recolours the
# whole deck" untrue: a recolour meant editing 43 files and missing one was silent.
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from figstyle import FOCAL_SOFT, COMP_SOFT, GREY, DIVMAP_SOFT  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap
# The divergent map is imported, not rebuilt. Two local copies of it existed, and a
# recolour of FOCAL/COMP moved the figures that imported it while leaving these two
# behind: the same failure the palette itself had.

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
H = os.path.join(REPO, "results", "exp11_hir_benchmark")
S = os.path.join(REPO, "results", "exp11_synthetic_phase_diagram")

def draw_ed6b(ax):
    """Phase diagram over (alpha, lambda), color = distributional (energy) advantage."""
    dag=pd.read_csv(f"{S}/dart_advantage_grid.csv")
    grid=dag.pivot_table(index='lambda',columns='alpha',values='adv_energy_vs_mean')
    im=ax.imshow(grid.values,cmap=DIVMAP_SOFT,vmin=-1,vmax=1,aspect='auto',origin='lower')
    ax.set_xticks(range(len(grid.columns))); ax.set_xticklabels([f'{a:g}' for a in grid.columns],fontsize=6)
    ax.set_yticks(range(len(grid.index))); ax.set_yticklabels([f'{l:g}' for l in grid.index],fontsize=5.5)
    ax.set_xlabel(r'minority fraction $\alpha$'); ax.set_ylabel(r'conflict $\lambda$')
    cb=ax.figure.colorbar(im,ax=ax,fraction=0.046,pad=0.04); cb.set_label('energy $-$ mean\nHit@1',fontsize=5.5); cb.ax.tick_params(labelsize=5)
    ax.set_title("Distributional advantage is regime-dependent", loc='left')


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.5,3.0))
    draw_ed6b(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "ed6b.png"), dpi=200, bbox_inches="tight")
    print("wrote ed6b.png")
