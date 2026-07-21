"""DART Figure 5 panel 5b: analytic boundary alpha*=B/(A+B)
Source data: source_data/fig5a_theoretical_boundary.csv
Run standalone: python fig5b.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
H = os.path.join(REPO, "results", "exp11_hir_benchmark")
S = os.path.join(REPO, "results", "exp11_synthetic_phase_diagram")

def draw_5b(ax):
    """Analytic boundary alpha* = B/(A+B) with decision regions."""
    tb=pd.read_csv(f"{H}/theoretical_boundary.csv")
    tb['ratio']=tb['B']/(tb['A']+tb['B'])
    u=tb.dropna(subset=['ratio']).drop_duplicates(subset=['A','B'])
    # boundary curve: alpha_star vs ratio (perfect identity) -> show as decision line in (ratio, alpha) space
    xx=np.linspace(0,1,100)
    ax.plot(xx,xx,color='k',lw=1.5,zorder=3)
    ax.fill_between(xx,xx,1,color=COMP,alpha=0.12)   # alpha>alpha*: minority wins (DART regime)
    ax.fill_between(xx,0,xx,color=FOCAL,alpha=0.12)   # alpha<alpha*: majority wins (mean sufficient)
    ax.text(0.72,0.30,'majority optimal\n(mean sufficient)',fontsize=6,color=FOCAL,ha='center')
    ax.text(0.30,0.75,'minority optimal\n(structure matters)',fontsize=6,color=COMP,ha='center')
    ax.text(0.62,0.55,r'$\alpha^*=\dfrac{B}{A+B}$',fontsize=8,rotation=41,color='k')
    ax.set_xlabel(r'welfare ratio $B/(A{+}B)$'); ax.set_ylabel(r'minority fraction $\alpha$')
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    for sp in ['right','top']: ax.spines[sp].set_visible(False)
    ax.set_title("Analytic decision boundary", loc='left')


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.5,3.0))
    draw_5b(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "5b.png"), dpi=200, bbox_inches="tight")
    print("wrote 5b.png")
