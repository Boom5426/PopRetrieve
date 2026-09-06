#!/usr/bin/env python
"""Phase C, gates 1 and 2 measured on the transition-retrieval task itself.

Plan section 12 asks for the manuscript's three necessary conditions to be measured on the same
queries the retrieval is run on, instead of on separate constructions. Gate 3 needs no new
computation: it is read directly off the Phase A and Phase B rankings, and is assembled in
phase_d_synthesis.py. This script computes the two that do need the cells.

GATE 1: DIFFERENTIAL RESPONSE
-----------------------------
Two cellular states are fixed in advance as the cell-cycle calls that ship with the plate, G1 and
G2M, with S dropped as intermediate. For query condition (c, q):

    r_state = mean(treated cells of (c,q) in that state) - mean(vehicle cells of c in that state)
    D       = 1 - cos(r_G1, r_G2M)

Each state's response is referred to its OWN state-matched vehicle mean. Referring both to a
pooled vehicle mean would leave the difference between the two vehicle states inside the
responses and inflate D, which is correction R30 in CORRECTIONS.md.

D is a property of the condition, not of a query draw, so it is computed from all cells of the
condition. It never enters a ranking, so using both sublibrary halves here cannot leak into
Phase A: it is a diagnostic that is joined to the rankings afterwards.

GATE 2: RECOVERABILITY
----------------------
The state partition cannot be reused here. Cell-cycle phase is itself scored from expression, so
asking a probe to recover it from expression is partly circular, which is the failure mode this
project exists to criticise and the reason the Tahoe pilot scored Gate 2 on drug identity
instead. This script keeps that choice and asks the per-query version of it:

    can a probe tell a cell that saw drug q in context c from a vehicle cell of context c?

The label is external, it is which well the cell came from, and it is exactly the quantity a
population-aware retriever depends on: if the drug's effect is not recoverable in single cells,
no distributional score can use it.

    A_sup    5-fold cross-validated linear probe (logistic regression, C=1), out-of-fold accuracy
    A_unsup  k-means with k=2 on the same cells, best-permutation accuracy
    G        A_sup - A_unsup

Both arms are balanced and capped at GATE2_CELLS_PER_ARM cells, so chance is 0.5 by construction.
Following the manuscript, label matching is free for the unsupervised arm.

OUTPUTS (--out)
---------------
    gate1_observed.csv   per (context, query drug): D and the counts behind it
    gate2_observed.csv   per (context, query drug): A_sup, A_unsup, G
    provenance.json

Run:
    python analysis/phase2_transition/phase_c_gates.py \
        --h5ad <plate3 .h5ad> --freeze-dir results/phase2_transition/eligibility \
        --out results/phase2_transition/phase_c
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp
from joblib import Parallel, delayed
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_eligibility import read_obs, sha256                       # noqa: E402
import phase2_common as pc                                           # noqa: E402

STATES = ("G1", "G2M")
MIN_STATE_CELLS = 50          # per arm of the four (treated x state, vehicle x state)
GATE2_CELLS_PER_ARM = 300     # matches analysis/tahoe_pilot/tahoe_gate_pilot.py
GATE2_SEED = 0


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def _cos(a, b) -> float:
    na, nb = float(np.linalg.norm(a)), float(np.linalg.norm(b))
    return float("nan") if na < 1e-12 or nb < 1e-12 else float(a @ b / (na * nb))


def gate2_one(Z: np.ndarray, y: np.ndarray, seed: int) -> tuple[float, float]:
    """Supervised ceiling and unsupervised accuracy on one balanced two-arm problem."""
    oof = np.empty_like(y)
    for tr, te in StratifiedKFold(5, shuffle=True, random_state=seed).split(Z, y):
        clf = LogisticRegression(max_iter=2000, C=1.0)
        clf.fit(Z[tr], y[tr])
        oof[te] = clf.predict(Z[te])
    a_sup = float((oof == y).mean())
    km = KMeans(n_clusters=2, n_init=10, random_state=seed).fit_predict(Z)
    acc = float((km == y).mean())
    return a_sup, float(max(acc, 1.0 - acc))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--h5ad", required=True)
    ap.add_argument("--freeze-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n-jobs", type=int, default=12)
    ap.add_argument("--limit-contexts", type=int, default=0)
    ap.add_argument("--no-hash", action="store_true")
    a = ap.parse_args()

    h5ad = Path(a.h5ad).resolve()
    freeze_dir, out = Path(a.freeze_dir), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    freeze = json.loads((freeze_dir / "task_freeze.json").read_text())
    if freeze["input_sha256"] and not a.no_hash:
        got = sha256(h5ad)
        if got != freeze["input_sha256"]:
            raise ValueError(f"input does not match the freeze: {got}")
    elig = pd.read_csv(freeze_dir / "query_eligibility.csv")
    ctx_tab = pd.read_csv(freeze_dir / "context_summary.csv")
    contexts = ctx_tab.loc[ctx_tab.context_usable, "cell_name"].tolist()
    if a.limit_contexts:
        contexts = contexts[:a.limit_contexts]
    queries_by_ctx = {c: g.loc[g.eligible, "drug"].tolist() for c, g in elig.groupby("cell_name")}

    import anndata as ad
    log(f"reading {h5ad}")
    adata = ad.read_h5ad(h5ad)
    X = adata.X
    if not sp.isspmatrix_csr(X):
        X = sp.csr_matrix(X)
    X = X.astype(np.float32)
    obs = read_obs(h5ad, ["cell_name", "drug", "phase"])
    del adata
    cell_name, drug, phase = obs.cell_name.to_numpy(), obs.drug.to_numpy(), obs.phase.to_numpy()
    log(f"X {X.shape}")

    g1_rows, g2_rows = [], []
    excl = {"treated_state_too_few": 0, "vehicle_state_too_few": 0}

    for ci, c in enumerate(contexts):
        in_ctx = cell_name == c
        ctrl_rows = np.flatnonzero(in_ctx & (drug == pc.CONTROL_DRUG))
        ctrl_state = {s: ctrl_rows[phase[ctrl_rows] == s] for s in STATES}
        veh_ok = all(len(ctrl_state[s]) >= MIN_STATE_CELLS for s in STATES)
        ctrl_mean_state = ({s: np.asarray(X[ctrl_state[s]].mean(0)).ravel() for s in STATES}
                           if veh_ok else None)

        qlist = queries_by_ctx[c]
        # ---- Gate 1 ----
        for q in qlist:
            r = np.flatnonzero(in_ctx & (drug == q))
            tstate = {s: r[phase[r] == s] for s in STATES}
            rec = {"cell_line": c, "drug": q,
                   "n_treated_G1": len(tstate["G1"]), "n_treated_G2M": len(tstate["G2M"]),
                   "n_vehicle_G1": len(ctrl_state["G1"]), "n_vehicle_G2M": len(ctrl_state["G2M"])}
            if not veh_ok:
                excl["vehicle_state_too_few"] += 1
                rec.update({"induced_cosine": np.nan, "D": np.nan,
                            "norm_r_G1": np.nan, "norm_r_G2M": np.nan})
            elif any(len(tstate[s]) < MIN_STATE_CELLS for s in STATES):
                excl["treated_state_too_few"] += 1
                rec.update({"induced_cosine": np.nan, "D": np.nan,
                            "norm_r_G1": np.nan, "norm_r_G2M": np.nan})
            else:
                rr = {s: np.asarray(X[tstate[s]].mean(0)).ravel() - ctrl_mean_state[s]
                      for s in STATES}
                cs = _cos(rr["G1"], rr["G2M"])
                rec.update({"induced_cosine": cs, "D": 1.0 - cs,
                            "norm_r_G1": float(np.linalg.norm(rr["G1"])),
                            "norm_r_G2M": float(np.linalg.norm(rr["G2M"]))})
            g1_rows.append(rec)

        # ---- Gate 2 ----
        rng = np.random.default_rng([GATE2_SEED, ci])
        jobs, meta = [], []
        for q in qlist:
            r = np.flatnonzero(in_ctx & (drug == q))
            n = int(min(len(r), len(ctrl_rows), GATE2_CELLS_PER_ARM))
            if n < 2:
                continue
            ia = rng.choice(r, n, replace=False)
            ib = rng.choice(ctrl_rows, n, replace=False)
            Z = np.asarray(sp.vstack([X[ia], X[ib]]).todense(), dtype=np.float64)
            y = np.r_[np.ones(n, int), np.zeros(n, int)]
            jobs.append(delayed(gate2_one)(Z, y, GATE2_SEED))
            meta.append((q, n))
        res = Parallel(n_jobs=a.n_jobs, prefer="threads")(jobs)
        for (q, n), (a_sup, a_unsup) in zip(meta, res):
            g2_rows.append({"cell_line": c, "drug": q, "n_per_arm": n,
                            "A_sup": a_sup, "A_unsup": a_unsup, "G": a_sup - a_unsup})
        log(f"context {ci + 1}/{len(contexts)} {c} done ({time.time() - t0:.0f}s)")

    g1 = pd.DataFrame(g1_rows)
    g2 = pd.DataFrame(g2_rows)
    g1.to_csv(out / "gate1_observed.csv", index=False)
    g2.to_csv(out / "gate2_observed.csv", index=False)

    prov = {
        "input_h5ad": str(h5ad), "input_sha256": freeze["input_sha256"],
        "n_contexts": len(contexts),
        "constants": {"STATES": list(STATES), "MIN_STATE_CELLS": MIN_STATE_CELLS,
                      "GATE2_CELLS_PER_ARM": GATE2_CELLS_PER_ARM, "GATE2_SEED": GATE2_SEED},
        "gate1_rows": int(len(g1)), "gate1_scored": int(g1.D.notna().sum()),
        "gate1_exclusions": excl,
        "gate2_rows": int(len(g2)),
        "gate2_label": "treated(q,c) vs vehicle(c); external, not expression-derived",
        "runtime_seconds": round(time.time() - t0, 1),
    }
    (out / "provenance.json").write_text(json.dumps(prov, indent=2) + "\n")
    log(f"Gate 1 scored {g1.D.notna().sum()}/{len(g1)}; median D = {g1.D.median():.4f}")
    log(f"Gate 2 A_sup median {g2.A_sup.median():.4f} | A_unsup median {g2.A_unsup.median():.4f}")
    log(f"wrote {out}  ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    sys.exit(main())
