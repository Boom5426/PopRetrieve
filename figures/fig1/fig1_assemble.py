"""DART Figure 1: Distributional differences are visible, but their value depends on the evaluator.
5 panels, all drawn from code. NO Fig-4 collapse numbers (this figure sets tension only).

Panel 1a was previously a dashed placeholder box that printed "[ AI schematic 1a ]" and the path
of a prompt file into the rendered PDF. It is now a real matplotlib schematic (fig1a.py).
"""
import os, sys, matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fig1a import draw_1a
from fig1b import draw_1b
from fig1c import draw_1c
from fig1d import draw_1d
from fig1e import draw_1e
GREY="#4d4d4d"
TITLES={"a":"Two drugs, one hidden minority","b":"The drug-retrieval task","c":"Means tie, distributions separate",
        "d":"When is the evaluator independent?","e":"The metric evidence ladder"}
def build(apply_style, panel_letter):
    apply_style(sizes=(8,7,6))
    fig=plt.figure(figsize=(11.0,6.4))
    gs=fig.add_gridspec(2,6,hspace=0.42,wspace=0.55,left=0.045,right=0.97,top=0.92,bottom=0.09)
    spans={"a":(0,0,3),"b":(0,3,6),"c":(1,0,2),"d":(1,2,4),"e":(1,4,6)}
    fns={"a":draw_1a,"b":draw_1b,"c":draw_1c,"d":draw_1d,"e":draw_1e}
    for k,(rr,c0,c1) in spans.items():
        ax=fig.add_subplot(gs[rr,c0:c1]); fns[k](ax); ax.set_title(TITLES[k],loc="left"); panel_letter(ax,k,case="lower")
    out=os.path.dirname(os.path.abspath(__file__))
    fig.savefig(os.path.join(out,"fig1_problem.png"),dpi=300,bbox_inches="tight")
    fig.savefig(os.path.join(out,"fig1_problem.pdf"),bbox_inches="tight")
    return fig


if __name__ == "__main__":
    from figstyle import apply_style, panel_letter
    build(apply_style, panel_letter)
    print("wrote fig1 composite")
