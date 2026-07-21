"""DART Figure 3 panel 3e: alpha-crossover heterogeneity
Source data: source_data/fig3e_alpha_crossover.csv
Run standalone: python fig3e.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def draw_3e(ax):
    """exp01 alpha-crossover: energy beats mean as subpop mixing (alpha) varies."""
    cr=pd.read_csv(f"{REPO}/figures/source_data/fig3e_alpha_crossover.csv")
    for cl,mk in zip(['K562','A549','MCF7'],['o','s','^']):
        d=cr[cr.cell_line==cl].sort_values('alpha')
        ax.plot(d['alpha'],d['global_energy_hit@1'],'-',marker=mk,color=FOCAL,ms=4,lw=1.3,alpha=0.85)
        ax.plot(d['alpha'],d['mean_cosine_hit@1'],'--',marker=mk,color=COMP,ms=4,lw=1.1,alpha=0.7)
    ax.plot([],[],'-',color=FOCAL,label='energy'); ax.plot([],[],'--',color=COMP,label='mean cosine')
    ax.legend(fontsize=6,loc='center right',frameon=False)
    ax.set_xlabel(r'subpopulation mixing $\alpha$'); ax.set_ylabel('Hit@1')
    ax.set_ylim(-0.05,1.08)
    ax.text(0.5,-0.001,'(3 cell lines; marker = line)',transform=ax.transAxes,fontsize=5,color='0.5',ha='center')
    for sp in ['right','top']: ax.spines[sp].set_visible(False)
    ax.set_title("Gain tracks subpopulation structure", loc='left')


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.6,3.0))
    draw_3e(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "3e.png"), dpi=200, bbox_inches="tight")
    print("wrote 3e.png")
