"""Figure 5 panel a: the task, with candidate responses OBSERVED. Schematic; no computed value.
Run standalone: python fig5a.py

The drawing lives in figures/phase2_task.py and is shared with Figure 6 panel a, which draws the
identical task with the third station replaced by a forward predictor. That is the only difference
between the two pages, so it has to be the only difference between the two schematics; see the
module docstring there for why the switch is a parameter rather than a second drawing.
"""
import os as _os
import sys as _sys

_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from phase2_task import draw_task  # noqa: E402


def draw_5a(ax):
    return draw_task(ax, "oracle")


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(4.09, 1.67))
    draw_5a(ax)
    fig.savefig(_os.path.join(_os.path.dirname(__file__), "5a.png"), dpi=200, bbox_inches="tight")
    print("wrote 5a.png")
