#!/usr/bin/env python3
"""Recover a U-arm results file that the estimator audit produced but never installed.

WHY THIS EXISTS
---------------
`run_legacy_suite.sh` was run twice, once per estimator arm, in two separate checkouts, and
`compare_arms.py` then walked both trees and recorded EVERY numeric cell of every file under both
arms into `results/estimator_audit/arm_comparison_full.csv`. The U-arm tree itself was not kept:
the reissue installed a whitelist of files into `results/` and the rest of that tree is gone.

`analysis/class_c/class_c_magnitude_control_v2.py` is one of the files that was compared and not
installed. It cannot simply be re-run on this machine: it needs `data/processed/sciplex3_all.pt`,
which DATA.md documents as large and untracked and which is absent here. Its U-arm output is
therefore only reachable through the comparison table, which is where this script goes.

WHY THAT IS A LEGITIMATE PROVENANCE PATH, AND HOW IT IS CHECKED
---------------------------------------------------------------
The comparison table is not a summary. It holds one row per (file, row key, column) with the
value under each arm, so the U-arm file is a pivot of it and nothing is being interpolated,
averaged or inferred. What could still go wrong is a mis-keyed pivot, a column dropped in
transit, or a comparison table built against a different version of the file.

So the script does not write anything until it has rebuilt the OTHER arm and checked it against
the file on disk. If pivoting `arm_v` reproduces the installed V-arm file to floating-point
printing precision, on every row and every column, then the same pivot of `arm_u` is that file's
U-arm counterpart. If it does not, the script refuses and says which column disagreed.

Non-numeric columns are not in the comparison table. They are taken from the on-disk V file,
which is correct by construction: the two arms differ only in the estimator, so a label column is
identical between them, and the row key the comparison uses is built from those labels.

    python3 analysis/estimator_audit/recover_u_arm_output.py \\
        --file upgrade/class_c_magnitude_control_v2.csv \\
        --key-columns cell_line query_drug \\
        --out results/upgrade/class_c_magnitude_control_v2.csv
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys

import numpy as np
import pandas as pd

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
COMPARISON = os.path.join(REPO, "results", "estimator_audit", "arm_comparison_full.csv")
KEY_SEP = " | "          # the separator compare_arms.py builds its row key with
ROUNDTRIP_TOL = 1e-12    # a rebuilt V cell may differ only by CSV printing precision


def _pivot(sub: pd.DataFrame, arm: str) -> pd.DataFrame:
    wide = sub.pivot(index="row", columns="column", values=arm)
    wide.index.name = "row"
    return wide


def recover(file_key: str, key_columns: list[str], disk_path: str) -> pd.DataFrame:
    cmp_all = pd.read_csv(COMPARISON)
    sub = cmp_all[cmp_all["file"] == file_key].copy()
    if sub.empty:
        raise SystemExit(
            f"{COMPARISON} holds no rows for {file_key!r}. Known files include:\n  "
            + "\n  ".join(sorted(cmp_all['file'].unique())[:20]))
    if not bool(sub["keyed"].all()):
        raise SystemExit(
            f"{file_key} was compared POSITIONALLY, not by row key, for "
            f"{int((~sub['keyed']).sum())} of its {len(sub)} cells. A positional comparison "
            f"cannot be pivoted back into a file, because nothing ties a row to its identity.")

    disk = pd.read_csv(disk_path)
    for col in key_columns:
        if col not in disk.columns:
            raise SystemExit(f"{disk_path} has no key column {col!r}; columns are {list(disk.columns)}")
    disk = disk.assign(row=disk[key_columns].astype(str).agg(KEY_SEP.join, axis=1))
    if disk["row"].duplicated().any():
        raise SystemExit(
            f"{key_columns} do not identify a row of {disk_path}; "
            f"{int(disk['row'].duplicated().sum())} keys repeat.")

    wide_v, wide_u = _pivot(sub, "arm_v"), _pivot(sub, "arm_u")
    numeric = [c for c in disk.columns if c not in key_columns + ["row"]]
    missing = [c for c in numeric if c not in wide_v.columns]
    if missing:
        raise SystemExit(
            f"the comparison table does not cover {missing} of {disk_path}. A file cannot be "
            f"rebuilt from a partial column set; re-run compare_arms.py or the experiment itself.")
    extra = [c for c in wide_v.columns if c not in numeric]
    if extra:
        raise SystemExit(
            f"the comparison table carries columns {extra} that {disk_path} does not have, so the "
            f"two are not the same file version.")

    if set(wide_v.index) != set(disk["row"]):
        only_cmp = sorted(set(wide_v.index) - set(disk["row"]))[:5]
        only_disk = sorted(set(disk["row"]) - set(wide_v.index))[:5]
        raise SystemExit(
            f"row sets differ: {len(wide_v)} in the comparison against {len(disk)} on disk. "
            f"Only in comparison: {only_cmp}. Only on disk: {only_disk}.")

    # ---- the check that licenses the write -----------------------------------------------
    ordered_v = wide_v.reindex(disk["row"].to_numpy())[numeric].to_numpy(dtype=float)
    on_disk = disk[numeric].to_numpy(dtype=float)
    worst = float(np.nanmax(np.abs(ordered_v - on_disk)))
    if not worst <= ROUNDTRIP_TOL:
        col = numeric[int(np.nanargmax(np.nanmax(np.abs(ordered_v - on_disk), axis=0)))]
        raise SystemExit(
            f"rebuilding the V arm from the comparison table does NOT reproduce {disk_path}: "
            f"largest disagreement {worst:.3e}, worst column {col!r}, tolerance {ROUNDTRIP_TOL}. "
            f"The comparison was built against a different version of this file, so its U column "
            f"is not this file's counterpart and nothing may be written from it.")

    out = disk.copy()
    out[numeric] = wide_u.reindex(disk["row"].to_numpy())[numeric].to_numpy(dtype=float)
    moved = {c: float(np.nanmax(np.abs(out[c].to_numpy(dtype=float) - disk[c].to_numpy(dtype=float))))
             for c in numeric}
    print(f"V round-trip exact to {worst:.3e} over {len(disk)} rows x {len(numeric)} columns")
    for c, d in sorted(moved.items(), key=lambda kv: -kv[1]):
        print(f"  {c:<30s} largest |U - V| = {d:.6g}")
    return out.drop(columns=["row"])


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--file", required=True, help="the file key as it appears in arm_comparison_full.csv")
    ap.add_argument("--key-columns", nargs="+", required=True,
                    help="the columns compare_arms.py built the row key from, in order")
    ap.add_argument("--out", required=True, help="where to write the recovered U-arm file")
    ap.add_argument("--backup-dir", default=None,
                    help="if the output exists, copy it here before overwriting")
    args = ap.parse_args()

    out_path = os.path.join(REPO, args.out) if not os.path.isabs(args.out) else args.out
    recovered = recover(args.file, args.key_columns, out_path)
    if args.backup_dir:
        os.makedirs(args.backup_dir, exist_ok=True)
        shutil.copy2(out_path, os.path.join(args.backup_dir, os.path.basename(out_path)))
        print(f"backed up the existing file to {args.backup_dir}")
    recovered.to_csv(out_path, index=False)
    print(f"wrote {out_path}  ({len(recovered)} rows)")


if __name__ == "__main__":
    main()
