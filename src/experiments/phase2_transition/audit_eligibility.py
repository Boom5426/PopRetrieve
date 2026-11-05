#!/usr/bin/env python
"""Data eligibility audit for transition-to-intervention retrieval on Tahoe-100M plate 3.

WHAT THIS IS
------------
An audit of the data, run before any model is fitted, any retrieval is run or any metric is
computed. It fixes the candidate pool and the query pool so that every later phase runs against
the same pool.

The task the pool must serve:

    given a held-out cellular context's untreated controls X_source, a desired treated target
    population X_target, and a fixed candidate drug library D, rank the candidates by how well
    each is predicted to carry X_source to X_target.

WHAT IS AUDITED, AND WHY EACH THRESHOLD IS WHERE IT IS
------------------------------------------------------
MIN_TREATED_CELLS = 100
    A query condition is eligible if it has at least 100 treated cells. Conditions below it are
    excluded as queries. A drug is never removed from the candidate library, for a cell-count
    reason or any other, because the library is what the ranking is over.

MIN_CONTROL_CELLS = 200
    The source draw is at most 200 control cells. Setting the floor equal to the source draw
    makes the source population a genuine 200-cell sample rather than a resample of a smaller
    pool. The audit also reports the count at a 100-cell floor, which shows how sensitive the
    pool is to this choice.

N_SOURCE = N_TARGET = 200, SEEDS = (13, 29, 47, 71, 101)
    Recorded in task_freeze.json so that the later phases draw the same cells.

Two further columns are audited:

  oracle_splittable     The query half and the oracle response-bank half of the generating
                        drug's cells must be cell-disjoint. A condition can give
                        a full-size 200-cell query and a full-size 200-cell oracle bank only if it
                        has at least 400 cells; below that both halves shrink. The audit reports
                        the count at 400 so Phase A knows how many queries run at full size.

  n_samples             A batch-disjoint split is preferred over a random split-half
  n_sublibraries        when a replicate label exists. Tahoe plate 3 carries two candidate
                        labels, `sample` and `sublibrary`, and they are not interchangeable, so
                        the audit measures the structure of both rather than assuming either is a
                        replicate. `sample` is a drug well: it is nested inside the drug axis, so
                        splitting on it cannot separate two halves of one condition. `sublibrary`
                        is a library-preparation pool that every condition is spread across, so
                        splitting on it does separate one condition into two halves that share no
                        library prep. The audit reports both counts and the per-condition cell
                        occupancy of a sublibrary, which is what decides whether a
                        sublibrary-disjoint split leaves usable halves.

WHAT THIS DELIBERATELY DOES NOT DO
----------------------------------
It does not read the expression matrix. Every quantity here is a count, so the audit runs off the
`obs` table alone and cannot be influenced by any expression-derived statistic. It does not choose
drugs, cell lines or thresholds by looking at a downstream result.

Run:
    python src/experiments/phase2_transition/audit_eligibility.py \
        --h5ad /path/to/plate3_..._preprocessed_cpu.h5ad \
        --out results/phase2_transition/eligibility
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

# ---- constants (see module docstring for the reason for each) ----
CONTROL_DRUG = "DMSO_TF"
MIN_TREATED_CELLS = 100
MIN_CONTROL_CELLS = 200
MIN_CONTROL_CELLS_SENSITIVITY = 100   # reported alongside, never used to select
N_SOURCE = 200
N_TARGET = 200
SEEDS = (13, 29, 47, 71, 101)
FULL_ORACLE_CELLS = N_TARGET * 2       # cell-disjoint query + oracle bank

OBS_COLUMNS = ["cell_line", "cell_name", "drug", "drugname_drugconc",
               "sample", "sublibrary", "plate", "phase"]


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def read_obs(h5ad_path: Path, columns: list[str]) -> pd.DataFrame:
    """Read named obs columns out of an .h5ad without touching X.

    AnnData stores a categorical column as a group of (categories, codes) and a plain column as a
    dataset. Both forms are handled explicitly; anything else raises rather than being coerced,
    so a schema change surfaces as an error instead of as a silently wrong count.
    """
    import h5py

    out: dict[str, np.ndarray] = {}
    with h5py.File(h5ad_path, "r") as f:
        obs = f["obs"]
        for col in columns:
            if col not in obs:
                raise KeyError(f"{h5ad_path.name} has no obs column {col!r}; "
                               f"available: {sorted(obs.keys())}")
            node = obs[col]
            if isinstance(node, h5py.Group):
                cats = node["categories"][:]
                codes = node["codes"][:]
                cats = np.asarray([c.decode() if isinstance(c, bytes) else str(c) for c in cats])
                if (codes < 0).any():
                    raise ValueError(f"obs[{col!r}] carries unmapped codes; refusing to guess")
                out[col] = cats[codes]
            else:
                vals = node[:]
                out[col] = np.asarray([v.decode() if isinstance(v, bytes) else v for v in vals])
    return pd.DataFrame(out)


def sha256(path: Path, chunk: int = 1 << 22) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            b = fh.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--h5ad", required=True, help="Tahoe plate 3 preprocessed .h5ad")
    ap.add_argument("--out", required=True, help="output directory for the audit tables")
    ap.add_argument("--no-hash", action="store_true",
                    help="skip the sha256 of the input file (provenance is then incomplete)")
    a = ap.parse_args()

    h5ad = Path(a.h5ad).resolve()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    if not h5ad.exists():
        raise FileNotFoundError(h5ad)

    log(f"reading obs from {h5ad}")
    obs = read_obs(h5ad, OBS_COLUMNS)
    log(f"obs {obs.shape}")

    # ---- integrity checks on the axes the task is defined over ----
    plates = sorted(obs.plate.unique())
    if len(plates) != 1:
        raise ValueError(f"expected a single plate, found {plates}")
    line_map = obs.groupby("cell_name", observed=True).cell_line.nunique()
    if (line_map != 1).any():
        raise ValueError("cell_name does not map 1:1 onto cell_line; the context axis is ambiguous")
    conc = obs.groupby("drug", observed=True).drugname_drugconc.nunique()
    multi_dose = conc[conc > 1]

    lines = sorted(obs.cell_name.unique())
    all_drugs = sorted(obs.drug.unique())
    if CONTROL_DRUG not in all_drugs:
        raise ValueError(f"control arm {CONTROL_DRUG!r} absent; found {all_drugs[:5]} ...")
    candidates = [d for d in all_drugs if d != CONTROL_DRUG]
    log(f"{len(lines)} cell lines, {len(all_drugs)} drug labels "
        f"= {len(candidates)} candidates + control {CONTROL_DRUG!r}")

    # ---- per (cell line, drug) counts ----
    g = obs.groupby(["cell_name", "drug"], observed=True)
    cond = g.agg(n_cells=("drug", "size"),
                 n_samples=("sample", "nunique"),
                 n_sublibraries=("sublibrary", "nunique")).reset_index()
    phase_counts = (obs.groupby(["cell_name", "drug", "phase"], observed=True)
                       .size().unstack(fill_value=0).reset_index())
    phase_cols = [c for c in phase_counts.columns if c not in ("cell_name", "drug")]
    phase_counts = phase_counts.rename(columns={c: f"n_{c}" for c in phase_cols})
    cond = cond.merge(phase_counts, on=["cell_name", "drug"], how="left")
    cond["is_control"] = cond.drug == CONTROL_DRUG

    # ---- control availability per context ----
    ctrl = (cond[cond.is_control][["cell_name", "n_cells", "n_samples"]]
            .rename(columns={"n_cells": "n_control_cells", "n_samples": "n_control_samples"}))
    missing_ctrl = sorted(set(lines) - set(ctrl.cell_name))
    ctrl = ctrl.set_index("cell_name").reindex(lines).fillna(0).astype(int).reset_index()
    ctrl.columns = ["cell_name", "n_control_cells", "n_control_samples"]

    # ---- eligibility of every (context, candidate) pair, present or absent ----
    grid = pd.MultiIndex.from_product([lines, candidates],
                                      names=["cell_name", "drug"]).to_frame(index=False)
    q = grid.merge(cond[cond.is_control == False], on=["cell_name", "drug"], how="left")
    q["n_cells"] = q.n_cells.fillna(0).astype(int)
    q["n_samples"] = q.n_samples.fillna(0).astype(int)
    q["n_sublibraries"] = q.n_sublibraries.fillna(0).astype(int)
    q = q.merge(ctrl, on="cell_name", how="left")

    # Exclusion reasons are evaluated in a fixed order and only the first one is recorded, so the
    # counts in exclusions.csv partition the excluded conditions exactly once each.
    reason = np.full(len(q), "", dtype=object)
    reason = np.where((reason == "") & (q.n_cells.to_numpy() == 0), "condition_absent", reason)
    reason = np.where((reason == "") & (q.n_control_cells.to_numpy() < MIN_CONTROL_CELLS),
                      "context_control_too_few", reason)
    reason = np.where((reason == "") & (q.n_cells.to_numpy() < MIN_TREATED_CELLS),
                      "treated_too_few", reason)
    q["exclusion_reason"] = reason
    q["eligible"] = q.exclusion_reason == ""
    q["full_size_query"] = q.eligible & (q.n_cells >= N_TARGET)
    q["oracle_splittable_full"] = q.eligible & (q.n_cells >= FULL_ORACLE_CELLS)
    q["sample_disjoint_possible"] = q.eligible & (q.n_samples >= 2)
    q["sublibrary_disjoint_possible"] = q.eligible & (q.n_sublibraries >= 2)

    # ---- per-context summary ----
    ctx = (q.groupby("cell_name")
             .agg(n_candidates_present=("n_cells", lambda s: int((s > 0).sum())),
                  n_eligible=("eligible", "sum"),
                  n_full_size=("full_size_query", "sum"),
                  n_oracle_full=("oracle_splittable_full", "sum"),
                  median_treated_cells=("n_cells", "median"),
                  min_treated_cells=("n_cells", "min"))
             .reset_index()
             .merge(ctrl, on="cell_name", how="left"))
    ctx["context_usable"] = ctx.n_control_cells >= MIN_CONTROL_CELLS

    # ---- structure of the two candidate replicate labels ----
    smp = obs.groupby("sample", observed=True).agg(n_drugs=("drug", "nunique"),
                                                   n_lines=("cell_name", "nunique"))
    sub_occ = obs.groupby(["cell_name", "drug", "sublibrary"], observed=True).size()

    excl = (q[~q.eligible].groupby("exclusion_reason").size()
              .rename("n_conditions").reset_index()
              .sort_values("n_conditions", ascending=False))

    # ---- sensitivity of the control-cell floor ----
    ctrl_at_100 = int((ctrl.n_control_cells >= MIN_CONTROL_CELLS_SENSITIVITY).sum())
    ctrl_at_200 = int((ctrl.n_control_cells >= MIN_CONTROL_CELLS).sum())
    elig_at_100 = int(((q.n_cells >= MIN_TREATED_CELLS)
                       & (q.n_control_cells >= MIN_CONTROL_CELLS_SENSITIVITY)).sum())

    # ---- write ----
    cond.to_csv(out / "condition_counts.csv", index=False)
    q.to_csv(out / "query_eligibility.csv", index=False)
    ctx.to_csv(out / "context_summary.csv", index=False)
    excl.to_csv(out / "exclusions.csv", index=False)
    pd.DataFrame({"drug": candidates}).to_csv(out / "candidate_library.csv", index=False)

    freeze = {
        "input_h5ad": str(h5ad),
        "input_bytes": h5ad.stat().st_size,
        "input_sha256": None if a.no_hash else sha256(h5ad),
        "n_cells_total": int(len(obs)),
        "plate": plates[0],
        "control_drug": CONTROL_DRUG,
        "n_cell_lines": len(lines),
        "n_drug_labels": len(all_drugs),
        "n_candidates": len(candidates),
        "drugs_with_multiple_concentrations": {k: int(v) for k, v in multi_dose.items()},
        "cell_lines_missing_control_arm": missing_ctrl,
        "thresholds": {
            "MIN_TREATED_CELLS": MIN_TREATED_CELLS,
            "MIN_CONTROL_CELLS": MIN_CONTROL_CELLS,
            "N_SOURCE": N_SOURCE,
            "N_TARGET": N_TARGET,
            "FULL_ORACLE_CELLS": FULL_ORACLE_CELLS,
        },
        "seeds": list(SEEDS),
        "counts": {
            "grid_conditions": int(len(q)),
            "conditions_present": int((q.n_cells > 0).sum()),
            "eligible_queries": int(q.eligible.sum()),
            "eligible_full_size": int(q.full_size_query.sum()),
            "eligible_oracle_full": int(q.oracle_splittable_full.sum()),
            "eligible_sample_disjoint": int(q.sample_disjoint_possible.sum()),
            "eligible_sublibrary_disjoint": int(q.sublibrary_disjoint_possible.sum()),
            "contexts_usable": int(ctx.context_usable.sum()),
        },
        "replicate_label_structure": {
            "n_samples": int(obs["sample"].nunique()),
            "drugs_per_sample_max": int(smp.n_drugs.max()),
            "lines_per_sample_max": int(smp.n_lines.max()),
            "sample_is_nested_in_drug": bool(smp.n_drugs.max() == 1),
            "n_sublibraries": int(obs.sublibrary.nunique()),
            "sublibraries_per_condition_median": float(cond.n_sublibraries.median()),
            "sublibraries_per_condition_min": int(cond.n_sublibraries.min()),
            "cells_per_condition_sublibrary_median": float(sub_occ.median()),
        },
        "sensitivity_of_the_control_floor": {
            "contexts_with_control_ge_100": ctrl_at_100,
            "contexts_with_control_ge_200": ctrl_at_200,
            "eligible_queries_if_control_floor_were_100": elig_at_100,
        },
        "exclusions": {r.exclusion_reason: int(r.n_conditions) for r in excl.itertuples()},
    }
    (out / "task_freeze.json").write_text(json.dumps(freeze, indent=2, sort_keys=False) + "\n")

    log(json.dumps(freeze["counts"], indent=2))
    log(f"wrote {out}")


if __name__ == "__main__":
    sys.exit(main())
