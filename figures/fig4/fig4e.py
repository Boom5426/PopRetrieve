"""PopRetrieve Figure 4 panel 4e: gate axis vs true divergence
Source data: results/exp16_gate_diagnosis/_merged_query_divergence.csv
             (source_data/fig4ef_gate_divergence.csv is a hand-built column view of it, not read here)
Run standalone: python fig4e.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
FOCAL, COMP, GREY, INK = "#5185C0", "#E99D4E", "#7A7A7A", "#1A1A1A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
key=["split_type","cell_line","heldout_drug","observed_library_fraction","seed"]

def draw_4e(ax):
    """Gate axes vs true divergence: structure_reliability (wrong dir) + conflict (too weak)."""
    mg=pd.read_csv(f"{REPO}/results/exp16_gate_diagnosis/_merged_query_divergence.csv")
    u=mg.dropna(subset=['structure_reliability_score','true_divergence']).drop_duplicates(subset=key)
    ax.scatter(u['true_divergence'],u['structure_reliability_score'],s=4.5,color=COMP,alpha=0.28,
               edgecolors='none',zorder=2)
    z=np.polyfit(u['true_divergence'],u['structure_reliability_score'],1)
    xx=np.linspace(u['true_divergence'].min(),u['true_divergence'].max(),50)
    ax.plot(xx,np.polyval(z,xx),color=COMP,lw=1.8,zorder=3)
    rho=float(u['true_divergence'].corr(u['structure_reliability_score'],method='spearman'))
    # 1:1 re-cut. The note used to sit in a data-free strip bolted onto the RIGHT of the axis
    # (xlim ran to 2.62 while the data stop at 1.90). At the printed panel width that strip is
    # 0.4 in and the note is 0.8 in, so the x axis is now cropped to the data and the note moved
    # into the data-free BAND ABOVE the cloud (no query exceeds a reliability of 0.82).
    ax.text(0.985,0.98,f'Spearman $\\rho$ = ${rho:+.2f}$\nit should rise with divergence',
            transform=ax.transAxes,fontsize=6,color=COMP,va='top',ha='right',linespacing=1.30)
    ax.set_xlabel('true response divergence',fontsize=6.4)
    ax.set_ylabel('diagnostic score:\nstructure reliability',fontsize=6.4)
    ax.set_ylim(0.26,1.03); ax.set_xlim(0.30,1.95)
    ax.set_xticks([0.5,1.0,1.5]); ax.set_yticks([0.3,0.5,0.7])
    ax.tick_params(labelsize=5.8)
    for sp in ['right','top']: ax.spines[sp].set_visible(False)
    # the axis runs past the data only to carry the annotation, so the spine stops at the data
    ax.spines['left'].set_bounds(0.26,0.82)
    ax.set_title("The diagnostic axis points the wrong way", loc='left')


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.5,3.0))
    draw_4e(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "4e.png"), dpi=200, bbox_inches="tight")
    print("wrote 4e.png")
