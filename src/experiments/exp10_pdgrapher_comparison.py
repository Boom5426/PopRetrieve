#!/usr/bin/env python
"""Experiment 10 — PDGrapher-aligned comparison on the closed-loop benchmark.

Direct inverse-design (PDGrapher family) ranks intervention *targets*; DART ranks *drugs* by
population retrieval. This experiment puts them on common ground using the repository's
precomputed closed-loop benchmark (``data/benchmarks/pdgrapher_closed_loop_benchmark.parquet``
+ the CIGS signal parquets), so no PDGrapher training is needed — its ranked outputs for the
LINCS/CIGS closed-loop task are materialized as per-candidate scores.

Method families mapped onto the benchmark's per-candidate signals:
    graph_proximity     PDGrapher-family inverse design (network proximity to the target field)
    target_overlap      PDGrapher-family (candidate-target vs query-target overlap)
    signature_reversal  CMap-style signature-reversal retrieval
    distance_reduction  DART-flavored distributional signal — source→target *population*
                        distance reduction from response_rescue_labels_CIGS (how much a
                        candidate moves the diseased population toward the target state)
    field_match         upper-reference relevance signal (the field ground-truth itself)
    random              lower-reference

Two comparison directions (the spec's requirement):
  (A) DRUG ranking: every signal is scored on Drug Hit@1/5, MRR, nDCG@10, top-k overlap vs the
      PDGrapher reference (graph_proximity), top-1 flip, Δrank, and runtime.
  (B) TARGET ranking: each drug ranking is converted to a target ranking via the drug→target
      map (adapter), then scored on target nDCG@10 and target recall@K against the query's
      ground-truth targets — and, symmetrically, PDGrapher's target ranking is converted to a
      drug ranking and re-scored, demonstrating the bridge works both ways.

Outputs (results/exp10_pdgrapher_comparison/):
    drug_ranking_comparison.csv    per (query, signal) drug-side metrics
    drug_ranking_summary.csv       per-signal drug metrics averaged over queries
    target_ranking_comparison.csv  per (query, signal) target nDCG / recall@K
    flip_vs_pdgrapher.csv          each signal vs graph_proximity: overlap, top-1 flip, Δrank
    conversion_consistency.csv     target→drug round-trip recovery of GT drugs
    runtime.csv                    per-signal ranking wall-clock
    provenance.csv                 benchmark path, drug→target source, GT definition
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from retrieval.evaluation import (retrieval_metrics, topk_overlap, top1_flip, delta_rank,
                                   top1_index, rank_of)
from retrieval.target_metrics import target_ndcg, target_recall_at_k, Timer


def _multi_gt_metrics(scores: np.ndarray, relevant_mask: np.ndarray,
                      ks=(1, 5, 10, 20)) -> dict:
    """Retrieval metrics for a single query with possibly MANY relevant candidates.

    Hit@k = 1 if any relevant candidate ranks within top-k; MRR from the best (smallest) rank
    of a relevant candidate; nDCG@10 over all relevant candidates (binary gains); plus the best
    relevant rank. ``scores`` and ``relevant_mask`` are aligned 1-D over the candidate list.
    """
    scores = np.asarray(scores, dtype=float)
    relevant_mask = np.asarray(relevant_mask).astype(bool)
    rel_idx = np.flatnonzero(relevant_mask)
    if len(rel_idx) == 0:
        return {}
    # Break ties deterministically by sorting candidates by score desc; a candidate's rank is
    # its 1-indexed position in that order (no tie inflation — each position is unique).
    order = np.argsort(-scores, kind="stable")
    pos_of = np.empty(len(scores), dtype=int)
    pos_of[order] = np.arange(1, len(scores) + 1)
    ranks = pos_of[rel_idx]
    best = int(ranks.min())
    out = {f"hit@{k}": float(best <= k) for k in ks}
    out["mrr"] = float(1.0 / best)
    # nDCG@10: binary-relevance DCG over relevant candidates in top-10 vs ideal (all relevant
    # packed at the top). Both capped at 10 positions so the ratio stays in [0, 1].
    n_rel_top = min(int(np.sum(ranks <= 10)), 10)
    dcg = float(np.sum([1.0 / np.log2(r + 1) for r in ranks if r <= 10][:10]))
    ideal = float(np.sum([1.0 / np.log2(i + 2) for i in range(min(len(rel_idx), 10))]))
    out["ndcg@10"] = dcg / ideal if ideal > 0 else 0.0
    out["best_rank"] = best
    out["median_rank"] = float(np.median(ranks))
    return out
from utils.io import results_path, write_csv
from utils.logging import log, section

from baselines.pdgrapher_adapter import (
    load_closed_loop_benchmark, benchmark_queries, ground_truth_drugs, ground_truth_targets,
    ranking_for, DrugTargetMap, target_ranking_to_drug_ranking, drug_ranking_to_target_ranking,
    FIELD_GT_THRESH,
)

OUT = "exp10_pdgrapher_comparison"
PDGRAPHER_REF = "graph_proximity"
# signal name -> (baseline_name in benchmark OR external parquet, score column, family)
DRUG_SIGNALS = {
    "graph_proximity":   ("graph_proximity", "graph_proximity", "pdgrapher_inverse_design"),
    "target_overlap":    ("target_overlap", "target_overlap", "pdgrapher_inverse_design"),
    "signature_reversal": ("signature_reversal", "signature_reversal", "signature_retrieval"),
    "field_match":       ("field_match", "field_match", "reference_upper"),
    "random":            ("random", "final_score", "reference_lower"),
}
KS = (1, 5, 10, 20)


def _distance_reduction_ranking(query_id: str, repo_root: Path) -> pd.DataFrame:
    """DART-flavored signal: source→target population distance reduction per candidate.

    From response_rescue_labels_CIGS: higher relative distance reduction = candidate moves the
    diseased population closer to the target state = better (the population-distance analogue of
    DART's distributional retrieval on this closed-loop task). Joined to drug_name via the
    benchmark's candidate_id (SMILES).
    """
    rr = pd.read_parquet(repo_root / "data" / "benchmarks" / "response_rescue_labels_CIGS.parquet")
    bench = pd.read_parquet(repo_root / "data" / "benchmarks" / "pdgrapher_closed_loop_benchmark.parquet")
    sub = rr[rr.query_id == query_id].copy()
    id2name = dict(zip(bench.candidate_id, bench.drug_name))
    sub["drug_name"] = sub.candidate_id.map(id2name)
    sub = sub.dropna(subset=["drug_name"])
    col = "relative_source_to_target_distance_reduction"
    out = sub.groupby("drug_name")[col].max().reset_index().rename(columns={col: "score"})
    return out.sort_values("score", ascending=False).reset_index(drop=True)


def _drug_scores_for_signal(df, query_id, signal, repo_root):
    """Return dict drug_name -> score for a signal on a query."""
    if signal == "distance_reduction":
        r = _distance_reduction_ranking(query_id, repo_root)
        return dict(zip(r.drug_name, r.score))
    baseline_name, col, _ = DRUG_SIGNALS[signal]
    r = ranking_for(df, query_id, baseline_name, col)
    return dict(zip(r.drug_name, r.score))


def run(repo_root=None):
    section("EXP10 — PDGrapher-aligned closed-loop comparison")
    repo_root = Path(repo_root) if repo_root else Path(__file__).resolve().parents[2]
    df = load_closed_loop_benchmark()
    queries = benchmark_queries(df)
    dt_map = DrugTargetMap.from_drug_target_prior()   # exact 1369/1369 benchmark coverage
    log(f"[exp10] {len(queries)} queries, {df.drug_name.nunique()} candidate drugs, "
        f"drug→target map: {len(dt_map.drug2targets)} drugs / {len(dt_map.target2drugs)} targets")

    signals = list(DRUG_SIGNALS) + ["distance_reduction"]
    all_drugs = sorted(df.drug_name.dropna().unique())

    drug_rows, target_rows, flip_rows, conv_rows = [], [], [], []
    rt_acc = {s: [] for s in signals}

    for q in queries:
        gt_drugs = set(ground_truth_drugs(df, q, FIELD_GT_THRESH))
        gt_targets = set(ground_truth_targets(df, q, dt_map, FIELD_GT_THRESH))
        # candidate universe for this query = drugs present in the benchmark for it
        q_drugs = sorted(df[df.query_id == q].drug_name.dropna().unique())
        # precompute per-signal scores
        sig_scores = {}
        for s in signals:
            t0 = time.perf_counter()
            sc = _drug_scores_for_signal(df, q, s, repo_root)
            rt_acc[s].append(time.perf_counter() - t0)
            sig_scores[s] = sc

        # reference (PDGrapher) ordering over the shared candidate order
        order = q_drugs
        ref_vec = np.array([sig_scores[PDGRAPHER_REF].get(d, -1e9) for d in order])

        for s in signals:
            vec = np.array([sig_scores[s].get(d, -1e9) for d in order])
            # ---- (A) drug-side retrieval metrics (multi-relevant) ----
            true_pos = np.array([1 if d in gt_drugs else 0 for d in order])
            if true_pos.sum() == 0:
                continue
            rm = _multi_gt_metrics(vec, true_pos, ks=(1, 5, 10, 20))
            drug_rows.append({"query_id": q, "signal": s,
                              "family": (DRUG_SIGNALS[s][2] if s in DRUG_SIGNALS
                                         else "dart_distributional"),
                              "n_gt": int(true_pos.sum()), "n_cand": len(order), **rm})
            # ---- flip vs PDGrapher ----
            if s != PDGRAPHER_REF:
                ov = topk_overlap(vec, ref_vec, k=10, metric="fraction")
                fl = top1_flip(vec, ref_vec)
                # delta_rank of the first GT drug: does s rank it higher than PDGrapher?
                gt_idx = int(np.argmax(true_pos))
                dr = delta_rank(ref_vec, vec, gt_idx)
                flip_rows.append({"query_id": q, "signal": s, "topk_overlap": ov,
                                  "top1_flip": int(fl), "delta_rank_vs_pdgrapher": dr})

            # ---- (B) target-side: convert drug ranking -> target ranking ----
            t_scores = drug_ranking_to_target_ranking(sig_scores[s], dt_map, agg="max")
            t_order = sorted(t_scores, key=lambda t: t_scores[t], reverse=True)
            t_vec = np.array([t_scores[t] for t in t_order])
            t_rel = np.array([1 if t in gt_targets else 0 for t in t_order], dtype=float)
            if t_rel.sum() > 0:
                tndcg = target_ndcg(t_vec, t_rel, k=10)
                trec = {f"target_recall@{k}": target_recall_at_k(t_vec, t_rel, k) for k in KS}
                target_rows.append({"query_id": q, "signal": s, "n_gt_targets": int(t_rel.sum()),
                                    "n_targets": len(t_order), "target_ndcg@10": tndcg, **trec})

        # ---- conversion consistency: PDGrapher TARGET ranking -> DRUG ranking ----
        # build a target ranking from graph_proximity's own drug scores, then convert back
        gp_drug = sig_scores[PDGRAPHER_REF]
        gp_target = drug_ranking_to_target_ranking(gp_drug, dt_map, agg="max")
        back_drug = target_ranking_to_drug_ranking(gp_target, dt_map, drugs=q_drugs, agg="max")
        bd_order = sorted(back_drug, key=lambda d: back_drug[d], reverse=True)
        bd_vec = np.array([back_drug[d] for d in bd_order])
        bd_tp = np.array([1 if d in gt_drugs else 0 for d in bd_order])
        if bd_tp.sum() > 0:
            rm_back = _multi_gt_metrics(bd_vec, bd_tp, ks=(1, 5, 10, 20))
            conv_rows.append({"query_id": q, "roundtrip": "pdgrapher_drug→target→drug",
                              "hit@1": rm_back["hit@1"], "hit@5": rm_back["hit@5"],
                              "mrr": rm_back["mrr"], "ndcg@10": rm_back["ndcg@10"],
                              "n_gt": int(bd_tp.sum())})

    # ---- assemble & write ----
    drug_df = pd.DataFrame(drug_rows)
    write_csv(drug_df, results_path(OUT, "drug_ranking_comparison.csv"))
    metric_cols = [c for c in drug_df.columns
                   if c.startswith(("hit@", "mrr", "ndcg", "best_rank", "median_rank"))]
    drug_summ = drug_df.groupby(["signal", "family"])[metric_cols].mean().reset_index()
    drug_summ = drug_summ.sort_values("hit@1", ascending=False)
    write_csv(drug_summ, results_path(OUT, "drug_ranking_summary.csv"))

    tgt_df = pd.DataFrame(target_rows)
    write_csv(tgt_df, results_path(OUT, "target_ranking_comparison.csv"))
    tgt_summ = tgt_df.groupby("signal")[[c for c in tgt_df.columns
                                         if c.startswith("target_")]].mean().reset_index()
    write_csv(tgt_summ, results_path(OUT, "target_ranking_summary.csv"))

    write_csv(pd.DataFrame(flip_rows), results_path(OUT, "flip_vs_pdgrapher.csv"))
    write_csv(pd.DataFrame(conv_rows), results_path(OUT, "conversion_consistency.csv"))

    rt = pd.DataFrame([{"signal": s, "per_query_ms": float(np.mean(rt_acc[s]) * 1e3),
                        "n_queries": len(rt_acc[s])} for s in signals])
    write_csv(rt, results_path(OUT, "runtime.csv"))

    write_csv(pd.DataFrame([{
        "benchmark": "pdgrapher_closed_loop_benchmark.parquet",
        "drug_target_map": "drug_target_prior.parquet (CIGS graph, exact 1369/1369)",
        "gt_definition": f"field_match >= {FIELD_GT_THRESH}",
        "pdgrapher_reference_signal": PDGRAPHER_REF,
        "dart_signal": "distance_reduction (relative source→target population distance reduction)",
        "note": "no PDGrapher training; precomputed closed-loop ranked outputs consumed",
    }]), results_path(OUT, "provenance.csv"))

    # ---- console headline ----
    section("EXP10 HEADLINE — drug-side ranking (mean over queries)")
    log(drug_summ.round(3).to_string(index=False))
    section("EXP10 — target-side ranking (mean over queries)")
    log(tgt_summ.round(3).to_string(index=False))
    section("EXP10 — conversion consistency (PDGrapher drug→target→drug round-trip)")
    if conv_rows:
        cc_df = pd.DataFrame(conv_rows)
        log(f"  round-trip Hit@1={cc_df['hit@1'].mean():.3f}  Hit@5={cc_df['hit@5'].mean():.3f}  "
            f"MRR={cc_df['mrr'].mean():.3f}  (vs direct graph_proximity in drug_ranking_summary)")
    return {"drug_summary": drug_summ.to_dict("records")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=None)
    ap.parse_args()
    run()


if __name__ == "__main__":
    main()
