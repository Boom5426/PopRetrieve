"""DART Figure 3 panel 3c: per-query regret reduction ECDF
Source data: source_data/fig3c_regret_reduction.csv
Run standalone: python fig3c.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def draw_3c(ax):
    """Regret-reduction distribution (the Class-A positive), ECDF style."""
    rr=pd.read_csv(f"{REPO}/figures/source_data/fig3c_regret_reduction.csv")['regret_reduction'].values
    xs=np.sort(rr); ys=np.arange(1,len(xs)+1)/len(xs)
    ax.plot(xs,ys,color=FOCAL,lw=1.8,zorder=3)
    ax.axvline(0,ls='--',lw=1.0,color=GREY,zorder=1)
    med=np.median(rr); frac=(rr>0).mean()
    ax.axvline(med,ls=':',lw=1.1,color=FOCAL,zorder=2)
    ax.text(med+0.03,0.15,f'median\n+{med:.3f}',fontsize=6,color=FOCAL)
    ax.text(0.96,0.06,f'{frac:.0%} of queries improved\nn=621, p=4e-56',transform=ax.transAxes,
            ha='right',va='bottom',fontsize=5.8,color=FOCAL)
    ax.set_xlabel('regret reduction (mean $-$ DART coverage-worst)')
    ax.set_ylabel('cumulative fraction'); ax.set_xlim(-1.0,1.5)
    for sp in ['right','top']: ax.spines[sp].set_visible(False)
    ax.set_title("Per-query regret reduction is positive", loc='left')


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.6,3.0))
    draw_3c(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "3c.png"), dpi=200, bbox_inches="tight")
    print("wrote 3c.png")
