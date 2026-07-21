"""DART Figure 3 panel 3f: Class-A metric robustness
Source data: source_data/fig3f_classA_robustness.csv
Run standalone: python fig3f.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def draw_3f(ax):
    """Class-A robustness: all DART metrics show positive regret reduction."""
    f=pd.read_csv(f"{REPO}/figures/source_data/fig3f_classA_robustness.csv")
    labs={'DART_energy':'energy','DART_mmd':'MMD','DART_sliced_wasserstein':'sliced-W',
          'DART_coverage_mean':'cov-mean','DART_coverage_worst':'cov-worst'}
    f=f.sort_values('median_regret_reduction')
    ys=np.arange(len(f))
    ax.barh(ys,f['median_regret_reduction'],color=FOCAL,alpha=0.8,height=0.62)
    for y,v,fr in zip(ys,f['median_regret_reduction'],f['frac_improved']):
        ax.text(v+0.002,y,f'+{v:.3f}',va='center',fontsize=5.8,color=FOCAL)
    ax.set_yticks(ys); ax.set_yticklabels([labs[m] for m in f['method']],fontsize=6)
    ax.set_xlabel('median regret reduction'); ax.set_xlim(0,0.14)
    ax.axvline(0,color='k',lw=0.8)
    for sp in ['right','top']: ax.spines[sp].set_visible(False)
    ax.set_title("Every distributional metric shows the gain", loc='left')


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.6,3.0))
    draw_3f(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "3f.png"), dpi=200, bbox_inches="tight")
    print("wrote 3f.png")
