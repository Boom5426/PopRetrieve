"""DART Figure 2 panel 2d: mean_cosine = cmap_cosine operation identity
Source data: source_data/fig2d_operation_identity.csv
Run standalone: python fig2d.py  (writes 2d.png)
"""
import os, numpy as np, pandas as pd, matplotlib.pyplot as plt
import sys; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def draw_2d(ax):
    s=pd.read_csv(f"{REPO}/results/exp08_signature_baselines/summary.csv")
    agg=s.groupby('method')['hit@1'].mean()
    rows=[('mean cosine',agg['mean_cosine'],FOCAL,2),
          ('CMap cosine',agg['cmap_cosine'],FOCAL,1),
          ('CMap WTCS',agg['cmap_wtcs'],GREY,0)]
    for lab,val,col,y in rows:
        ax.scatter([val],[y],s=46,color=col,zorder=3)
        ax.text(val+0.006,y,f'{val:.4f}' if col==FOCAL else f'{val:.3f}',
                va='center',ha='left',fontsize=6,color=col)
    xb=0.352
    ax.plot([xb,xb],[1,2],color='k',lw=1.0)
    ax.plot([xb,xb+0.006],[2,2],color='k',lw=1.0); ax.plot([xb,xb+0.006],[1,1],color='k',lw=1.0)
    ax.text(xb-0.006,1.5,'identical\noperation',va='center',ha='right',fontsize=6)
    ax.set_xlim(0.30,0.52); ax.set_ylim(-0.6,2.6)
    ax.set_yticks([0,1,2]); ax.set_yticklabels(['CMap WTCS','CMap cosine','mean cosine'])
    ax.set_xlabel('Hit@1 (7-task mean, axis from 0.30)')
    ax.set_xticks([0.30,0.35,0.40,0.45,0.50])
    for sp in ['right','top']: ax.spines[sp].set_visible(False)
    ax.set_title("Mean-cosine and CMap are the same operation", loc='left')


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.4,3.0))
    draw_2d(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "2d.png"), dpi=200, bbox_inches="tight")
    print("wrote 2d.png")
