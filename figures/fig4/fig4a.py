"""DART Figure 4 panel 4a: Class A vs Class B sign flip
Source data: source_data/fig4a_classA_vs_classB.csv
Run standalone: python fig4a.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
key=["split_type","cell_line","heldout_drug","observed_library_fraction","seed"]

def draw_4a(ax):
    p=pd.read_csv(f"{REPO}/figures/source_data/fig4a_classA_vs_classB.csv")
    a=p['classA_regret_reduction']; b=p['classB_moa_ndcg_gain']
    parts=ax.violinplot([a,b],positions=[0,1],showmedians=True,widths=0.7)
    for i,pc in enumerate(parts['bodies']):
        pc.set_facecolor(FOCAL if i==0 else COMP); pc.set_alpha(0.5)
    for kk in ['cmedians','cbars','cmins','cmaxes']:
        parts[kk].set_color('k'); parts[kk].set_linewidth(1.0)
    ax.axhline(0,ls='--',lw=1.0,color=GREY,zorder=1)
    ax.text(0.30,a.median()+0.12,f'+{a.median():.3f}\n{(a>0).mean():.0%}>0',ha='left',fontsize=6,color=FOCAL)
    ax.text(1.30,b.mean()-0.02,f'{b.mean():+.3f}\n{(b>0).mean():.0%}>0',ha='left',fontsize=6,color=COMP)
    ax.set_xticks([0,1]); ax.set_xticklabels(['Class A\n(regret)','Class B\n(MoA-nDCG)'],fontsize=6.5)
    ax.set_ylabel('DART advantage'); ax.set_ylim(-0.9,1.05); ax.set_xlim(-0.6,1.9)
    for sp in ['right','top']: ax.spines[sp].set_visible(False)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.5,3.0))
    draw_4a(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "4a.png"), dpi=200, bbox_inches="tight")
    print("wrote 4a.png")
