"""DART Figure 4 panel 4f: recommendation cannot sort divergence
Source data: source_data/fig4ef_gate_divergence.csv
Run standalone: python fig4f.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
FOCAL, COMP, GREY = "#5185C0", "#E99D4E", "#7A7A7A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
key=["split_type","cell_line","heldout_drug","observed_library_fraction","seed"]

def draw_4f(ax):
    """Binary recommendation does not separate divergence (Mann-Whitney p=0.09)."""
    mg=pd.read_csv(f"{REPO}/results/exp16_gate_diagnosis/_merged_query_divergence.csv")
    u=mg.dropna(subset=['true_divergence']).drop_duplicates(subset=key)
    rec=u[u.recommendation_mode=='DART_recommended']['true_divergence']
    nonrec=u[u.recommendation_mode!='DART_recommended']['true_divergence']
    bp=ax.boxplot([rec,nonrec],positions=[0,1],widths=0.55,patch_artist=True,showfliers=False)
    for patch,col in zip(bp['boxes'],[FOCAL,GREY]): patch.set_facecolor(col); patch.set_alpha(0.5)
    for med in bp['medians']: med.set_color('k')
    ax.set_xticks([0,1]); ax.set_xticklabels([f'recommended\nn={len(rec)}',f'non-rec\nn={len(nonrec)}'],fontsize=6)
    ax.set_ylabel('true response divergence')
    ax.text(0.5,0.97,'Mann-Whitney p=0.09',transform=ax.transAxes,ha='center',va='top',fontsize=6,color=GREY)
    for sp in ['right','top']: ax.spines[sp].set_visible(False)
    ax.set_title("Recommendation cannot sort by divergence", loc='left')


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.5,3.0))
    draw_4f(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "4f.png"), dpi=200, bbox_inches="tight")
    print("wrote 4f.png")
