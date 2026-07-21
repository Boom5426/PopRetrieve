"""DART Figure 4 panel 4b: MoA-nDCG gain by cell line
Source data: source_data/fig4a_classA_vs_classB.csv
Run standalone: python fig4b.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
key=["split_type","cell_line","heldout_drug","observed_library_fraction","seed"]

def draw_4b(ax):
    p=pd.read_csv(f"{REPO}/figures/source_data/fig4a_classA_vs_classB.csv")
    for cl,col in zip(['A549','K562','MCF7'],[FOCAL,GREY,COMP]):
        d=p[p.cell_line==cl]['classB_moa_ndcg_gain'].sort_values().values
        if len(d)>3:
            ys=np.arange(1,len(d)+1)/len(d)
            ax.plot(d,ys,color=col,lw=1.4,label=f'{cl} (n={len(d)})')
    ax.axvline(0,ls='--',lw=1.0,color='k',zorder=1)
    ax.legend(fontsize=5.4,loc='upper left',frameon=False,handlelength=1.2,labelspacing=0.25)
    ax.set_xlabel('MoA-nDCG gain (DART $-$ mean)'); ax.set_ylabel('cumulative fraction')
    ax.set_xlim(-0.6,0.6)
    for sp in ['right','top']: ax.spines[sp].set_visible(False)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.5,3.0))
    draw_4b(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "4b.png"), dpi=200, bbox_inches="tight")
    print("wrote 4b.png")
