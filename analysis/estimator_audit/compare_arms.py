#!/usr/bin/env python
"""Phase 2 (P0-A): diff the two estimator arms and build the old-vs-new table.

Two complete runs of every result that depends on a population scorer exist, identical in code,
data and seeds and differing only in POPRETRIEVE_ESTIMATOR. This walks both results trees and
reports, per file and per numeric column, what moved.

Three things are reported for every column, because they answer different questions:

    delta        the change in the column mean. Says how far a number moved.
    rel          that change relative to the V-arm mean. Says whether it matters at that scale.
    sign_flips   how many individual cells changed sign. A mean that barely moves while a third of
                 its rows change sign is a different situation from one that moves a lot uniformly,
                 and only the second is safe to describe as a shift.

A file that exists in one arm and not the other is reported as such rather than skipped: an
experiment that failed in one arm must not vanish from the audit.

Run, after both arms have finished:
    python analysis/estimator_audit/compare_arms.py --arm-v <dir> --arm-u <dir> \
        --out results/estimator_audit
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

# Files whose numbers appear in the manuscript, with the columns that carry the claim. Anything not
# listed is still diffed generically; this list only controls what the headline table shows.
HEADLINE = {
    "exp01_sciplex3_controlled/metrics_summary.csv": None,
    "exp03_crossline_semireal/summary.csv": None,
    "exp05_frangieh_natural/summary.csv": None,
    "exp06_theory_limits/degenerate_limit_synthetic.csv": None,
    "exp08_signature_baselines/summary.csv": None,
    "exp08_signature_baselines/summary_by_task.csv": None,
    "exp09_predict_then_rank/summary.csv": None,
    "exp09_structure_diagnostics/exp09_structure_diagnostics_summary.csv": None,
    "exp11_hir_benchmark/theoretical_boundary.csv": None,
    "exp12_partial_observed_retrieval/summary.csv": None,
    "exp13_real_data_projection/projection.csv": None,
    "exp16_gate_diagnosis/gate_vs_true_divergence.csv": None,
    "exp17_true_divergence_subset/divergence_stratified.csv": None,
}


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def _key_columns(a: pd.DataFrame, b: pd.DataFrame) -> list[str]:
    """Non-numeric columns that uniquely identify a row in BOTH frames.

    A summary table like recommendation_vs_outcome.csv has one row per (recommendation mode,
    scorer). Averaging a column down that table mixes scorers whose numbers move in opposite
    directions and reports the average as if it were a claim, which is how a real 0.176 -> 0.195
    improvement and a real 0.268 -> 0.135 collapse became a single misleading "0.118 -> 0.035".
    Comparing row by row is the only version of this table that means anything.
    """
    cand = [c for c in a.columns
            if c in b.columns and not pd.api.types.is_numeric_dtype(a[c])]
    if not cand:
        return []
    for k in range(1, min(len(cand), 4) + 1):
        for i in range(len(cand) - k + 1):
            sel = cand[i:i + k]
            if (not a.duplicated(sel).any() and not b.duplicated(sel).any()
                    and set(map(tuple, a[sel].astype(str).to_numpy()))
                    == set(map(tuple, b[sel].astype(str).to_numpy()))):
                return sel
    return []


def compare_frames(a: pd.DataFrame, b: pd.DataFrame, rel: str) -> list[dict]:
    """Row-keyed where the file has identifying columns, column-wise otherwise."""
    rows = []
    num = [c for c in a.columns
           if c in b.columns and pd.api.types.is_numeric_dtype(a[c])
           and pd.api.types.is_numeric_dtype(b[c])
           and not pd.api.types.is_bool_dtype(a[c]) and not pd.api.types.is_bool_dtype(b[c])]
    if not num:
        return rows
    key = _key_columns(a, b)

    if key:
        m = a[key + num].merge(b[key + num], on=key, suffixes=("_v", "_u"))
        for _, r in m.iterrows():
            label = " | ".join(str(r[k]) for k in key)
            for c in num:
                try:
                    x, y = float(r[f"{c}_v"]), float(r[f"{c}_u"])
                except (TypeError, ValueError):
                    continue
                if not (np.isfinite(x) and np.isfinite(y)):
                    continue
                d = y - x
                rows.append({
                    "file": rel, "row": label, "column": c, "arm_v": float(x), "arm_u": float(y),
                    "delta": d, "rel": (d / abs(x)) if abs(x) > 1e-12 else np.nan,
                    "max_abs_cell_delta": abs(d),
                    "sign_flips": int(np.sign(x) != np.sign(y)), "n": 1, "keyed": True,
                })
        return rows

    if len(a) != len(b):
        return [{"file": rel, "row": "", "column": "<row count>", "arm_v": len(a), "arm_u": len(b),
                 "delta": len(b) - len(a), "rel": np.nan, "sign_flips": np.nan, "n": np.nan,
                 "keyed": False, "note": "row counts differ and no key column; not compared"}]
    for c in num:
        x, y = a[c].to_numpy(dtype=float), b[c].to_numpy(dtype=float)
        ok = np.isfinite(x) & np.isfinite(y)
        if not ok.any():
            continue
        mv, mu = float(np.mean(x[ok])), float(np.mean(y[ok]))
        d = mu - mv
        rows.append({
            "file": rel, "row": "<column mean>", "column": c, "arm_v": mv, "arm_u": mu, "delta": d,
            "rel": (d / abs(mv)) if abs(mv) > 1e-12 else np.nan,
            "max_abs_cell_delta": float(np.max(np.abs(y[ok] - x[ok]))),
            "sign_flips": int(np.sum(np.sign(x[ok]) != np.sign(y[ok]))),
            "n": int(ok.sum()), "keyed": False,
        })
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arm-v", required=True)
    ap.add_argument("--arm-u", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    av, au, out = Path(a.arm_v), Path(a.arm_u), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    rows, missing = [], []
    for pv in sorted(av.rglob("*.csv")):
        rel = str(pv.relative_to(av))
        if rel.startswith("_") or "per_query_scores" in rel and pv.stat().st_size > 5e8:
            continue
        pu = au / rel
        if not pu.exists():
            missing.append({"file": rel, "present_in": "v only"})
            continue
        try:
            dv, du = pd.read_csv(pv), pd.read_csv(pu)
        except Exception as exc:                       # noqa: BLE001
            missing.append({"file": rel, "present_in": f"unreadable: {exc}"[:120]})
            continue
        rows += compare_frames(dv, du, rel)
    for pu in sorted(au.rglob("*.csv")):
        rel = str(pu.relative_to(au))
        if not (av / rel).exists() and not rel.startswith("_"):
            missing.append({"file": rel, "present_in": "u only"})

    df = pd.DataFrame(rows)
    df.to_csv(out / "arm_comparison_full.csv", index=False)
    pd.DataFrame(missing).to_csv(out / "arm_comparison_missing.csv", index=False)

    head = df[df.file.isin(HEADLINE)].copy() if len(df) else df
    if len(df):
        summary_keyed = int(df.get("keyed", pd.Series(dtype=bool)).sum())
    head.to_csv(out / "arm_comparison_headline.csv", index=False)

    moved = df[(df.rel.abs() > 0.01) | (df.sign_flips > 0)] if len(df) else df
    moved.sort_values("rel", key=lambda s: s.abs(), ascending=False).to_csv(
        out / "arm_comparison_moved.csv", index=False)

    summary = {
        "files_compared": int(df.file.nunique()) if len(df) else 0,
        "columns_compared": int(len(df)),
        "columns_moved_more_than_1pct": int((df.rel.abs() > 0.01).sum()) if len(df) else 0,
        "columns_with_any_sign_flip": int((df.sign_flips > 0).sum()) if len(df) else 0,
        "files_missing_from_one_arm": len(missing),
        "rows_compared_row_keyed": int(df.keyed.sum()) if "keyed" in df else 0,
    }
    (out / "arm_comparison_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    log(json.dumps(summary, indent=2))
    log(f"wrote {out}")


if __name__ == "__main__":
    sys.exit(main())
