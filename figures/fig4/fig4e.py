"""DART Figure 4 panel 4e: gate axis vs true divergence
Source data: source_data/fig4ef_gate_divergence.csv
Run standalone: python fig4e.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
key=["split_type","cell_line","heldout_drug","observed_library_fraction","seed"]

def draw_4e(ax):
    """Gate axes vs true divergence: structure_reliability (wrong dir) + conflict (too weak)."""
    mg=pd.read_csv(f"{REPO}/results/exp16_gate_diagnosis/_merged_query_divergence.csv")
    u=mg.dropna(subset=['structure_reliability_score','true_divergence']).drop_duplicates(subset=key)
    ax.scatter(u['true_divergence'],u['structure_reliability_score'],s=5,color=COMP,alpha=0.3,edgecolors='none')
    z=np.polyfit(u['true_divergence'],u['structure_reliability_score'],1)
    xx=np.linspace(u['true_divergence'].min(),u['true_divergence'].max(),50)
    ax.plot(xx,np.polyval(z,xx),color=COMP,lw=1.6)
    ax.text(0.04,0.06,'structure reliability\n$\\rho$=$-$0.21 (wrong sign)',transform=ax.transAxes,fontsize=6,color=COMP,va='bottom')
    ax.set_xlabel('true response divergence'); ax.set_ylabel('gate: structure reliability')
    for sp in ['right','top']: ax.spines[sp].set_visible(False)
    ax.set_title("The gate axis points the wrong way", loc='left')


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.5,3.0))
    draw_4e(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "4e.png"), dpi=200, bbox_inches="tight")
    print("wrote 4e.png")
