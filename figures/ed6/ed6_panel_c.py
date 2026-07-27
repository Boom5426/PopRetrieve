"""EvalShift Extended Data Fig. 6 panel c: distributional-advantage phase diagram
Source data: source_data/fig5c_dart_advantage_grid.csv
Run standalone: python fig5c.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"
from matplotlib.colors import LinearSegmentedColormap
DIVMAP = LinearSegmentedColormap.from_list('dart_div', [COMP, '#f7f7f7', FOCAL])

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
H = os.path.join(REPO, "results", "exp11_hir_benchmark")
S = os.path.join(REPO, "results", "exp11_synthetic_phase_diagram")

def draw_5c(ax):
    """Phase diagram over (alpha, lambda), color = distributional (energy) advantage."""
    dag=pd.read_csv(f"{S}/dart_advantage_grid.csv")
    grid=dag.pivot_table(index='lambda',columns='alpha',values='adv_energy_vs_mean')
    im=ax.imshow(grid.values,cmap=DIVMAP,vmin=-1,vmax=1,aspect='auto',origin='lower')
    ax.set_xticks(range(len(grid.columns))); ax.set_xticklabels([f'{a:g}' for a in grid.columns],fontsize=6)
    ax.set_yticks(range(len(grid.index))); ax.set_yticklabels([f'{l:g}' for l in grid.index],fontsize=5.5)
    ax.set_xlabel(r'minority fraction $\alpha$'); ax.set_ylabel(r'conflict $\lambda$')
    cb=ax.figure.colorbar(im,ax=ax,fraction=0.046,pad=0.04); cb.set_label('energy $-$ mean\nHit@1',fontsize=5.5); cb.ax.tick_params(labelsize=5)
    ax.set_title("Distributional advantage is regime-dependent", loc='left')


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.5,3.0))
    draw_5c(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "5c.png"), dpi=200, bbox_inches="tight")
    print("wrote 5c.png")
