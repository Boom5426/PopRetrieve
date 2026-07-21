"""DART Figure 5 panel 5e: benchmark QC
Source data: source_data/fig5e_sanity_checks.csv
Run standalone: python fig5e.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
H = os.path.join(REPO, "results", "exp11_hir_benchmark")
S = os.path.join(REPO, "results", "exp11_synthetic_phase_diagram")

def draw_5e(ax):
    """QC sanity checks panel."""
    sc=pd.read_csv(f"{H}/sanity_checks.csv")
    labs={'no_conflict_flip_rate':'no-conflict\nflip rate','median_boundary_margin':'median\nboundary margin',
          'predicted_mean_dart_eq_mean':'pred-mean:\nDART=mean'}
    ys=np.arange(len(sc))
    for y,(_,row) in zip(ys,sc.iterrows()):
        passed=row['pass']==1
        ax.barh(y,row['value'],color=FOCAL if passed else COMP,alpha=0.8,height=0.5)
        ax.plot(row['threshold'],y,'|',ms=14,color='k',mew=1.5)
        ax.text(row['value']+0.02,y,f"{row['value']:.3f} {'PASS' if passed else 'FAIL'}",va='center',fontsize=5.8,
                color=FOCAL if passed else COMP)
    ax.set_yticks(ys); ax.set_yticklabels([labs.get(c,c) for c in sc['check']],fontsize=5.8)
    ax.set_xlabel('value (| = threshold)'); ax.set_xlim(0,1.1)
    for sp in ['right','top']: ax.spines[sp].set_visible(False)
    ax.set_title("Benchmark quality control", loc='left')


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.5,3.0))
    draw_5e(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "5e.png"), dpi=200, bbox_inches="tight")
    print("wrote 5e.png")
