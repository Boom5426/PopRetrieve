"""Figure 6 panel a: the same task, with candidate responses PREDICTED. Schematic; no value.
Run standalone: python fig6a.py

Deliberately the same drawing as Figure 5 panel a, from the same function in
figures/phase2_task.py, with one station and one line changed. A reader comparing the two pages
must be able to see that the experiment changed in exactly one place, and the only way to
guarantee that is for the two panels to be one drawing with one switch.
"""
import os as _os
import sys as _sys

_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from phase2_task import draw_task  # noqa: E402


def draw_6a(ax):
    return draw_task(ax, "predicted")


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(4.09, 1.67))
    draw_6a(ax)
    fig.savefig(_os.path.join(_os.path.dirname(__file__), "6a.png"), dpi=200, bbox_inches="tight")
    print("wrote 6a.png")
