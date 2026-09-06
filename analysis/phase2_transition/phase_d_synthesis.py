#!/usr/bin/env python
"""Phase C gate 3, the three-gate joint analysis, and the oracle-to-prediction decomposition.

This script computes nothing from cells. It reads the rankings that Phase A and Phase B already
produced and the two gate tables Phase C measured, and assembles plan sections 12 (gate 3), 13
(the joint analysis) and 14 (the decomposition). Keeping it separate from the runners means the
synthesis can be re-derived without re-running anything on the GPU, and that no analysis choice
here can reach back into how a ranking was produced.

GATE 3: DECISION RELEVANCE, READ OFF THE RETRIEVAL ITSELF
---------------------------------------------------------
Plan section 12 asks for decision relevance to stop being a state-ordering correlation and become
the retrieval outcome. Per (context, query drug, seed), holding the predictor fixed:

    delta_rank          rank under the mean route minus rank under the population route,
                        so positive means population information moved the true drug forward
    Flip@1              the two routes name a different top-1 candidate
    CorrectedFlip@1     the population route's top-1 is the true drug and the mean route's is not
    ReverseFlip@1       the reverse, reported because a flip rate without it is not interpretable

THE JOINT ANALYSIS
------------------
Plan section 13 refuses to accept three gates measured separately. Each query is placed in a
2 x 2 grid of pre-specified quartiles: differential response D on one axis, supervised
recoverability A_sup on the other, with the bottom and top quartiles forming the corners. The
prediction under test is that any population benefit concentrates in the high-D, high-A_sup cell.
Quartiles are computed on the pooled query set and fixed before any outcome is read; no threshold
is searched.

THE DECOMPOSITION
-----------------
Plan section 14 asks where population information is lost. Phase A and Phase B are paired query
by query, so for each query both dMRR_oracle and dMRR_predicted exist and the four cases can be
counted rather than argued:

    I    no oracle gain, no predicted gain     decision relevance is the limit
    II   oracle gain, no predicted gain        the forward predictor is the limit
    III  gain in both                          a real population-aware regime
    IV   no oracle gain but a predicted gain   suspect; noise or a ranking artefact

OUTPUTS (--out)
---------------
    gate3_decision_relevance.csv   per (phase, predictor): delta_rank, flips, with bootstrap CIs
    gate1_fidelity.csv             observed vs predicted differential response, per predictor
    three_gate_grid.csv            the section 13 grid
    oracle_to_prediction.csv       the section 14 case counts, per predictor
    per_query_joined.csv.gz        one row per query with every gate and every outcome on it
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import phase2_common as pc                                           # noqa: E402

POP_SCORER = "energy"          # the plan's primary population route
MEAN_SCORER = "mean_cosine"    # the plan's mean route
MAG_SCORER = "mean_l2"         # the magnitude-aware mean diagnostic
KEY = ["cell_line", "drug", "seed"]


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def route_pair(pq: pd.DataFrame, pop: str, ref: str, extra: list[str]) -> pd.DataFrame:
    """Join one scorer's rankings to another's on identical queries."""
    keys = KEY + extra
    a = pq[pq.scorer == pop].set_index(keys)
    b = pq[pq.scorer == ref].set_index(keys)
    j = a.join(b, rsuffix="_ref", how="inner").reset_index()
    j["delta_rank"] = j["rank_ref"] - j["rank"]
    j["flip@1"] = (j.top1_drug != j.top1_drug_ref).astype(float)
    j["corrected_flip@1"] = ((j["rank"] == 1) & (j["rank_ref"] > 1)).astype(float)
    j["reverse_flip@1"] = ((j["rank_ref"] == 1) & (j["rank"] > 1)).astype(float)
    j["d_reciprocal_rank"] = j.reciprocal_rank - j.reciprocal_rank_ref
    return j


def gate3_summary(j: pd.DataFrame, label: dict) -> dict:
    rec = dict(label)
    rec["n"] = len(j)
    for col in ("delta_rank", "flip@1", "corrected_flip@1", "reverse_flip@1",
                "d_reciprocal_rank"):
        rec[col] = float(j[col].mean())
        rec[f"{col}_lo"], rec[f"{col}_hi"] = pc.cluster_bootstrap(j, col, "cell_line")
    rec["frac_delta_rank_positive"] = float((j.delta_rank > 0).mean())
    rec["frac_delta_rank_negative"] = float((j.delta_rank < 0).mean())
    return rec


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--phase-a", required=True)
    ap.add_argument("--phase-b", required=True)
    ap.add_argument("--phase-c", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    pa, pb, pcd, out = Path(a.phase_a), Path(a.phase_b), Path(a.phase_c), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    A = pd.read_csv(pa / "per_query.csv.gz")
    B = pd.read_csv(pb / "per_query.csv.gz")
    g1o = pd.read_csv(pcd / "gate1_observed.csv")
    g2o = pd.read_csv(pcd / "gate2_observed.csv")
    g1p = pd.read_csv(pb / "gate1_predicted.csv.gz")
    log(f"phase A {A.shape}, phase B {B.shape}, gate1 {g1o.shape}, gate2 {g2o.shape}")

    # ---- gate 3 ----
    rows, pairs = [], {}
    for ref in (MEAN_SCORER, MAG_SCORER):
        j = route_pair(A, POP_SCORER, ref, [])
        pairs[("oracle", "oracle", ref)] = j
        rows.append(gate3_summary(j, {"phase": "oracle", "predictor": "oracle",
                                      "population": POP_SCORER, "reference": ref}))
        for p, g in B.groupby("predictor"):
            jj = route_pair(g, POP_SCORER, ref, ["predictor"])
            pairs[("predicted", p, ref)] = jj
            rows.append(gate3_summary(jj, {"phase": "predicted", "predictor": p,
                                           "population": POP_SCORER, "reference": ref}))
    gate3 = pd.DataFrame(rows)
    gate3.to_csv(out / "gate3_decision_relevance.csv", index=False)

    # ---- gate 1 fidelity: does a predictor reproduce the observed differential response? ----
    obs = g1o[["cell_line", "drug", "D", "induced_cosine"]].rename(
        columns={"D": "D_obs", "induced_cosine": "cos_obs"})
    g1p["D_pred"] = 1.0 - g1p.predicted_induced_cosine
    pred = (g1p.groupby(["cell_line", "predictor", "drug"], as_index=False)
                .agg(D_pred=("D_pred", "mean"), n_seed=("D_pred", "size")))
    fid = pred.merge(obs, on=["cell_line", "drug"], how="inner")
    frows = []
    for p, g in fid.groupby("predictor"):
        ok = g.dropna(subset=["D_obs", "D_pred"])
        rho = spearmanr(ok.D_obs, ok.D_pred).statistic if ok.D_pred.nunique() > 1 else np.nan
        frows.append({"predictor": p, "n": len(ok),
                      "median_D_obs": float(ok.D_obs.median()),
                      "median_D_pred": float(ok.D_pred.median()),
                      "max_abs_D_pred": float(ok.D_pred.abs().max()),
                      "frac_D_pred_below_1e-6": float((ok.D_pred.abs() < 1e-6).mean()),
                      "spearman_obs_vs_pred": float(rho) if rho == rho else np.nan})
    pd.DataFrame(frows).to_csv(out / "gate1_fidelity.csv", index=False)
    fid.to_csv(out / "gate1_observed_vs_predicted.csv.gz", index=False)

    # ---- one row per query, carrying every gate and every outcome ----
    def per_query(j, tag):
        g = j.groupby(["cell_line", "drug"], as_index=False).agg(
            **{f"dMRR_{tag}": ("d_reciprocal_rank", "mean"),
               f"corrected_flip_{tag}": ("corrected_flip@1", "mean"),
               f"reverse_flip_{tag}": ("reverse_flip@1", "mean"),
               f"delta_rank_{tag}": ("delta_rank", "mean")})
        return g

    joined = obs.merge(g2o[["cell_line", "drug", "A_sup", "A_unsup", "G"]],
                       on=["cell_line", "drug"], how="outer")
    joined = joined.merge(per_query(pairs[("oracle", "oracle", MEAN_SCORER)], "oracle"),
                          on=["cell_line", "drug"], how="left")
    for p in sorted(B.predictor.unique()):
        joined = joined.merge(per_query(pairs[("predicted", p, MEAN_SCORER)], p),
                              on=["cell_line", "drug"], how="left")
    joined.to_csv(out / "per_query_joined.csv.gz", index=False)

    # ---- section 13: the pre-specified quartile grid ----
    q = joined.dropna(subset=["D_obs", "A_sup"]).copy()
    q["D_quartile"] = pd.qcut(q.D_obs, 4, labels=["Q1", "Q2", "Q3", "Q4"])
    q["A_quartile"] = pd.qcut(q.A_sup, 4, labels=["Q1", "Q2", "Q3", "Q4"], duplicates="drop")
    grid_rows = []
    outcomes = ["dMRR_oracle", "corrected_flip_oracle"] + \
               [f"dMRR_{p}" for p in sorted(B.predictor.unique())]
    for (dq, aq), g in q.groupby(["D_quartile", "A_quartile"], observed=True):
        rec = {"D_quartile": dq, "A_quartile": aq, "n_queries": len(g),
               "median_D": float(g.D_obs.median()), "median_A_sup": float(g.A_sup.median())}
        for o in outcomes:
            rec[o] = float(g[o].mean()) if o in g else np.nan
        grid_rows.append(rec)
    pd.DataFrame(grid_rows).to_csv(out / "three_gate_grid.csv", index=False)

    # ---- section 14: the four cases ----
    crows = []
    for p in sorted(B.predictor.unique()):
        d = joined.dropna(subset=["dMRR_oracle", f"dMRR_{p}"])
        o_gain, p_gain = d.dMRR_oracle > 0, d[f"dMRR_{p}"] > 0
        crows.append({
            "predictor": p, "n_queries": len(d),
            "mean_dMRR_oracle": float(d.dMRR_oracle.mean()),
            "mean_dMRR_predicted": float(d[f"dMRR_{p}"].mean()),
            "case_I_neither": int((~o_gain & ~p_gain).sum()),
            "case_II_oracle_only": int((o_gain & ~p_gain).sum()),
            "case_III_both": int((o_gain & p_gain).sum()),
            "case_IV_predicted_only": int((~o_gain & p_gain).sum()),
            "retained_fraction_of_oracle_gain": (float(d[f"dMRR_{p}"].mean() / d.dMRR_oracle.mean())
                                                 if d.dMRR_oracle.mean() != 0 else np.nan),
        })
    pd.DataFrame(crows).to_csv(out / "oracle_to_prediction.csv", index=False)

    (out / "provenance.json").write_text(json.dumps({
        "phase_a": str(pa), "phase_b": str(pb), "phase_c": str(pcd),
        "population_scorer": POP_SCORER, "mean_scorer": MEAN_SCORER,
        "magnitude_diagnostic": MAG_SCORER,
        "n_queries_with_both_gates": int(len(q)),
        "runtime_seconds": round(time.time() - t0, 1),
    }, indent=2) + "\n")
    log(gate3[["phase", "predictor", "reference", "delta_rank", "corrected_flip@1",
               "reverse_flip@1", "flip@1"]].round(4).to_string(index=False))
    log(f"wrote {out} ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    sys.exit(main())
