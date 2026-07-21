"""DART Figure 1 panel 1c: toy 2D means-tie distributions-separate (synthetic)
Synthetic gaussians, seeded RandomState(3).
Run standalone: python fig1c.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"

def draw_1c(ax):
    rng=np.random.RandomState(3)
    tgt=np.vstack([rng.normal([-1.4,0],0.35,(80,2)),rng.normal([1.4,0.3],0.35,(80,2))])
    candA=np.vstack([rng.normal([-1.4,0.1],0.38,(80,2)),rng.normal([1.4,0.2],0.38,(80,2))])
    m=tgt.mean(0); candB=rng.normal(m,0.55,(160,2))
    ax.scatter(tgt[:,0],tgt[:,1],s=7,color=GREY,alpha=0.35,edgecolors='none',label='target')
    ax.scatter(candA[:,0],candA[:,1],s=7,color=FOCAL,alpha=0.45,edgecolors='none',label='dist-match')
    ax.scatter(candB[:,0],candB[:,1],s=7,color=COMP,alpha=0.4,edgecolors='none',label='mean-match')
    ax.plot(m[0],m[1],'x',color='k',ms=9,mew=2.0)
    ax.text(m[0]+0.15,m[1]+0.55,'shared\nmean',fontsize=5.8,ha='left')
    ax.legend(fontsize=5.2,loc='upper left',frameon=False,handletextpad=0.2,labelspacing=0.2,markerscale=1.3)
    ax.set_xlabel('latent dim 1'); ax.set_ylabel('latent dim 2')
    ax.set_xticks([]); ax.set_yticks([]); ax.set_ylim(-1.6,2.0)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.4,3.0))
    draw_1c(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "1c.png"), dpi=200, bbox_inches="tight")
    print("wrote 1c.png")
