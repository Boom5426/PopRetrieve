"""DART Figure 4 panel 4c: minority coverage gain by divergence quartile
Source data: source_data/fig4ef_gate_divergence.csv
Run standalone: python fig4c.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
key=["split_type","cell_line","heldout_drug","observed_library_fraction","seed"]

def draw_4c(ax):
    """Minority-coverage effect size by divergence quartile (significant but negligible)."""
    cbi=pd.read_csv(f"{REPO}/results/upgrade/coverage_by_identifiability.csv")
    # use exp12 minority coverage gain by divergence quartile
    mg=pd.read_csv(f"{REPO}/results/exp16_gate_diagnosis/_merged_query_divergence.csv")
    mg=mg.dropna(subset=['true_divergence','minority_state_coverage_gap'])
    mg['divq']=pd.qcut(mg['true_divergence'],4,labels=['Q1','Q2','Q3','Q4'])
    g=mg.groupby('divq',observed=True)['minority_state_coverage_gap'].agg(['mean','sem'])
    xs=np.arange(len(g))
    ax.bar(xs,g['mean'],yerr=g['sem'],width=0.6,color=FOCAL,alpha=0.75,error_kw=dict(lw=1,capsize=2))
    for x,m in zip(xs,g['mean']): ax.text(x,m*0.5,f'{m:+.4f}',ha='center',va='center',fontsize=5.0,color='white',rotation=90)
    ax.axhline(0,color='k',lw=0.8)
    ax.set_xticks(xs); ax.set_xticklabels(g.index)
    ax.set_xlabel('response-divergence quartile'); ax.set_ylabel('minority coverage gain')
    ax.text(0.5,0.90,'significant but negligible (<0.002)',transform=ax.transAxes,
            ha='center',va='top',fontsize=5.4,color=GREY)
    for sp in ['right','top']: ax.spines[sp].set_visible(False)
    ax.set_title("Minority-coverage gain is negligible", loc='left')


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.5,3.0))
    draw_4c(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "4c.png"), dpi=200, bbox_inches="tight")
    print("wrote 4c.png")
