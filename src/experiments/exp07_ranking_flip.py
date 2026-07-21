#!/usr/bin/env python
"""Experiment 7 — Ranking-flip analysis (plan §8-Exp7 / §14-Phase2, NEW).

Lifts the story from "the distance got bigger" to "the top-ranked DRUG actually
changed". Consumes the retained per-query candidate score vectors from exp01
(controlled) and exp03 (cross-line) — which the original scripts discarded after
Hit@1 — and computes, per query, between the incumbent (mean_cosine) and ours
(global_energy):

    top-1 flip rate      — does the #1 drug change?
    decision-flip-to-GT  — did mean pick a majority-biased drug while energy picked
                           the correct covers-both drug? (the real inverse decision)
    top-k overlap (k=5)  — Jaccard of the two top-k sets
    Kendall-tau / Spearman-rho of the two rankings
    delta-rank of covers-both (rank_mean - rank_energy; +ve => energy ranks GT higher)
    delta-rank vs response divergence (cross_cos) on the cross-line data

    python src/experiments/exp07_ranking_flip.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from retrieval.evaluation import (                        # noqa: E402
    top1_flip, topk_overlap, kendall_tau, spearman_rho, delta_rank, decision_flip,
    top1_index)
from utils.io import results_path, write_csv               # noqa: E402
from utils.logging import log, section                     # noqa: E402

OUT = "exp07_ranking_flip"
GT = "covers-both"
A, B = "mean_cosine", "global_energy"     # incumbent vs ours


def flip_records(df: pd.DataFrame, group_keys: list[str], dataset: str,
                 k: int = 5) -> pd.DataFrame:
    """Per-query flip metrics between rankers A (incumbent) and B (ours)."""
    recs = []
    for key, g in df.groupby(group_keys, sort=False):
        names = g["candidate"].tolist()
        if GT not in names:
            continue
        gt = names.index(GT)
        va, vb = g[A].to_numpy(), g[B].to_numpy()
        dflip = decision_flip(va, vb, names, gt)
        rec = dict(zip(group_keys, key if isinstance(key, tuple) else (key,)))
        rec.update({
            "dataset": dataset,
            "flipped": int(top1_flip(va, vb)),
            "decision_flip_to_gt": int(dflip["decision_flip_to_gt"]),
            "a_correct": int(dflip["a_correct"]),
            "b_correct": int(dflip["b_correct"]),
            "topk_overlap": topk_overlap(va, vb, k, "jaccard"),
            "kendall_tau": kendall_tau(va, vb),
            "spearman_rho": spearman_rho(va, vb),
            "delta_rank": delta_rank(va, vb, gt),
            "top1_incumbent": names[top1_index(va)],
            "top1_ours": names[top1_index(vb)],
        })
        recs.append(rec)
    return pd.DataFrame(recs)


def run():
    p01 = results_path("exp01_sciplex3_controlled", "per_query_scores.csv")
    p03 = results_path("exp03_crossline_semireal", "per_query_scores.csv")
    frames = []
    if p01.exists():
        d01 = pd.read_csv(p01)
        frames.append(flip_records(d01, ["cell_line", "alpha", "seed"], "controlled"))
        log(f"[exp07] controlled: {d01[['cell_line','alpha','seed']].drop_duplicates().shape[0]} queries")
    else:
        log(f"[exp07] WARNING: {p01} missing — run exp01 first")
    if p03.exists():
        d03 = pd.read_csv(p03)
        frames.append(flip_records(d03, ["pair", "d_star", "alpha", "seed"], "crossline"))
        log(f"[exp07] crossline: {d03[['pair','d_star','alpha','seed']].drop_duplicates().shape[0]} queries")
    else:
        log(f"[exp07] WARNING: {p03} missing — run exp03 first")
    if not frames:
        raise SystemExit("exp07 needs exp01 and/or exp03 per_query_scores.csv")

    per_query = pd.concat(frames, ignore_index=True)

    # --- summary per dataset/setting ---
    per_query["setting"] = per_query.get("cell_line", pd.Series(index=per_query.index, dtype=object))
    per_query["setting"] = per_query["setting"].fillna(per_query.get("pair"))
    summ = per_query.groupby(["dataset", "setting"]).agg(
        n_queries=("flipped", "size"),
        top1_flip_rate=("flipped", "mean"),
        decision_flip_to_gt_rate=("decision_flip_to_gt", "mean"),
        incumbent_hit1=("a_correct", "mean"),
        ours_hit1=("b_correct", "mean"),
        mean_topk_overlap=("topk_overlap", "mean"),
        mean_kendall_tau=("kendall_tau", "mean"),
        mean_delta_rank=("delta_rank", "mean"),
    ).reset_index()
    write_csv(summ, results_path(OUT, "ranking_flip_summary.csv"))
    write_csv(per_query.groupby(["dataset", "setting"])["topk_overlap"]
              .describe().reset_index(), results_path(OUT, "topk_overlap.csv"))

    # --- delta-rank vs response divergence (cross-line) ---
    div_path = results_path("exp03_crossline_semireal", "crossline_divergence.csv")
    if div_path.exists() and "crossline" in per_query["dataset"].values:
        div = pd.read_csv(div_path)
        div = div[div.get("reliable", True)][["pair", "drug", "cross_cos"]].rename(
            columns={"drug": "d_star"})
        cl = per_query[per_query.dataset == "crossline"]
        by_dstar = cl.groupby(["pair", "d_star"]).agg(
            delta_rank=("delta_rank", "mean"),
            top1_flip_rate=("flipped", "mean"),
            incumbent_hit1=("a_correct", "mean"),
            ours_hit1=("b_correct", "mean"),
        ).reset_index().merge(div, on=["pair", "d_star"], how="left")
        write_csv(by_dstar, results_path(OUT, "delta_rank_vs_divergence.csv"))
        if by_dstar["cross_cos"].notna().sum() >= 3:
            rho = by_dstar[["cross_cos", "delta_rank"]].corr(method="spearman").iloc[0, 1]
            log(f"[exp07] Spearman(cross_cos, delta_rank) over d* = {rho:+.2f} "
                f"(more divergent => energy wins by more rank positions)")

    # --- representative decision flips (mean picks majority-biased; energy picks GT) ---
    rep = per_query[per_query.decision_flip_to_gt == 1].copy()
    rep = rep.sort_values("delta_rank", ascending=False).head(12)
    cols = ["dataset", "setting", "alpha", "seed", "top1_incumbent", "top1_ours",
            "delta_rank"]
    cols = [c for c in cols if c in rep.columns]
    write_csv(rep[cols], results_path(OUT, "representative_cases.csv"))

    section("EXP07 RANKING-FLIP SUMMARY")
    log(summ.to_string(index=False))
    log(f"\nrepresentative decision-flip cases (mean->majority-biased, energy->covers-both): "
        f"{len(per_query[per_query.decision_flip_to_gt==1])} total; top {len(rep)} saved")
    n_flip_cases = int((per_query.decision_flip_to_gt == 1).sum())
    ok = n_flip_cases >= 3
    log(f"[{'PASS' if ok else 'WARN'}] >=3 representative decision flips: {n_flip_cases} found")
    return {"n_decision_flips": n_flip_cases, "summary": summ}


def main():
    run()


if __name__ == "__main__":
    main()
