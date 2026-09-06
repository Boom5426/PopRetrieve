#!/usr/bin/env python
"""Phase 6A: the numerical reissue ledger.

Not an experiment. It reads the two estimator arms and the manuscript source, and emits one table
that says, for every number the manuscript quotes through a LaTeX macro or a figure panel, whether
that number changed and by how much. Everything downstream of this point edits the manuscript from
this table rather than from a memory of which run produced what.

Four categories, fixed by the plan:

    A  must be updated in the main text: the value moved by more than the precision it is quoted at
    B  value moved, textual claim unchanged: substitute the number, leave the sentence
    C  interpretation must change: the number moved in a way that alters why it was reported
    D  blocked: could not be recomputed, so its status under the correct estimator is unknown

A and B are assigned mechanically from the size of the move against the quoted precision. C and D
are assigned by hand in the accompanying document, because "the explanation changed" is not a
property of a number.

Run:
    python analysis/estimator_audit/build_reissue_ledger.py \
        --comparison results/estimator_audit/arm_comparison_full.csv \
        --tex manuscript/latex/PopRetrieve_manuscript.tex \
        --out results/estimator_audit
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

MACRO = re.compile(r"\\newcommand\{\\([A-Za-z]+)\}\{([^}]*)\}")
NUMBER = re.compile(r"-?\d+\.?\d*")


def quoted_precision(text: str) -> float | None:
    """The smallest change that would be visible at the precision a macro is written to.

    A macro reading '0.205' is quoted to three decimals, so a move of 0.0005 is invisible and a
    move of 0.005 is not. A macro with no decimal point falls back to 0.5.
    """
    m = NUMBER.search(text.replace(",", ""))
    if not m:
        return None
    s = m.group(0)
    return 10 ** (-len(s.split(".")[1])) / 2 if "." in s else 0.5


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--comparison", required=True)
    ap.add_argument("--tex", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    cmp_df = pd.read_csv(a.comparison)
    tex = Path(a.tex).read_text()
    macros = {m.group(1): m.group(2) for m in MACRO.finditer(tex)}
    used = {k: len(re.findall(r"\\" + k + r"(?![A-Za-z])", tex)) for k in macros}

    # Wall-clock columns are not claims. They move because the two arms shared a machine, and
    # including them would put "the U arm was slower" in a table about scientific numbers.
    TIMING = ("runtime", "seconds", "_ms", "wall", "elapsed")
    rows = []
    for _, r in cmp_df.iterrows():
        if not np.isfinite(r.get("delta", np.nan)):
            continue
        if any(t in str(r["file"]).lower() or t in str(r["column"]).lower() for t in TIMING):
            continue
        moved = abs(r["delta"])
        rel = r.get("rel", np.nan)
        # A column is a reissue candidate when it moved at all. The category is decided against
        # three decimals, the precision the manuscript quotes almost everything at.
        if moved < 5e-4 and (not np.isfinite(rel) or abs(rel) < 0.001):
            cat = "unchanged"
        elif abs(rel) > 0.05 or (r.get("sign_flips", 0) or 0) > 0:
            cat = "A"
        else:
            cat = "B"
        rows.append({"file": r["file"], "column": r["column"], "arm_v": r["arm_v"],
                     "arm_u": r["arm_u"], "delta": r["delta"], "rel": rel,
                     "sign_flips": r.get("sign_flips", np.nan), "n": r.get("n", np.nan),
                     "category": cat})
    led = pd.DataFrame(rows)
    led.to_csv(out / "reissue_ledger.csv", index=False)

    counts = led.category.value_counts().to_dict()

    # Link each macro to the recomputed column whose V-arm value it matches. A macro is a number
    # the manuscript prints; if some column in the V arm carries that number and the U arm does
    # not, the macro has to be reissued. Matching is numeric and to the macro's own precision, so
    # a coincidental match at three decimals is possible and the table is a candidate list to be
    # checked, not an automatic edit list.
    mrows = []
    for k, v in macros.items():
        prec = quoted_precision(v)
        num = NUMBER.search(v.replace(",", "").replace("\\%", ""))
        val = float(num.group(0)) if num else None
        hit = None
        if val is not None and prec is not None:
            cand = led[np.isfinite(led.arm_v) & (np.abs(led.arm_v - val) <= prec)]
            if len(cand):
                cand = cand.reindex(cand.delta.abs().sort_values(ascending=False).index)
                hit = cand.iloc[0]
        mrows.append({
            "macro": k, "value": v, "uses_in_tex": used[k], "quoted_precision": prec,
            "matched_file": hit["file"] if hit is not None else "",
            "matched_column": hit["column"] if hit is not None else "",
            "arm_v": hit["arm_v"] if hit is not None else np.nan,
            "arm_u": hit["arm_u"] if hit is not None else np.nan,
            "category": hit["category"] if hit is not None else "no numeric match",
            "visible_at_quoted_precision": (bool(abs(hit["delta"]) > prec)
                                            if hit is not None and prec else False),
        })
    mac = pd.DataFrame(mrows)
    mac.to_csv(out / "manuscript_macros.csv", index=False)

    summary = {"columns": int(len(led)), "by_category": {k: int(v) for k, v in counts.items()},
               "macros_defined": len(macros),
               "macros_used_at_least_once": int(sum(1 for v in used.values() if v > 0)),
               "macros_matched_to_a_recomputed_column": int((mac.category != "no numeric match").sum()),
               "macros_visibly_changed": int(mac.visible_at_quoted_precision.sum())}
    (out / "reissue_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    print(led[led.category == "A"].sort_values("rel", key=lambda s: s.abs(), ascending=False)
          .head(30).to_string(index=False))


if __name__ == "__main__":
    sys.exit(main())
