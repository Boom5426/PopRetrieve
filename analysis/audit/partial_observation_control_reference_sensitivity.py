#!/usr/bin/env python3
"""Minimal control-reference sensitivity for the partial-observation coverage path.

The canonical Exp12 path is untouched.  For each of its existing queries and
candidate libraries this driver compares:

* the canonical raw-population coverage score; and
* a sensitivity score after subtracting the context-matched control mean from
  both query and candidate populations.

The sensitivity arm deliberately reruns query k-means and the implemented
row-normalized cosine candidate assignment after the subtraction.  Evaluation
uses the original raw populations and the original response-matching,
minority-coverage and MoA metrics, so only the retrieval score changes.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from data.load_sciplex3 import load_sciplex3
from experiments import exp12_partial_observed_retrieval as exp12
from retrieval.metrics import score_mean_cosine
from utils.io import DATA_ROOT


METHODS = ("DART_coverage_mean", "DART_coverage_worst")
FRACTIONS = (0.2, 0.4, 0.6)
SOURCE_KEY = ("split_type", "cell_line", "heldout_drug", "heldout_MoA",
              "observed_library_fraction", "seed")


def _load_annotation():
    """Load the same evaluation-only annotation through the configured data root."""
    annotation = pd.read_csv(DATA_ROOT / "annotation" / "drug_annotation_master.csv")
    drug2moa = dict(zip(annotation.drug_name, annotation.moa_class))
    drug2targets = {}
    for _, row in annotation.iterrows():
        targets = str(row.target_genes) if pd.notna(row.target_genes) else ""
        drug2targets[row.drug_name] = set(
            target.strip() for target in targets.split(";") if target.strip()
        )
    return drug2moa, drug2targets


def _source_lookup(path):
    """Index the frozen Exp12 per-query table without recomputing its raw arm."""
    source = pd.read_csv(path)
    lookup = {}
    for _, row in source.iterrows():
        key = (
            row.split_type, row.cell_line, row.heldout_drug, row.heldout_MoA,
            round(float(row.observed_library_fraction), 8), int(row.seed),
        )
        lookup.setdefault(key, {})[row.method] = row.to_dict()
    return lookup


def _source_rows(lookup, split_type, ctx, hd, heldout_moa, fraction, seed):
    key = (split_type, ctx, hd, heldout_moa, round(float(fraction), 8), int(seed))
    try:
        rows = lookup[key]
    except KeyError as exc:
        raise KeyError(f"frozen Exp12 row not found for {key}") from exc
    required = {"mean_cosine", *METHODS}
    missing = required.difference(rows)
    if missing:
        raise KeyError(f"frozen Exp12 row for {key} is missing {sorted(missing)}")
    return rows


def _offdiag_mean_batch(D):
    n = D.shape[-1]
    return (D.sum(dim=(-2, -1)) - D.diagonal(dim1=-2, dim2=-1).sum(dim=-1)) / (n * (n - 1))


def _energy_distance_batch(populations, query):
    """Exact U-statistic energy distances for equal-size candidate batches."""
    if not populations or len(query) < 2 or len(populations[0]) < 2:
        return np.full(len(populations), 1e6, dtype=np.float32)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    P = torch.as_tensor(np.stack(populations), dtype=torch.float32, device=device)
    Q = torch.as_tensor(np.asarray(query), dtype=torch.float32, device=device)
    with torch.no_grad():
        dxy = torch.cdist(P, Q.expand(len(P), -1, -1)).mean(dim=(-2, -1))
        dxx = _offdiag_mean_batch(torch.cdist(P, P))
        dyy_mat = torch.cdist(Q, Q)
        dyy = (dyy_mat.sum() - dyy_mat.diagonal().sum()) / (len(Q) * (len(Q) - 1))
        return (2 * dxy - dxx - dyy).detach().cpu().numpy()


def _subsample(X, max_cells, seed):
    if len(X) <= max_cells:
        return X
    return X[np.random.default_rng(seed).choice(len(X), max_cells, replace=False)]


def _coverage_scores(populations, query, labels_P, labels_Q, *, seed):
    """Return (coverage-mean score, coverage-worst score) in one batched pass."""
    labels_Q = np.asarray(labels_Q).astype(int)
    per_component = []
    for k in sorted(np.unique(labels_Q).tolist()):
        Qk = query[labels_Q == k]
        distances = np.full(len(populations), 1e6, dtype=np.float32)
        groups = {}
        for i, (P, labels) in enumerate(zip(populations, labels_P)):
            Pk = P[np.asarray(labels).astype(int) == k]
            if len(Pk) >= 2 and len(Qk) >= 2:
                max_cells = min(300, len(P), len(query))
                Pks = _subsample(Pk, max_cells, seed)
                Qks = _subsample(Qk, max_cells, seed + 1)
                key = (len(Pks), len(Qks))
                if key not in groups:
                    groups[key] = (Qks, [])
                groups[key][1].append((i, Pks))
        for Qks, entries in groups.values():
            indices, Pk_batch = zip(*entries)
            distances[np.asarray(indices)] = _energy_distance_batch(list(Pk_batch), Qks)
        per_component.append(distances)
    D = np.stack(per_component, axis=1)
    return -D.mean(axis=1), -D.max(axis=1)


def _welfare_proxy_batch(cand_pops, query_X, query_states, *, seed):
    """Exact batched counterpart of Exp12's raw energy-based welfare proxy."""
    names = list(cand_pops)
    per_candidate = {name: [] for name in names}
    for state in np.unique(query_states):
        Qs = query_X[query_states == state]
        if len(Qs) < 2:
            continue
        groups = {}
        for i, name in enumerate(names):
            P = cand_pops[name]
            max_cells = min(200, len(P), len(Qs))
            Ps = _subsample(P, max_cells, seed)
            Qsample = _subsample(Qs, max_cells, seed + 1)
            key = (len(Ps), len(Qsample))
            if key not in groups:
                groups[key] = (Qsample, [])
            groups[key][1].append((i, Ps))
        distances = np.full(len(names), 1e6, dtype=np.float32)
        for Qsample, entries in groups.values():
            indices, pops = zip(*entries)
            distances[np.asarray(indices)] = _energy_distance_batch(list(pops), Qsample)
        for i, name in enumerate(names):
            per_candidate[name].append(-float(distances[i]))
    return {
        name: (min(values) if values else -1e9)
        for name, values in per_candidate.items()
    }


def _rank(scores):
    return np.argsort(-np.asarray(scores), kind="stable")


def _evaluate_single(scores, names, query_X, query_states, cand_pops,
                     split_type, hd, drug2moa, drug2targets, welfare):
    order = _rank(scores)
    top1 = names[int(order[0])]
    regret = exp12._decision_regret(welfare, top1)
    minority = int(np.unique(query_states,
                             return_counts=True)[0][np.argmin(
                                 np.unique(query_states, return_counts=True)[1])])
    mino_cov = exp12._minority_state_coverage(
        cand_pops[top1], query_X, query_states, minority,
    )
    if split_type == "leave_drug_out":
        gt_moa = exp12._same_moa(hd, drug2moa, set(names))
        moa = exp12._ranking_metrics(scores, names, gt_moa)["ndcg"]
    else:
        moa = np.nan
    gt_target = exp12._same_target(hd, drug2targets, set(names)) if hd != "batch" else set()
    target = exp12._ranking_metrics(scores, names, gt_target)["mrr"] if gt_target else np.nan
    return {
        "top1": top1,
        "top1_rank": 1,
        "decision_regret": regret,
        "minority_state_coverage": mino_cov,
        "moa_ndcg": moa,
        "target_mrr": target,
    }


def _eval_from_source(row):
    return {
        "top1": row["selected_top1_drug"],
        "top1_rank": 1,
        "decision_regret": float(row["decision_regret"]),
        "minority_state_coverage": float(row["minority_state_coverage"]),
        "moa_ndcg": float(row["moa_ndcg"]),
        "target_mrr": float(row["target_mrr"]),
    }


def _single_query_rows(split_type, ctx, hd, heldout_moa, fraction, seed,
                       query_X, ctrl, cand_pops, names, drug2moa, drug2targets,
                       *, query_states_raw, query_states_ref, ref_scores,
                       labels_raw, labels_ref, source_rows, welfare):
    rows = []
    labels_changed = [
        float(np.any(raw != ref)) for raw, ref in zip(labels_raw, labels_ref)
    ]
    mean_eval = _eval_from_source(source_rows["mean_cosine"])
    assignment_changed = float(np.mean(labels_changed)) if labels_changed else 0.0

    for method in METHODS:
        raw_eval = _eval_from_source(source_rows[method])
        ref_eval = _evaluate_single(
            ref_scores[method], names, query_X, query_states_raw, cand_pops,
            split_type, hd, drug2moa, drug2targets, welfare,
        )
        for reference, ev in (
            ("raw_normalized_expression", raw_eval),
            ("matched_control_referenced", ref_eval),
        ):
            rows.append({
                "split_type": split_type,
                "cell_line": ctx,
                "heldout_drug": hd,
                "heldout_MoA": heldout_moa,
                "observed_library_fraction": fraction,
                "seed": seed,
                "method": method,
                "reference": reference,
                "n_candidates": len(names),
                "top1": ev["top1"],
                "top1_is_mean_top1": int(ev["top1"] == mean_eval["top1"]),
                "decision_regret": ev["decision_regret"],
                "population_minus_mean_regret_reduction":
                    mean_eval["decision_regret"] - ev["decision_regret"],
                "minority_state_coverage": ev["minority_state_coverage"],
                "population_minus_mean_minority_coverage":
                    ev["minority_state_coverage"] - mean_eval["minority_state_coverage"],
                "moa_ndcg": ev["moa_ndcg"],
                "population_minus_mean_moa_ndcg":
                    ev["moa_ndcg"] - mean_eval["moa_ndcg"]
                    if np.isfinite(ev["moa_ndcg"]) and np.isfinite(mean_eval["moa_ndcg"])
                    else np.nan,
                "target_mrr": ev["target_mrr"],
                "batch_coverage": np.nan,
                "candidate_assignment_changed_fraction": assignment_changed,
                "raw_vs_referenced_top1_changed": int(raw_eval["top1"] != ref_eval["top1"]),
            })
    return rows


def _score_single_query(query_X, ctrl, cand_pops, names, seed):
    Q_ref = query_X - ctrl
    query_states_raw, _ = exp12._query_states(query_X, k=2, seed=seed)
    query_states_ref, _ = exp12._query_states(Q_ref, k=2, seed=seed)
    populations = [cand_pops[n] for n in names]
    labels_raw = [exp12._assign_states(P, query_X, query_states_raw)
                  for P in populations]
    labels_ref = [exp12._assign_states(P - ctrl, Q_ref, query_states_ref)
                  for P in populations]
    ref_mean, ref_worst = _coverage_scores(
        [P - ctrl for P in populations], Q_ref, labels_ref, query_states_ref,
        seed=seed,
    )
    method_scores = {
        "DART_coverage_mean": ref_mean,
        "DART_coverage_worst": ref_worst,
    }
    return query_states_raw, query_states_ref, labels_raw, labels_ref, method_scores


def _rows_setting_a(ds, ctx, heldout, seed, drug2moa, drug2targets, source_lookup):
    rng = np.random.default_rng(seed)
    all_drugs = sorted(set(np.asarray(ds.pert)[
        (ds.context == ctx) & (~ds.is_control)
    ].tolist()))
    ctrl = ds.control_mean(ctx)
    rows = []
    for hd in heldout:
        hd_rows = ds.treated_rows(ctx, hd)
        if len(hd_rows) < 20:
            continue
        if len(hd_rows) > 200:
            hd_rows = rng.choice(hd_rows, 200, replace=False)
        query_X = ds.X[hd_rows]
        library = [d for d in all_drugs if d != hd]
        cand_pops = exp12._build_candidate_pops(
            ds, ctx, library, max_cells=150, rng=rng,
        )
        if len(cand_pops) < 5:
            continue
        names = list(cand_pops)
        q_raw, q_ref, labels_raw, labels_ref, ref_scores = _score_single_query(
            query_X, ctrl, cand_pops, names, seed,
        )
        welfare = _welfare_proxy_batch(cand_pops, query_X, q_raw, seed=seed)
        rows.extend(_single_query_rows(
            "leave_drug_out", ctx, hd, drug2moa.get(hd, "unknown"), 1.0,
            seed, query_X, ctrl, cand_pops, names, drug2moa, drug2targets,
            query_states_raw=q_raw, query_states_ref=q_ref,
            ref_scores=ref_scores, labels_raw=labels_raw, labels_ref=labels_ref,
            source_rows=_source_rows(source_lookup, "leave_drug_out", ctx, hd,
                                     drug2moa.get(hd, "unknown"), 1.0, seed),
            welfare=welfare,
        ))
    return rows


def _rows_setting_b(ds, ctx, heldout_moas, seed, drug2moa, drug2targets, source_lookup):
    rng = np.random.default_rng(seed)
    all_drugs = sorted(set(np.asarray(ds.pert)[
        (ds.context == ctx) & (~ds.is_control)
    ].tolist()))
    ctrl = ds.control_mean(ctx)
    rows = []
    for moa in heldout_moas:
        moa_drugs = [d for d in all_drugs if drug2moa.get(d) == moa]
        if len(moa_drugs) < 2:
            continue
        hd = moa_drugs[rng.integers(len(moa_drugs))]
        hd_rows = ds.treated_rows(ctx, hd)
        if len(hd_rows) < 20:
            continue
        if len(hd_rows) > 200:
            hd_rows = rng.choice(hd_rows, 200, replace=False)
        query_X = ds.X[hd_rows]
        library = [d for d in all_drugs if drug2moa.get(d) != moa]
        cand_pops = exp12._build_candidate_pops(
            ds, ctx, library, max_cells=150, rng=rng,
        )
        if len(cand_pops) < 5:
            continue
        names = list(cand_pops)
        q_raw, q_ref, labels_raw, labels_ref, ref_scores = _score_single_query(
            query_X, ctrl, cand_pops, names, seed,
        )
        welfare = _welfare_proxy_batch(cand_pops, query_X, q_raw, seed=seed)
        rows.extend(_single_query_rows(
            "leave_MoA_out", ctx, hd, moa, len(library) / len(all_drugs), seed,
            query_X, ctrl, cand_pops, names, drug2moa, drug2targets,
            query_states_raw=q_raw, query_states_ref=q_ref,
            ref_scores=ref_scores, labels_raw=labels_raw, labels_ref=labels_ref,
            source_rows=_source_rows(source_lookup, "leave_MoA_out", ctx, hd, moa,
                                     len(library) / len(all_drugs), seed),
            welfare=welfare,
        ))
    return rows


def _rows_setting_c(ds, ctx, seed, drug2moa, drug2targets, source_lookup):
    rng = np.random.default_rng(seed)
    all_drugs = sorted(set(np.asarray(ds.pert)[
        (ds.context == ctx) & (~ds.is_control)
    ].tolist()))
    ctrl = ds.control_mean(ctx)
    rows = []
    for fraction in FRACTIONS:
        n_measured = max(5, int(fraction * len(all_drugs)))
        perm = rng.permutation(all_drugs)
        measured = list(perm[:n_measured])
        hidden = list(perm[n_measured:])
        if len(hidden) < 5:
            continue
        hidden_rows = np.concatenate([
            ds.treated_rows(ctx, d) for d in hidden[:20]
        ])
        if len(hidden_rows) > 200:
            hidden_rows = rng.choice(hidden_rows, 200, replace=False)
        query_X = ds.X[hidden_rows]
        cand_pops = exp12._build_candidate_pops(
            ds, ctx, measured, max_cells=120, rng=rng,
        )
        if len(cand_pops) < 5:
            continue
        names = list(cand_pops)
        q_raw, q_ref, labels_raw, labels_ref, ref_scores = _score_single_query(
            query_X, ctrl, cand_pops, names, seed,
        )
        welfare = _welfare_proxy_batch(cand_pops, query_X, q_raw, seed=seed)
        source_rows = _source_rows(
            source_lookup, "partial_library", ctx, "batch", "batch", fraction, seed,
        )
        mean_row = source_rows["mean_cosine"]
        mean_regret = float(mean_row["decision_regret"])
        mean_mino = float(mean_row["minority_state_coverage"])
        mean_batch_coverage = float(mean_row["batch_coverage"])
        minority = int(np.unique(q_raw, return_counts=True)[0][np.argmin(
            np.unique(q_raw, return_counts=True)[1]
        )])
        assignment_changed = float(np.mean([
            np.any(raw != ref) for raw, ref in zip(labels_raw, labels_ref)
        ]))
        for method in METHODS:
            raw_row = source_rows[method]
            ref_batch = [names[i] for i in _rank(ref_scores[method])[:5]]
            state_cov = [max(
                exp12._minority_state_coverage(cand_pops[b], query_X, q_raw, s)
                for b in ref_batch
            ) for s in np.unique(q_raw)]
            ref_batch_coverage = float(np.mean(state_cov))
            ref_pick = ref_batch[int(np.argmax([welfare[b] for b in ref_batch]))]
            ref_regret = exp12._decision_regret(welfare, ref_pick)
            ref_mino = float(np.mean([
                exp12._minority_state_coverage(
                    cand_pops[b], query_X, q_raw, minority,
                ) for b in ref_batch
            ]))
            raw_top = raw_row["selected_top1_drug"]
            ref_top = ref_batch[0]
            for reference, row, regret, mino, batch_coverage in (
                ("raw_normalized_expression", raw_row,
                 float(raw_row["decision_regret"]),
                 float(raw_row["minority_state_coverage"]),
                 float(raw_row["batch_coverage"])),
                ("matched_control_referenced", None, ref_regret, ref_mino,
                 ref_batch_coverage),
            ):
                rows.append({
                    "split_type": "partial_library", "cell_line": ctx,
                    "heldout_drug": "batch", "heldout_MoA": "batch",
                    "observed_library_fraction": fraction, "seed": seed,
                    "method": method,
                    "reference": reference,
                    "n_candidates": len(names), "top1": raw_top if row is not None else ref_top,
                    "top1_is_mean_top1": int((raw_top if row is not None else ref_top) == mean_row["selected_top1_drug"]),
                    "decision_regret": regret,
                    "population_minus_mean_regret_reduction": mean_regret - regret,
                    "minority_state_coverage": mino,
                    "population_minus_mean_minority_coverage": mino - mean_mino,
                    "moa_ndcg": np.nan, "population_minus_mean_moa_ndcg": np.nan,
                    "target_mrr": np.nan,
                    "batch_coverage": batch_coverage,
                    "batch_coverage_minus_mean": batch_coverage - mean_batch_coverage,
                    "candidate_assignment_changed_fraction": assignment_changed,
                    "raw_vs_referenced_top1_changed": int(raw_top != ref_top),
                }
                )
    return rows


def run(data_path=None, source_path=None, n_drugs=40, n_seeds=5):
    ds = load_sciplex3(data_path)
    drug2moa, drug2targets = _load_annotation()
    source_path = source_path or ROOT / "results" / "exp12_partial_observed_retrieval" / "per_query_scores.csv"
    source_lookup = _source_lookup(source_path)
    rows = []
    for ctx in ("A549", "K562", "MCF7"):
        all_drugs = sorted(set(np.asarray(ds.pert)[
            (ds.context == ctx) & (~ds.is_control)
        ].tolist()))
        moa_classes = sorted(set(
            drug2moa.get(d) for d in all_drugs if drug2moa.get(d)
        ))
        moa_multi = [m for m in moa_classes if sum(
            1 for d in all_drugs if drug2moa.get(d) == m
        ) >= 2]
        for seed in range(n_seeds):
            rng = np.random.default_rng(seed)
            heldout = list(rng.choice(
                all_drugs, min(n_drugs, len(all_drugs)), replace=False,
            ))
            heldout_moas = list(rng.choice(
                moa_multi, min(len(moa_multi), 8), replace=False,
            ))
            rows.extend(_rows_setting_a(
                ds, ctx, heldout, seed, drug2moa, drug2targets, source_lookup,
            ))
            rows.extend(_rows_setting_b(
                ds, ctx, heldout_moas, seed, drug2moa, drug2targets, source_lookup,
            ))
            rows.extend(_rows_setting_c(
                ds, ctx, seed, drug2moa, drug2targets, source_lookup,
            ))
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--sciplex3", default=None)
    ap.add_argument("--source", default=None,
                    help="frozen Exp12 per-query table used for the canonical raw arm")
    ap.add_argument("--n-drugs", type=int, default=40)
    ap.add_argument("--n-seeds", type=int, default=5)
    args = ap.parse_args()
    df = run(args.sciplex3, args.source, args.n_drugs, args.n_seeds)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)

    group = ["split_type", "cell_line", "method", "reference"]
    agg = df.groupby(group, dropna=False).agg(
        n_queries=("seed", "count"),
        mean_regret_reduction=("population_minus_mean_regret_reduction", "mean"),
        median_regret_reduction=("population_minus_mean_regret_reduction", "median"),
        mean_minority_gain=("population_minus_mean_minority_coverage", "mean"),
        median_minority_gain=("population_minus_mean_minority_coverage", "median"),
        mean_moa_gain=("population_minus_mean_moa_ndcg", "mean"),
        median_moa_gain=("population_minus_mean_moa_ndcg", "median"),
        mean_batch_coverage_gain=("batch_coverage_minus_mean", "mean"),
        top1_mean_agreement=("top1_is_mean_top1", "mean"),
        assignment_changed_fraction=("candidate_assignment_changed_fraction", "mean"),
    ).reset_index()
    agg.to_csv(out.with_name(out.stem + "_summary.csv"), index=False)

    pivot = agg.pivot_table(
        index=["split_type", "cell_line", "method"],
        columns="reference", values=[
            "mean_regret_reduction", "median_regret_reduction",
            "mean_minority_gain", "median_minority_gain",
            "mean_moa_gain", "median_moa_gain",
            "mean_batch_coverage_gain", "top1_mean_agreement",
            "assignment_changed_fraction",
        ],
    ).reset_index()
    pivot.columns = [
        "_".join(x).strip("_") if isinstance(x, tuple) else x
        for x in pivot.columns
    ]
    pivot.to_csv(out.with_name(out.stem + "_comparison.csv"), index=False)
    print(f"wrote {len(df)} rows to {out}")


if __name__ == "__main__":
    main()
