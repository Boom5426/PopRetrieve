"""PopRetrieve Figure 3 panel 3l: the same four rankings scored against ABSOLUTE potency.

WHAT THE PANEL CLAIMS
---------------------
Absolute GDSC2 potency is a different endpoint from the drug-drug functional similarity that
panels h and i are graded on, and it rewards a different thing. Graded against it, the two
rankings that keep the candidate's raw response scale sit on the negative side of zero, the
control-subtracted mean cosine sits just above zero, and the ranking that compares no
distributions at all, sorting candidates by their own response magnitude, is far and away the
highest, positive in every one of the 103 queries.

This panel is a CONTROL ON THE ENDPOINT CHOICE in h and i. It is not evidence that retrieval
fails, and it must not be read as a method comparison in the paper's sense. A similarity
retriever is asked which candidate RESEMBLES the query; absolute potency asks which candidate
kills hardest. Handed a weak query, a correctly working retriever SHOULD return other weak
candidates, so a negative association here is the expected behaviour of a working instrument on
a mismatched endpoint, not a failure of it. That is not left as an argument: across the 103
queries the energy ranking's agreement with potency tracks the QUERY's own potency (Spearman
rho = -0.55 against the query's GDSC2 AUC, the same sign in all three cell lines), which is what
"returns candidates like the query" predicts and what a broken retriever would not produce. It is
asserted below. Panel m carries the other half of the mechanism: the energy distance between
query and candidate largely tracks the candidate's own magnitude (median rho +0.791).

WHICH WAY IS UP ON THIS AXIS
----------------------------
GDSC2 AUC runs OPPOSITE to potency: a low AUC is a potent drug. The plotted quantity is the
Spearman correlation between a ranking and the potency ranking built by the source script as
`rankdata(auc)`, rank 1 = lowest AUC = most potent, so POSITIVE means "puts the most potent
candidates first" and negative means "puts the least potent first". The axis label therefore says
"GDSC2 potency (low AUC)" and not "absolute potency (GDSC2 AUC)": the second wording equates
potency with AUC, which is backwards, so a GDSC-literate reader would take every sign on this
axis the wrong way round. The v2 source script exists because of a sign inversion and this figure
will not reintroduce one in a label. "Absolute" is not lost: it is the first word of the phrase
one line above, and the axis's shorter form is what leaves the label 0.25 in of margin inside its
box instead of 0.05 in.

Source data: figures/source_data/fig3hi_class_c_potency.csv
  103 leave-one-drug-out queries, SciPlex3 x GDSC2 at 10 uM, three cell lines, the v2 analysis
  with the corrected energy sign. Every number drawn is a median or a quartile computed from that
  file at draw time; nothing here is typed in.
Also read at draw time: figures/source_data/fig3hi_class_c_functional.csv, because the panel's
  one phrase is a claim about TWO endpoints and is asserted against both.

JUDGEMENT CALLS A READER COULD REASONABLY DISAGREE WITH
-------------------------------------------------------
1. BLUE AND ORANGE ARE OBJECT COLOURS HERE, AND THE HALF-PLANES ARE NOT WASHED. fig3_style makes
   blue and orange a statement about sign wherever a signed population-minus-mean advantage is
   plotted, and object colours only where retrieval families are genuinely compared. Two families
   are genuinely compared on this axis, so they take the object colours. But the SIGN on this
   axis does not mean what the wash means: negative here says "ranks the least potent candidates
   first", not "mean-signature retrieval is favoured". Washing the half-planes would attach the
   population-versus-mean reading to an axis that does not carry it, so fig3_style.sign_field is
   deliberately not called and neither side is labelled. Zero is drawn as a bare datum rule.
2. FILL SEPARATES THE TWO MEAN COSINES, and it is doing double duty. Within the orange family,
   filled is the raw mean cosine and open is the control-subtracted one, which is the pair the
   panel needs to distinguish because control subtraction is what removes the magnitude channel.
   The green control is also open, for the different reason that it performs no retrieval, which
   is the encoding panel h already uses. Colour separates the two meanings; the labels state both.
   Anyone who wanted one meaning per channel would need a hue this figure has already spent.
3. MEDIAN AND INTERQUARTILE RANGE ACROSS THE 103 QUERIES, not the per-cell-line medians panel h
   draws and not the full per-query cloud. At 0.64 in of axes height the four rows are 11 pt
   apart, where 103 jittered points per row are unreadable. The quartiles carry the part of the
   distribution the claim rests on: the control-subtracted interval straddles zero while the
   magnitude interval is nowhere near it. The sign is consistent across all three cell lines for
   all four rows, which is asserted below and stated in the caption rather than drawn.
4. THE FOURTH ROW'S INTERVAL IS NOT THE SAME KIND OF QUANTITY AS THE OTHER THREE, and the panel
   cannot show that. The magnitude ranking is QUERY-INDEPENDENT: it produces one ordering per
   cell line, so within a line its per-query rho is all but constant (mean within-line IQR 0.026)
   and nearly all of the drawn width (pooled IQR 0.115) is the difference BETWEEN the three cell
   lines. The three retrieval rows are the opposite: their within-line IQR is currently wider than
   their pooled one (0.344 against 0.281, 0.356 against 0.286, 0.459 against 0.449), so their
   intervals really are query-to-query spread. Both relations are asserted below, at the loose
   threshold of half the pooled IQR, because what has to hold is the direction of the contrast
   and not today's exact ratio. A reader comparing interval WIDTHS across the four rows would conclude the
   magnitude ranking is the steadiest across queries; it is constant across queries by
   construction, and the caption has to say so. The row is kept in the same grammar because the
   panel's claim is about where the four medians sit, not about how wide they are.
5. ROW ORDER IS FIXED BY FAMILY AND STORY, not sorted by median. Energy (-0.520) and the raw mean
   cosine (-0.533) differ by 0.013, which is not an ordering, and sorting on it would invite a
   reader to rank them.
6. THE FUNCTIONAL-SIMILARITY COUNTERPARTS ARE NOT DRAWN, although the same 103 queries carry them
   in fig3hi_class_c_functional.csv (energy +0.276, raw mean cosine +0.241, control-subtracted
   mean cosine +0.083, magnitude alone -0.330). Drawing arrows from those to these would put the
   study's one external win, +0.276, on the page being dragged across zero, which competes with
   the number panel h exists to make and reads as a refutation rather than as a control. The
   endpoint-to-endpoint comparison belongs to the caption. Run this module standalone and it
   prints both endpoints side by side, so the docstring above can be checked against the files.
   ONE CAVEAT THE CAPTION MUST CARRY: the two tables share the 103 query keys but not every
   candidate pool. Five MCF7 queries score fewer candidates under the functional oracle than
   under potency (four at 33 against 34, one at 30 against 34), because the functional oracle
   needs a GDSC2 dose-response profile for the candidate as well as for the query. The
   endpoint-to-endpoint medians are therefore near-paired, not exactly paired. Standalone output
   counts the mismatched queries rather than asserting an equality that is not true.
7. VALUE LABELS SIT ON THE OUTER SIDE OF THE INTERVAL, past the first quartile for a negative
   median and past the third for a positive one, so each number lies in empty space on the side
   its effect points. The number is the MEDIAN, not the interval end it sits beside.

THE PANEL'S PHRASE IS A TWO-ENDPOINT CLAIM. "Absolute potency is a different endpoint" cannot be
read off this panel's ink alone; its other half is in panel h. So it is not left to the reader:
_assert_endpoints_differ reads the functional table at draw time and requires the three sign
changes below to still be there. If the endpoints ever stop disagreeing, the build fails instead
of leaving a phrase the numbers no longer support.

BE EXACT ABOUT WHAT CHANGES SIGN. Between the functional endpoint and this one, energy (+0.276 to
-0.520), the raw mean cosine (+0.241 to -0.533) and magnitude alone (-0.330 to +0.692) all change
sign; the control-subtracted mean cosine does NOT, moving from +0.083 to +0.105, a collapse
towards zero. The retired ed5.py phrasing "every ranking's correlation with potency inverts" is
wrong on the third row of this panel and is not reproduced here or in the caption.

Run standalone: python fig3l.py
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from fig3_style import (EXT, HAIRLINE, MEAN, POP, PT_ANNOT, PT_TICK, REPO, SUBTLE, TEXT,
                        bare_axes, title, zero_rule)

SRC = os.path.join(REPO, "figures", "source_data", "fig3hi_class_c_potency.csv")
FUNCTIONAL = os.path.join(REPO, "figures", "source_data", "fig3hi_class_c_functional.csv")

N_QUERIES = 103

# (column, short label, colour, filled). Labels are short because the left pad is 1.20 in; the
# caption expands "ctrl-subtr." to control-subtracted and "magnitude" to candidate response
# magnitude. "no retrieval" stays on the panel: it is what stops the green row being read as a
# rival method that beat the paper's own.
ROWS = [
    ("energy_rho",           "energy",                   POP,  True),
    ("mean_cosine_raw_rho",  "mean cosine, raw",         MEAN, True),
    ("mean_cosine_ctrl_rho", "mean cosine, ctrl-subtr.", MEAN, False),
    ("magnitude_only_rho",   "magnitude, no retrieval",  EXT,  False),
]

# The two rankings that keep the candidate's raw response scale, i.e. the ones the magnitude
# channel is expected to drag negative against an absolute-potency endpoint.
KEEPS_RAW_SCALE = ("energy_rho", "mean_cosine_raw_rho")
CTRL = "mean_cosine_ctrl_rho"
NO_RETRIEVAL = "magnitude_only_rho"
# The query's own potency, on the axis the source table stores it on. Low AUC = potent.
QUERY_AUC = "query_auc"

TITLE_3L = "Absolute potency is a different endpoint"

# Axis: the spine spans the drawn data, the view is wider so each median's value label has empty
# space to sit in on the side its effect points.
SPINE_LO, SPINE_HI = -0.75, 0.75
XLIM_LO, XLIM_HI = -0.95, 1.00
LABEL_GAP = 0.050


def _iqr(x):
    q1, q3 = np.percentile(np.asarray(x, dtype=float), [25, 75])
    return float(q3 - q1)


def _load(path, what):
    """Read a per-query table, refusing to draw anything the file does not support."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"{path} does not exist. Run the Class-C analysis and export the per-query {what} "
            f"table. This panel will not render placeholder correlations.")
    d = pd.read_csv(path)
    missing = [c for c, _l, _c, _f in ROWS if c not in d.columns]
    if missing:
        raise KeyError(f"{path} is missing {missing}; panel 3l needs all four ranking columns.")
    if len(d) != N_QUERIES:
        raise ValueError(f"{path} has {len(d)} queries; panel 3l and the caption both say "
                         f"{N_QUERIES}. Fix one or the other, do not draw the mismatch.")
    if d[[c for c, _l, _c, _f in ROWS]].isna().any().any():
        raise ValueError(f"{path} carries missing correlations; medians would be over a subset "
                         f"the caption does not describe.")
    return d


def _assert_claims(d, med):
    """Assert, from the data, every relationship this panel and its caption state.

    A drawn number can go stale silently; an assertion cannot. These are the statements the
    panel makes with ink, plus the cross-cell-line consistency, the interval-kind caveat and the
    mechanism reading that its docstring and caption claim.
    """
    for col in KEEPS_RAW_SCALE:
        assert med[col] < 0, (
            f"3l says the rankings that keep the raw response scale sit below zero against "
            f"absolute potency, but {col} has median {med[col]:+.3f}.")

    assert med[CTRL] > 0, (
        f"3l says the control-subtracted mean cosine does NOT change sign against potency, "
        f"but its median is {med[CTRL]:+.3f}. Do not redraw it as an inversion.")
    others = [abs(med[c]) for c, _l, _c, _f in ROWS if c != CTRL]
    assert abs(med[CTRL]) < min(others), (
        f"3l draws the control-subtracted mean cosine as the row nearest zero; it is not "
        f"({abs(med[CTRL]):.3f} against {min(others):.3f}).")

    retrieval = [med[c] for c, _l, _c, _f in ROWS if c != NO_RETRIEVAL]
    assert med[NO_RETRIEVAL] > max(retrieval), (
        f"3l draws the no-retrieval magnitude scalar as the highest row; it is not "
        f"({med[NO_RETRIEVAL]:+.3f} against {max(retrieval):+.3f}).")
    assert (d[NO_RETRIEVAL] > 0).all(), (
        f"3l's caption says the magnitude scalar is positive in all {N_QUERIES} queries; "
        f"{int((d[NO_RETRIEVAL] <= 0).sum())} are not.")

    # Judgement call 3: the caption says every row keeps its sign in all three cell lines. All
    # four rows, not the two the panel leans hardest on.
    for col, _lab, _c, _f in ROWS:
        by_line = d.groupby("cell_line")[col].median()
        assert (np.sign(by_line) == np.sign(med[col])).all(), (
            f"3l's caption says every row's sign holds in all three cell lines; {col} has "
            f"pooled median {med[col]:+.3f} against per-line {by_line.round(3).to_dict()}.")

    # Judgement call 4: the fourth row's interval is between-cell-line, the other three are
    # query-to-query. The caption has to say so, so the file has to keep it true.
    for col, _lab, _c, _f in ROWS:
        pooled = _iqr(d[col])
        within = float(np.mean([_iqr(g[col]) for _k, g in d.groupby("cell_line")]))
        if col == NO_RETRIEVAL:
            assert within < 0.5 * pooled, (
                f"3l's caption says the no-retrieval row's drawn width is mostly the difference "
                f"between cell lines (within-line IQR {within:.3f}, pooled {pooled:.3f}); it is "
                f"no longer, so stop describing it that way.")
        else:
            assert within > 0.5 * pooled, (
                f"3l's caption contrasts the retrieval rows' intervals as genuine query-to-query "
                f"spread; {col} now has within-line IQR {within:.3f} against pooled {pooled:.3f}, "
                f"so its width has become a between-cell-line effect too.")

    # The panel's defence, which the caption states: a negative rho here is a working retriever
    # on a mismatched endpoint. If the retriever returns candidates like the query, then a potent
    # query (LOW AUC) is the one whose rho comes out positive, so rho must fall as query AUC
    # rises. It does, pooled and in each cell line.
    assert QUERY_AUC in d.columns, (
        f"{SRC} is missing {QUERY_AUC}; 3l's caption says a negative rho is the expected "
        f"behaviour of a working retriever, and that claim is checked against the query's own "
        f"potency, not asserted by hand.")
    for col in KEEPS_RAW_SCALE:
        pooled_r = float(d[[col, QUERY_AUC]].corr(method="spearman").iloc[0, 1])
        assert pooled_r < -0.2, (
            f"3l's caption reads the negative medians as a similarity retriever tracking the "
            f"query's own potency, which requires {col} to fall as the query's AUC rises; the "
            f"pooled Spearman rho is {pooled_r:+.3f}.")
        by_line = {k: float(g[[col, QUERY_AUC]].corr(method="spearman").iloc[0, 1])
                   for k, g in d.groupby("cell_line")}
        assert all(v < 0 for v in by_line.values()), (
            f"3l's caption says that reading holds in all three cell lines; {col} against "
            f"{QUERY_AUC} gives {({k: round(v, 3) for k, v in by_line.items()})}.")


def _assert_endpoints_differ(med):
    """Assert the panel's one phrase, which is a claim about two endpoints, from both files.

    "Absolute potency is a different endpoint" is not readable from this panel's ink; the other
    half of the comparison is panel h. Checking it here means a data change breaks the build
    rather than leaving a true-looking phrase over numbers that no longer support it.
    """
    f = _load(FUNCTIONAL, "functional-similarity")
    fmed = {c: float(f[c].median()) for c, _l, _c, _f in ROWS}
    for col in list(KEEPS_RAW_SCALE) + [NO_RETRIEVAL]:
        assert fmed[col] * med[col] < 0, (
            f"3l's phrase says absolute potency is a different endpoint, on the strength of "
            f"{col} changing sign between them; it now runs {fmed[col]:+.3f} to {med[col]:+.3f}.")
    assert fmed[CTRL] > 0 and med[CTRL] > 0, (
        f"3l's docstring and caption are exact that the control-subtracted mean cosine is the "
        f"one row that does NOT change sign; it runs {fmed[CTRL]:+.3f} to {med[CTRL]:+.3f}.")
    return fmed


def draw_3l(ax):
    d = _load(SRC, "absolute-potency")
    med = {c: float(d[c].median()) for c, _l, _c, _f in ROWS}
    _assert_claims(d, med)
    _assert_endpoints_differ(med)

    ys = np.arange(len(ROWS))[::-1]
    for y, (col, _lab, colour, filled) in zip(ys, ROWS):
        q1, q3 = (float(v) for v in np.percentile(d[col].values, [25, 75]))
        assert XLIM_LO < q1 - LABEL_GAP and q3 + LABEL_GAP < XLIM_HI, (
            f"{col} quartiles {q1:.3f},{q3:.3f} leave no room inside the view for the value "
            f"label this panel puts {LABEL_GAP} outside them.")
        ax.plot([q1, q3], [y, y], color=colour, lw=1.4, solid_capstyle="butt", zorder=3)
        ax.plot([med[col]], [y], marker="o", ms=4.6, mew=1.0, zorder=4,
                mfc=colour if filled else "white", mec=colour, ls="none")
        # The median's value, on the side its effect points, clear of the interval it summarises.
        if med[col] < 0:
            ax.text(q1 - LABEL_GAP, y, f"{med[col]:+.2f}", ha="right", va="center",
                    fontsize=PT_ANNOT, color=TEXT)
        else:
            ax.text(q3 + LABEL_GAP, y, f"{med[col]:+.2f}", ha="left", va="center",
                    fontsize=PT_ANNOT, color=TEXT)

    # Zero is the datum: to its left a ranking puts the least potent candidates first. It is NOT
    # a population-versus-mean boundary, so the half-planes stay unwashed and unlabelled.
    zero_rule(ax, 0.0, vertical=True, color=SUBTLE, lw=0.8, zorder=2)

    bare_axes(ax, keep=("bottom",))
    ax.set_xlim(XLIM_LO, XLIM_HI)
    ax.set_ylim(-0.60, len(ROWS) - 0.40)
    ax.set_xticks([-0.5, 0.0, 0.5])
    ax.spines["bottom"].set_bounds(SPINE_LO, SPINE_HI)
    ax.spines["bottom"].set_color(HAIRLINE)
    ax.set_yticks(ys)
    ax.set_yticklabels([r[1] for r in ROWS])
    ax.tick_params(axis="y", length=0, labelsize=PT_ANNOT)
    ax.tick_params(axis="x", labelsize=PT_TICK)
    # "(low AUC)" is load-bearing: GDSC2 AUC runs OPPOSITE to potency, so "potency (GDSC2 AUC)"
    # inverts every sign on this axis for a reader who knows the assay.
    ax.set_xlabel(r"Spearman $\rho$ with GDSC2 potency (low AUC)", fontsize=PT_ANNOT,
                  color=TEXT, labelpad=1.5)
    title(ax, TITLE_3L)
    return ax


def _endpoint_table():
    """Both endpoints' medians, so this module's docstring can be checked against the files.

    Not drawn: see judgement call 6. Standalone only, and it raises rather than skipping if the
    functional table is absent, because a silent half-answer is worse than no answer.

    The two tables share the 103 query keys but NOT every candidate pool, so this reports the
    mismatch instead of asserting an equality that is false. See judgement call 6.
    """
    p, f = _load(SRC, "absolute-potency"), _load(FUNCTIONAL, "functional-similarity")
    keys = ["cell_line", "query_drug"]
    assert set(map(tuple, p[keys].values.tolist())) == set(map(tuple, f[keys].values.tolist())), \
        "the two Class-C tables are not the same 103 queries; they cannot be compared per row."
    lines = []
    for col, lab, _c, _f in ROWS:
        mf, mp = float(f[col].median()), float(p[col].median())
        flips = "changes sign" if mf * mp < 0 else "same sign"
        lines.append(f"  {lab:<26s} functional {mf:+.3f}  ->  potency {mp:+.3f}   {flips}")
    if "n_cand" in p.columns and "n_cand" in f.columns:
        m = p[keys + ["n_cand"]].merge(f[keys + ["n_cand"]], on=keys, suffixes=("_pot", "_fun"))
        diff = m[m.n_cand_pot != m.n_cand_fun]
        lines.append(f"  candidate pools differ for {len(diff)} of {len(m)} queries "
                     f"(the endpoint medians are near-paired, not exactly paired)")
        for _i, r in diff.iterrows():
            lines.append(f"    {r.cell_line} {r.query_drug}: potency {int(r.n_cand_pot)} "
                         f"candidates, functional {int(r.n_cand_fun)}")
    return "\n".join(lines)


if __name__ == "__main__":
    from figstyle import apply_style
    from fig3_style import PT_TITLE

    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    fig = plt.figure(figsize=(3.60, 1.02))
    # The rect this panel occupies in fig3_assemble: 1.20 in of left pad, 0.10 in right,
    # 0.38 in bottom, and the title band above the axes.
    ax = fig.add_axes([1.20 / 3.60, 0.38 / 1.02, 2.30 / 3.60, 0.64 / 1.02])
    draw_3l(ax)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "3l.png")
    fig.savefig(out, dpi=300)
    print(f"wrote {out}")
    print(_endpoint_table())
