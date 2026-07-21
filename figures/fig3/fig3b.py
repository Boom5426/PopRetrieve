"""DART Figure 3 panel 3b: Hit@1 by scorer x task
Source data: source_data/fig3b_task_heatmap.csv
Run standalone: python fig3b.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def draw_3b(ax):
    """Hit@1 by scorer x task heatmap."""
    sbt=pd.read_csv(f"{REPO}/results/exp08_signature_baselines/summary_by_task.csv")
    order=['global_energy','coverage_mean','pca_dist','coverage_worst','pca_mean','cmap_wtcs','cmap_cosine','mean_cosine']
    labs={'global_energy':'energy','coverage_mean':'cov-mean','pca_dist':'PCA-dist','coverage_worst':'cov-worst',
          'pca_mean':'PCA-mean','cmap_wtcs':'WTCS','cmap_cosine':'CMap','mean_cosine':'mean'}
    pv=sbt.pivot_table(index='method',columns='task',values='hit@1').reindex(order)
    pv=pv[['controlled','crossline','frangieh']]
    im=ax.imshow(pv.values,cmap='Blues',vmin=0.25,vmax=0.95,aspect='auto')
    ax.set_xticks(range(3)); ax.set_xticklabels(['controlled','crossline','frangieh'],fontsize=6,rotation=20,ha='right')
    ax.set_yticks(range(len(order))); ax.set_yticklabels([labs[m] for m in order],fontsize=6)
    for i in range(len(order)):
        for j in range(3):
            v=pv.values[i,j]
            ax.text(j,i,f'{v:.2f}',ha='center',va='center',fontsize=5.5,color='white' if v>0.62 else 'k')
    cb=ax.figure.colorbar(im,ax=ax,fraction=0.046,pad=0.04); cb.set_label('Hit@1',fontsize=6); cb.ax.tick_params(labelsize=5)
    ax.set_title("Advantage holds across datasets", loc='left')


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.6,3.0))
    draw_3b(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "3b.png"), dpi=200, bbox_inches="tight")
    print("wrote 3b.png")
