"""EvalShift Figure 4 panel 4a: Class A vs Class B sign flip
Source data: source_data/fig4a_classA_vs_classB.csv
Run standalone: python fig4a.py
"""
import os, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
FOCAL, COMP, GREY, INK = "#5185C0", "#E99D4E", "#7A7A7A", "#1A1A1A"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
key=["split_type","cell_line","heldout_drug","observed_library_fraction","seed"]

# The plotted view of the y axis, and the top of the axes box. VIEW_CUT is where the drawn
# distributions and the left spine both stop; the band between VIEW_CUT and AXES_TOP carries the
# two summary blocks and holds no data ink at all.
VIEW_BOT, VIEW_CUT, AXES_TOP = -1.05, 1.42, 3.12

def draw_4a(ax):
    """Same 480 paired queries, two metric classes.

    Presentation note (2026-07-26). The old version drew violinplot(showmedians=True) inside
    ylim (-0.9, 1.05) while the Class-A distribution runs to +2.82, so the extrema whiskers were
    cut by the axis with nothing saying so. The view still stops at +1.4 (opening it to +2.9
    would flatten the Class-B violin to a line), but the truncation is now stated on the panel,
    and the summary is drawn as an explicit median dot on an interquartile bar rather than as a
    whisker the axis silently amputates.

    Geometry note (2026-07-26, 1:1 re-cut). The composite is now authored at its printed width, so
    this panel is 1.4 in wide instead of 2.1 in and the two summary blocks no longer fit in the
    strip to the right of the violins. They are set above the violins instead, and the left spine
    stops at +1.42 so the reader can see where the plotted view ends.

    Overlap fix (2026-07-26, residual pass). Those blocks were centered over their violins inside
    ylim (-1.05, 2.05), and matplotlib evaluates a violin's kernel over the full observed support:
    Class A runs to +2.823, so a hairline of real density was drawn through all three lines of
    "median / +0.129 / 73% > 0" and through "tail to +2.8". Text on plotted ink is not fixable by
    nudging inside this geometry, because the hairline sits exactly on the violin's centre line at
    every height. Three things changed, none of them statistical:
      * the drawn distributions are CLIPPED at VIEW_CUT = +1.42, which is where the left spine
        already declared the view to end; ink was previously drawn to the ylim (+2.05) while the
        spine stopped at +1.42, so the panel now says one thing instead of two. What is beyond the
        cut is still stated on the panel, as the third line of the Class-A block;
      * the axes box is opened to +3.12 and the row is 1.05 in tall instead of 0.78 in, which
        leaves a 0.43 in data-free band above the cut and reproduces the violins at their previous
        scale (0.2518 versus 0.2516 in per unit) rather than flattening them to make room;
      * the blocks are set flush left and flush right instead of centred, which puts 21 pt between
        them; they were 2.4 pt apart when their value lines were set on one line and centred.
    """
    p=pd.read_csv(f"{REPO}/figures/source_data/fig4a_classA_vs_classB.csv")
    a=p['classA_regret_reduction']; b=p['classB_moa_ndcg_gain']
    parts=ax.violinplot([a,b],positions=[0,1],showmedians=False,showextrema=False,widths=0.62)
    # Clip to the plotted view. The rectangle is in data coordinates and is resolved at draw time,
    # so it tracks the limits set below.
    view=Rectangle((-0.60,VIEW_BOT),2.20,VIEW_CUT-VIEW_BOT,transform=ax.transData)
    for i,pc in enumerate(parts['bodies']):
        pc.set_facecolor(FOCAL if i==0 else COMP); pc.set_alpha(0.55); pc.set_edgecolor('none')
        pc.set_clip_path(view)
    for i,v in enumerate([a,b]):
        q1,med,q3=np.percentile(v,[25,50,75])
        ax.vlines(i,q1,q3,color=INK,lw=2.6,zorder=3)
        ax.plot(i,med,'o',ms=3.4,mfc='white',mec=INK,mew=0.8,zorder=4)
    ax.axhline(0,ls='--',lw=0.9,color=GREY,zorder=1)
    # One block per violin, in the data-free band above VIEW_CUT: flush left over Class A, flush
    # right over Class B. The truncation note is the Class-A block's third line rather than a
    # separate grey artist, because two artists stacked in this band left only 4 pt between them
    # and the tail being reported is Class A's own.
    ax.text(-0.58,3.04,f'median $+${a.median():.3f}\n{(a>0).mean():.0%} $>$ 0\n'
                       f'tail to $+${a.max():.1f}',
            ha='left',va='top',fontsize=6,color=FOCAL,linespacing=1.30)
    ax.text(1.58,3.04,f'mean ${b.mean():+.3f}$\n{(b>0).mean():.0%} $>$ 0',
            ha='right',va='top',fontsize=6,color=COMP,linespacing=1.30)
    ax.set_xticks([0,1])
    ax.set_xticklabels(['Class A\nregret reduction','Class B\nMoA-nDCG gain'],fontsize=6.2)
    ax.set_ylabel('distributional\n$-$ mean advantage',fontsize=6.5)
    # Centre the y label on the PLOTTED view rather than on the axes box. The box now runs to
    # AXES_TOP to carry the summary blocks, and a label centred on it would point at the blank
    # band instead of at the distributions and the ticks it names.
    ax.yaxis.label.set_y(((VIEW_BOT+VIEW_CUT)/2-VIEW_BOT)/(AXES_TOP-VIEW_BOT))
    ax.set_ylim(VIEW_BOT,AXES_TOP); ax.set_xlim(-0.60,1.60)
    ax.set_yticks([-1.0,-0.5,0.0,0.5,1.0])
    ax.spines['left'].set_bounds(VIEW_BOT,VIEW_CUT)
    for sp in ['right','top']: ax.spines[sp].set_visible(False)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.5,3.0))
    draw_4a(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "4a.png"), dpi=200, bbox_inches="tight")
    print("wrote 4a.png")
