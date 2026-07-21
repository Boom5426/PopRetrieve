"""DART Figure 3 panel 3a: overall Hit@1 ladder
Source data: source_data/fig3a_hit1_ladder.csv
Run standalone: python fig3a.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def draw_3a(ax):
    """Overall Hit@1 ladder by scorer."""
    s=pd.read_csv(f"{REPO}/results/exp08_signature_baselines/summary.csv")
    agg=s.groupby('method')['hit@1'].mean().sort_values()
    labs={'global_energy':'energy','pca_dist':'PCA-dist','coverage_mean':'coverage-mean',
          'coverage_worst':'coverage-worst','pca_mean':'PCA-mean','cmap_wtcs':'CMap WTCS',
          'cmap_cosine':'CMap cosine','mean_cosine':'mean cosine'}
    fam={'global_energy':FOCAL,'coverage_mean':FOCAL,'coverage_worst':FOCAL,
         'pca_dist':GREY,'pca_mean':GREY,'cmap_wtcs':GREY,'cmap_cosine':COMP,'mean_cosine':COMP}
    ys=np.arange(len(agg))
    for y,(m,v) in zip(ys,agg.items()):
        ax.barh(y,v,color=fam[m],alpha=0.85,height=0.68)
        ax.text(v+0.008,y,f'{v:.3f}',va='center',fontsize=5.8,color=fam[m])
    ax.set_yticks(ys); ax.set_yticklabels([labs[m] for m in agg.index],fontsize=6)
    ax.set_xlabel('Hit@1 (7-task mean)'); ax.set_xlim(0,0.95)
    for sp in ['right','top']: ax.spines[sp].set_visible(False)
    ax.set_title("Distributional scorers rank drugs better", loc='left')


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.6,3.0))
    draw_3a(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "3a.png"), dpi=200, bbox_inches="tight")
    print("wrote 3a.png")
