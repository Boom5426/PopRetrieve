"""Figure 5 panels e and f: the natural-tissue arm, retuned for the 6.9 in print canvas.

WHY THIS FILE EXISTS
--------------------
Panels e (Gate 1 on patient glioblastoma) and f (the premise tested on the same tumours) are drawn
by ``figures/fig7/fig7_natural.py``, which is where they were authored when they were their own
figure. The data loading, the marks, the statistics and the colours all stay there: this module
imports those two draw functions unchanged, so there is exactly one copy of the plotting code and
no possibility of the two versions drifting apart.

What this module adds is GEOMETRY AND TYPOGRAPHY ONLY. Figure 5 is now authored at its final print
width (6.9 in) instead of 11.6 in, so each of these panels is ~1.3-1.6 in wide instead of ~3.2 in,
while the annotation text is at last full size. The interpretive sentences that fit at 11.6 in
("(near-orthogonal)", "additive-predictor limit ... no divergence at all") no longer fit, and at
this size they run across the point cloud. They are shortened here and the sentences they carried
are in the Fig. 5 caption.

Nothing below changes a data value, a statistic, a colour or a mark. Every edit is a set_text,
set_position or set_fontsize on an annotation, plus two axis labels wrapped onto a second line.
Each edit is keyed to the annotation it retunes by a substring of the ORIGINAL text and raises if
that annotation is not found, so an upstream rewording fails the build here instead of silently
leaving the old, too-wide label on the page.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "fig7")))

from fig7_natural import draw_b as _draw_gate1_natural
from fig7_natural import draw_c as _draw_premise_natural


def _retune(ax, edits, panel):
    """Apply {substring-of-original-text: {text/position/fontsize/...}} to ax's annotations.

    Raises if a key matches no annotation or more than one, because a silently skipped edit here
    means a label that overruns its panel on the printed page.
    """
    for key, spec in edits.items():
        hits = [t for t in ax.texts if key in t.get_text()]
        if len(hits) != 1:
            raise KeyError(
                f"panel {panel}: {len(hits)} annotation(s) contain {key!r}, expected exactly 1. "
                f"fig7_natural.py was reworded; re-point this retune at the new text rather than "
                f"letting the un-retuned label print.")
        t = hits[0]
        if "text" in spec:
            t.set_text(spec["text"])
        if "position" in spec:
            t.set_position(spec["position"])
        if "fontsize" in spec:
            t.set_fontsize(spec["fontsize"])
        if "ha" in spec:
            t.set_ha(spec["ha"])
        if "va" in spec:
            t.set_va(spec["va"])


def draw_nat_gate1(ax):
    """Panel e. Induced response cosine in patient tumours against our constructed mixtures."""
    _draw_gate1_natural(ax)
    _retune(ax, {
        # the band is keyed by its two numbers; "(near-orthogonal)" is the interpretation and is
        # in the caption, which also gives the 1-cos divergence scale the comparison should use
        "constructed mixtures": {"text": "constructed\n0.014-0.044", "position": (0.60, 0.075)},
        # 35 characters of italic gloss ran from the right spine back across the point column
        "additive-predictor limit": {"text": "cos = 1:\nno divergence",
                                     "position": (1.64, 0.98)},
        # n stays on the panel; "patient-drug" is stated in the caption
        "patient-drug pairs": {"text": "n = 17 pairs", "position": (0.60, 1.08)},
    }, "e")
    # the full label, cos(d_malignant, d_myeloid), is 50 characters: rotated, that is 2.1 in of
    # text against a 1.18 in axes, so it would run past the panel above. The caption defines it.
    ax.set_ylabel("induced response cosine", fontsize=6.2)


def draw_nat_premise(ax):
    """Panel f. Mean-signature similarity against malignant-compartment response similarity."""
    _draw_premise_natural(ax)
    # the stats block is built from the data in fig7_natural; only its third line is shortened,
    # and it is shortened by editing the rendered string, never by retyping a number
    hits = [t for t in ax.texts if "Spearman" in t.get_text()]
    if len(hits) != 1:
        raise KeyError("panel f: expected exactly one Spearman annotation")
    hits[0].set_text(hits[0].get_text().replace(" of them from ONE patient", " from ONE patient"))
    # one line of 37 characters is 1.5 in of text under a 1.2 in axes
    ax.set_xlabel("cos(mean signature of\ndrug A, drug B)", fontsize=6.2)
