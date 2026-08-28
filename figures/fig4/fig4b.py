"""PopRetrieve Figure 4 panel 4b: MoA-nDCG gain by cell line
Source data: source_data/fig4a_classA_vs_classB.csv
Run standalone: python fig4b.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
FOCAL, COMP, GREY, INK = "#5185C0", "#E99D4E", "#7A7A7A", "#1A1A1A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
key=["split_type","cell_line","heldout_drug","observed_library_fraction","seed"]

def draw_4b(ax):
    """Class-B gain ECDF per cell line.

    Presentation note (2026-07-26). The three cell lines were coloured FOCAL / GREY / COMP, i.e.
    the deck's blue "distributional" and orange "mean" roles were spent on cell-line identity,
    which invites the reader to read a method contrast into a within-PopRetrieve stratification. They
    are now three tints of the same blue, and the shared median is labelled directly.
    """
    p=pd.read_csv(f"{REPO}/figures/source_data/fig4a_classA_vs_classB.csv")
    shades=['#2C5A87',FOCAL,'#9DC1E2']; ns=[]
    for cl,col in zip(['A549','K562','MCF7'],shades):
        d=p[p.cell_line==cl]['classB_moa_ndcg_gain'].sort_values().values
        if len(d)>3:
            ys=np.arange(1,len(d)+1)/len(d)
            ns.append(len(d))
            ax.plot(d,ys,color=col,lw=1.5,label=cl)
    ax.axvline(0,ls='--',lw=0.9,color=INK,zorder=1)
    # 1:1 re-cut. An ECDF that jumps at zero leaves two free corners, upper left and lower right,
    # and at the printed panel width the key and the median note no longer both fit in one of
    # them: the key takes the upper left (no curve rises above 0.15 left of -0.2) and the note
    # takes the lower right (no curve falls below 0.7 right of +0.02). The per-line n moves
    # out of the key labels and into that note, in key order, because 'A549 n=157' set three
    # times is 0.7 in of text on a 1.2 in panel and ran onto the curves at zero.
    #
    # Residual pass (2026-07-26): that note is 0.53 in wide and anchored at 0.97 of the axes, so
    # its right edge came within 1.2 pt of panel c's rotated y label, the tightest text-to-text
    # gap in the six-figure deck. Nothing here changed, deliberately: this panel has only 0.575 in
    # of free zone between its dashed zero line and its right spine for a 0.53 in note, so pulling
    # the note left to open the gap just moves the collision onto the zero line. The clearance is
    # taken out of panel c's left pad instead (fig4_assemble.ROWS row 1). Measured after: 7.7 pt
    # to panel c's y label, 3.8 pt to this panel's own zero line (unchanged).
    ax.legend(fontsize=5.8,loc='upper left',frameon=False,handlelength=1.0,labelspacing=0.24,
              borderaxespad=0.05,handletextpad=0.25)
    ax.set_xlabel('MoA-nDCG gain,\ndistributional $-$ mean',fontsize=6.2)
    ax.set_ylabel('cumulative\nfraction',fontsize=6.5)
    ax.set_xlim(-0.62,0.62); ax.set_ylim(0,1.02)
    ax.set_xticks([-0.5,-0.25,0,0.25,0.5]); ax.tick_params(labelsize=5.8)
    ax.text(0.97,0.03,'median 0.000 in\nall three lines\nn = '+'/'.join(str(n) for n in ns),
            transform=ax.transAxes,
            fontsize=5.8,color=GREY,ha='right',va='bottom',linespacing=1.30)
    for sp in ['right','top']: ax.spines[sp].set_visible(False)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.5,3.0))
    draw_4b(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "4b.png"), dpi=200, bbox_inches="tight")
    print("wrote 4b.png")
