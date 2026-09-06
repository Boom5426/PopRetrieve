#!/usr/bin/env python
"""Phase A: the oracle response-bank ceiling for transition-to-intervention retrieval.

WHAT QUESTION THIS ANSWERS
--------------------------
    With perfect candidate outcomes, does population information improve intervention selection?

Every candidate's response in the held-out context is taken from the observed data instead of
from a forward model. That removes the forward model from the loop, so whatever difference
remains between the mean route and the population route is an upper bound on what any predictor
could deliver. It is an information ceiling and it is NOT a deployable result: the deployed
setting never has observed candidate responses in the target context, which is what Phase B
removes.

THE TASK, UNCHANGED FROM THE FREEZE
-----------------------------------
For a held-out context c and a query drug q the retriever sees the vehicle cells of c and the
observed treated population X_{q,c}, and ranks all 92 candidates. It never sees q. See
docs/phase2/01_TRANSITION_TASK_FREEZE.md.

    mu_source = mean(X_source)
    P_target  = { x_i^target - mu_source }        drawn from sublibrary half H1
    P_d       = { x_i^{d,c}  - mu_source }        drawn from sublibrary half H2, observed

    mean route        s_d = cos( mean(P_target), mean(P_d) )
    population route  s_d = -Energy( P_target, P_d )                        (primary)
                      s_d = -MMD^2, -SlicedWasserstein                      (secondary)
                      s_d = -||mean(P_target) - mean(P_d)||                 (diagnostic)

WHAT IS PRE-SPECIFIED HERE, AND WHY
-----------------------------------
The freeze fixes the pools, the seeds, the source draw and the target draw. Three choices the
plan leaves open are fixed here, before any number was computed:

1.  Every candidate's oracle bank is drawn from the SAME sublibrary half H2, and the target from
    H1. The plan requires cell-disjointness only for the generating drug, which would leave that
    one candidate drawn from a different library-prep half than its 91 competitors. If sublibrary
    carries any technical shift, that asymmetry would penalise the ground truth by construction.
    Drawing every bank from H2 costs half of each pool and buys a comparison in which the
    ground-truth candidate is treated exactly like every distractor.

2.  N_BANK = 100 cells per candidate, without replacement, and all available cells when a
    candidate has fewer. Sampling with replacement to force a constant size would put duplicate
    cells in the bank, which inflates the energy distance of exactly the small-n candidates; the
    U-statistic estimators are unbiased in n, so unequal n costs variance rather than bias.

3.  The energy distance and MMD are reported in the U-statistic form, which is unbiased at any
    sample size, with the manuscript's V-statistic carried alongside rather than replaced.

Nothing here is selected on an outcome: no thresholding, no drug or context dropped, and the
library is all 92 compounds for every query.

OUTPUTS (--out)
---------------
    per_query.csv.gz        one row per (context, query drug, seed, scorer)
    summary.csv             per scorer: MRR, Hit@1/5/10 with a context-clustered bootstrap
    delta_vs_reference.csv  paired differences against the mean route and against mean_l2
    provenance.json         inputs, hashes, constants, seeds, runtime

Run:
    python analysis/phase2_transition/phase_a_oracle.py \
        --h5ad <plate3 .h5ad> \
        --freeze-dir results/phase2_transition/eligibility \
        --out results/phase2_transition/phase_a
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_eligibility import read_obs, sha256                       # noqa: E402
import phase2_common as pc                                           # noqa: E402


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--h5ad", required=True)
    ap.add_argument("--freeze-dir", required=True,
                    help="output of audit_eligibility.py; the pools are READ, not recomputed")
    ap.add_argument("--out", required=True)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--limit-contexts", type=int, default=0,
                    help="debug only: first N contexts. Never use for a reported result.")
    ap.add_argument("--no-hash", action="store_true")
    a = ap.parse_args()

    import torch

    h5ad = Path(a.h5ad).resolve()
    freeze_dir, out = Path(a.freeze_dir), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    dev = torch.device(a.device if (torch.cuda.is_available() or a.device == "cpu") else "cpu")
    t0 = time.time()

    freeze = json.loads((freeze_dir / "task_freeze.json").read_text())
    if freeze["input_sha256"] and not a.no_hash:
        got = sha256(h5ad)
        if got != freeze["input_sha256"]:
            raise ValueError(f"input does not match the freeze: {got} != {freeze['input_sha256']}")
    elig = pd.read_csv(freeze_dir / "query_eligibility.csv")
    ctx_tab = pd.read_csv(freeze_dir / "context_summary.csv")
    candidates = pd.read_csv(freeze_dir / "candidate_library.csv")["drug"].tolist()
    contexts = ctx_tab.loc[ctx_tab.context_usable, "cell_name"].tolist()
    if a.limit_contexts:
        contexts = contexts[:a.limit_contexts]
    queries_by_ctx = {c: g.loc[g.eligible, "drug"].tolist() for c, g in elig.groupby("cell_name")}
    log(f"{len(contexts)} contexts, {len(candidates)} candidates, "
        f"{sum(len(queries_by_ctx[c]) for c in contexts)} eligible queries, device={dev}")

    import anndata as ad
    log(f"reading {h5ad}")
    adata = ad.read_h5ad(h5ad)
    X = adata.X
    if not sp.isspmatrix_csr(X):
        X = sp.csr_matrix(X)
    X = X.astype(np.float32)
    obs = read_obs(h5ad, ["cell_name", "drug", "sublibrary"])
    del adata
    log(f"X {X.shape} nnz={X.nnz:,}")

    sublibs = np.sort(pd.unique(obs.sublibrary))
    sub_code = pd.Categorical(obs.sublibrary, categories=sublibs).codes
    cell_name, drug = obs.cell_name.to_numpy(), obs.drug.to_numpy()
    gt_index = {d: i for i, d in enumerate(candidates)}

    rows: list[dict] = []
    n_bank_small = n_bank_total = n_bank_fallback = 0

    for ci, c in enumerate(contexts):
        in_ctx = cell_name == c
        ctrl_rows = np.flatnonzero(in_ctx & (drug == pc.CONTROL_DRUG))
        cand_rows = {d: np.flatnonzero(in_ctx & (drug == d)) for d in candidates}
        qlist = queries_by_ctx[c]

        for seed in pc.SEEDS:
            h1 = pc.sublibrary_halves(len(sublibs), seed, ci)

            r_src = pc.rng_for(pc.RNG_SOURCE, seed, ci)
            src = r_src.choice(ctrl_rows, min(pc.N_SOURCE, len(ctrl_rows)), replace=False)
            mu = np.asarray(X[src].mean(0), dtype=np.float32).ravel()

            r_bank = pc.rng_for(pc.RNG_BANK, seed, ci)
            bank_rows, sizes = [], []
            for d in candidates:
                r = cand_rows[d]
                r2 = r[~h1[sub_code[r]]]
                if len(r2) < 2:
                    # Fewer than two cells in the bank half cannot be scored, and dropping the
                    # candidate would shrink the library, which the freeze forbids. Falls back to
                    # both halves. Only reachable for candidates with a handful of cells in total,
                    # never for the query drug, which needs at least 100. Counted in provenance.
                    r2 = r
                    n_bank_fallback += 1
                take = min(pc.N_BANK, len(r2))
                bank_rows.append(r_bank.choice(r2, take, replace=False))
                sizes.append(take)
                n_bank_total += 1
                n_bank_small += int(take < pc.N_BANK)
            B = np.asarray(X[np.concatenate(bank_rows)].todense(), dtype=np.float32) - mu
            cache = pc.make_cache(B, sizes, ci, seed, torch, dev)

            for qi, q in enumerate(qlist):
                r = cand_rows[q]
                r1 = r[h1[sub_code[r]]]
                take = min(pc.N_TARGET, len(r1))
                if take < 2:
                    continue
                r_t = pc.rng_for(pc.RNG_TARGET, seed, ci, gt_index[q])
                tidx = r_t.choice(r1, take, replace=False)
                T = np.asarray(X[tidx].todense(), dtype=np.float32) - mu
                sc = pc.score_all(torch.as_tensor(T, device=dev), cache, torch)
                gi = gt_index[q]
                for name, s in sc.items():
                    rk, tied = pc.rank_of(s, gi)
                    # Top-1 identity is needed for Flip@1 in plan section 12. argmax resolves a
                    # tie to the first candidate in library order; ties are counted in n_ties so
                    # such a case is visible rather than silently decided.
                    rows.append({
                        "cell_line": c, "drug": q, "seed": seed, "scorer": name,
                        "rank": rk, "reciprocal_rank": 1.0 / rk,
                        "hit@1": float(rk <= 1), "hit@5": float(rk <= 5), "hit@10": float(rk <= 10),
                        "n_ties": tied, "n_target_cells": take,
                        "top1_drug": candidates[int(np.argmax(s))],
                        "n_bank_cells_gt": sizes[gi], "n_bank_min": int(min(sizes)),
                        "n_source_cells": len(src), "n_candidates": len(candidates),
                    })
        log(f"context {ci + 1}/{len(contexts)} {c} done ({time.time() - t0:.0f}s)")

    per_query = pd.DataFrame(rows)
    per_query.to_csv(out / "per_query.csv.gz", index=False)   # 10 MB raw, 0.7 MB gzipped
    summary = pc.summarize(per_query, ["scorer"])
    summary.to_csv(out / "summary.csv", index=False)
    pc.paired_deltas(per_query, []).to_csv(out / "delta_vs_reference.csv", index=False)

    prov = {
        "input_h5ad": str(h5ad), "input_sha256": freeze["input_sha256"],
        "freeze_dir": str(freeze_dir), "device": str(dev),
        "n_contexts": len(contexts), "n_candidates": len(candidates),
        "n_eligible_queries": int(sum(len(queries_by_ctx[c]) for c in contexts)),
        "constants": {"N_SOURCE": pc.N_SOURCE, "N_TARGET": pc.N_TARGET, "N_BANK": pc.N_BANK,
                      "SW_N_PROJ": pc.SW_N_PROJ, "SW_N_QUANTILE": pc.SW_N_QUANTILE,
                      "N_BOOTSTRAP": pc.N_BOOTSTRAP},
        "seeds": list(pc.SEEDS),
        "bank_slots": n_bank_total, "bank_slots_below_N_BANK": n_bank_small,
        "bank_slots_falling_back_to_both_halves": n_bank_fallback,
        "oracle_disclaimer": "oracle information ceiling, not deployment evaluation",
        "runtime_seconds": round(time.time() - t0, 1),
    }
    (out / "provenance.json").write_text(json.dumps(prov, indent=2) + "\n")
    log(summary.to_string(index=False))
    log(f"wrote {out}  ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    sys.exit(main())
