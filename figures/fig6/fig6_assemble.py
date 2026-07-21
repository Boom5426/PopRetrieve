"""DART Figure 6: Structure preservation and identifiability constrain distribution-aware retrieval.
7-panel two-gate mechanism figure. Assembles a-g into fig6_two_gate.{png,pdf}.
"""
import os, sys, matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fig6a import draw_6a
from fig6b import draw_6b
from fig6c import draw_6c
from fig6d import draw_6d
from fig6e import draw_6e
from fig6f import draw_6f
from fig6g import draw_6g

# Panel b's title used to read "No predictor gives a positive gain". The deck's own source
# data (source_data/fig6b_predictor_gaps.csv) falsifies it: the latent-linear predictor's
# nDCG@10 gain is +0.027. The panel only looked consistent because a reindex key typo
# dropped that predictor. The honest summary is that the gain is small and its SIGN is not
# consistent across predictors, which is a weaker claim than the old title and a true one.
TITLES={"a":"Retrieval limited by the predictor",
        "b":"Gain is small and sign-inconsistent",
        "c":"Structure survives; divergence does not",
        "d":"Structure diagnostics, real vs predicted",
        "e":"No method recovers subpopulations","f":"More cells cannot fix low separability",
        "g":"No positive effect at any divergence"}

def build(apply_style, panel_letter):
    apply_style(sizes=(8,7,6))
    fig=plt.figure(figsize=(11.4,6.8))
    gs=fig.add_gridspec(2,12,hspace=0.66,wspace=2.4,left=0.05,right=0.965,top=0.92,bottom=0.11)
    spans={"a":(0,0,3),"b":(0,3,6),"c":(0,6,9),"d":(0,9,12),"e":(1,0,4),"f":(1,4,8),"g":(1,8,12)}
    fns={"a":draw_6a,"b":draw_6b,"c":draw_6c,"d":draw_6d,"e":draw_6e,"f":draw_6f,"g":draw_6g}
    for k,(rr,c0,c1) in spans.items():
        ax=fig.add_subplot(gs[rr,c0:c1]); fns[k](ax); ax.set_title(TITLES[k],loc="left")
        panel_letter(ax,k,case="lower")
    out=os.path.dirname(os.path.abspath(__file__))
    fig.savefig(os.path.join(out,"fig6_two_gate.png"),dpi=300,bbox_inches="tight")
    fig.savefig(os.path.join(out,"fig6_two_gate.pdf"),bbox_inches="tight")
    return fig


if __name__ == "__main__":
    from figstyle import apply_style, panel_letter
    build(apply_style, panel_letter)
    print("wrote fig6_two_gate.{png,pdf}")
