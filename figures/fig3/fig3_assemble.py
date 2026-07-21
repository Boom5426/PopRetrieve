"""DART Figure 3: Objective-aligned metrics reveal strong distributional signal (Class A).
6-panel figure, 2x3 grid. This gain is objective-aligned (Class A); it is NOT independent validation.
"""
import os, sys, matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fig3a import draw_3a
from fig3b import draw_3b
from fig3c import draw_3c
from fig3d import draw_3d
from fig3e import draw_3e
from fig3f import draw_3f
def build(apply_style, panel_letter):
    apply_style(sizes=(8,7,6))
    fig=plt.figure(figsize=(11.0,6.6))
    gs=fig.add_gridspec(2,3,hspace=0.5,wspace=0.42,left=0.075,right=0.965,top=0.92,bottom=0.10)
    fns={"a":draw_3a,"b":draw_3b,"c":draw_3c,"d":draw_3d,"e":draw_3e,"f":draw_3f}
    spans={"a":(0,0),"b":(0,1),"c":(0,2),"d":(1,0),"e":(1,1),"f":(1,2)}
    for k,(rr,cc) in spans.items():
        ax=fig.add_subplot(gs[rr,cc]); fns[k](ax); panel_letter(ax,k,case="lower")
    out=os.path.dirname(os.path.abspath(__file__))
    fig.savefig(os.path.join(out,"fig3_apparent_gains.png"),dpi=300,bbox_inches="tight")
    fig.savefig(os.path.join(out,"fig3_apparent_gains.pdf"),bbox_inches="tight")
    return fig


if __name__ == "__main__":
    from figstyle import apply_style, panel_letter
    build(apply_style, panel_letter)
    print("wrote fig3 composite")
