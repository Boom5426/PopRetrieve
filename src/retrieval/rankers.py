"""Candidate rankers: turn a task's query dict into per-scorer candidate scores.

Faithful 1:1 ports of the original ``score_query`` (controlled) and ``score``
(cross-line / frangieh) plus the metric-robustness variant, all routed through the
unified ``retrieval.metrics`` interface. The four headline scorers are:

    mean_cosine    — cosine of mean-delta signatures            (incumbent 'mean-out')
    global_energy  — -energy_distance(whole cand, whole target) (K=1 distributional)
    coverage_mean  — -mean_k  energy over subpops               (routed via coverage_aggregate)
    coverage_worst — -max_k   energy over subpops               (routed via coverage_aggregate)

Coverage is now computed through the validated ``coverage_aggregate`` (the originals
hard-coded ``-0.5*(ea+eb)`` / ``-max`` and bypassed it); the values are identical.
Every ranker returns ``{scorer: {candidate_name: score}}`` (higher = better) — the
full per-query score vectors that exp07 ranking-flip consumes.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from data.population import RetrievalResult
from retrieval.evaluation import rank_of
from retrieval.metrics import (
    energy_distance_u, mmd_rbf_u, sliced_wasserstein, _tensor,
    score_mean_cosine, score_mean_l2, score_energy, score_coverage,
)

# mean_l2 sits beside mean_cosine deliberately: it is not a fifth method competing with the
# others but the control that says how much of any population scorer's advantage over cosine is
# response magnitude rather than population structure. Added 2026-09-03, after Phase A found that
# two thirds of the oracle gain over cosine is recovered by it.
SCORERS = ["mean_cosine", "mean_l2", "global_energy", "coverage_mean", "coverage_worst"]
METRIC_SET = ["mean_cosine", "energy", "mmd", "sliced_w"]


def _cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return 0.0 if na < 1e-12 or nb < 1e-12 else float(a @ b / (na * nb))


# ---------------------------------------------------------------------------
# Controlled (nearest-mean subpop split), ports eval_controlled_mixture.score_query
# ---------------------------------------------------------------------------


def score_controlled(q: dict, max_cells=None, seed: int = 0) -> dict:
    target, lab, pc = q["target"], q["target_labels"], q["pseudo_control"]
    mu_a, mu_b = target[lab == 0].mean(0), target[lab == 1].mean(0)

    def split_labels(P):
        m = np.linalg.norm(P - mu_a, axis=1) < np.linalg.norm(P - mu_b, axis=1)
        return np.where(m, 0, 1)

    out = {s: {} for s in SCORERS}
    for name, P in q["candidates"].items():
        out["mean_cosine"][name] = score_mean_cosine(P, target, control_P=pc, control_Q=pc)
        out["mean_l2"][name] = score_mean_l2(P, target, control_P=pc, control_Q=pc)
        out["global_energy"][name] = score_energy(P, target, max_cells=max_cells, seed=seed)
        labP = split_labels(P)
        out["coverage_mean"][name] = score_coverage(P, target, labP, lab,
                                                     aggregator="mean", max_cells=max_cells, seed=seed)
        out["coverage_worst"][name] = score_coverage(P, target, labP, lab,
                                                      aggregator="worst", max_cells=max_cells, seed=seed)
    return out


# ---------------------------------------------------------------------------
# Labeled (known-context subpop split), ports crossline / frangieh score()
# ---------------------------------------------------------------------------


def score_labeled(q: dict, max_cells=None, seed: int = 0) -> dict:
    T, tlab, cT = q["target"], q["tlab"], q["ctrl_T"]
    out = {s: {} for s in SCORERS}
    for name, (P, plab, cP) in q["cands"].items():
        out["mean_cosine"][name] = score_mean_cosine(P, T, control_P=cP, control_Q=cT)
        out["mean_l2"][name] = score_mean_l2(P, T, control_P=cP, control_Q=cT)
        out["global_energy"][name] = score_energy(P, T, max_cells=max_cells, seed=seed)
        out["coverage_mean"][name] = score_coverage(P, T, plab, tlab,
                                                    aggregator="mean", max_cells=max_cells, seed=seed)
        out["coverage_worst"][name] = score_coverage(P, T, plab, tlab,
                                                     aggregator="worst", max_cells=max_cells, seed=seed)
    return out


# ---------------------------------------------------------------------------
# Metric robustness (global K=1 with energy / MMD / sliced-W), ports
# eval_metric_robustness.score
# ---------------------------------------------------------------------------


def _cap(P, n, r):
    return P if len(P) <= n else P[r.choice(len(P), n, replace=False)]


def score_metric_robustness(q: dict, cap: int = 220, seed: int = 0,
                            n_proj: int = 64) -> dict:
    r = np.random.default_rng(seed)
    ctrl = q["pseudo_control"]
    T = q["target"]
    tgt_sig = T.mean(0) - ctrl
    Tt = _tensor(_cap(T, cap, r))
    out = {m: {} for m in METRIC_SET}
    import torch
    for name, P in q["candidates"].items():
        out["mean_cosine"][name] = _cos(tgt_sig, P.mean(0) - ctrl)
        Pt = _tensor(_cap(P, cap, r))
        with torch.no_grad():
            out["energy"][name] = -float(energy_distance_u(Pt, Tt))
            out["mmd"][name] = -float(mmd_rbf_u(Pt, Tt))
            out["sliced_w"][name] = -float(sliced_wasserstein(Pt, Tt, n_proj=n_proj))
    return out


# ---------------------------------------------------------------------------
# RetrievalResult assembly (plan §6.3 abstraction)
# ---------------------------------------------------------------------------


def build_result(query_id: str, names: list[str], score_dict: dict,
                 ground_truth: str) -> RetrievalResult:
    scorers = list(score_dict)
    scores_df = pd.DataFrame(
        {s: [score_dict[s][n] for n in names] for s in scorers}, index=names)
    rankings = pd.DataFrame(
        {s: [names[i] for i in np.argsort(-scores_df[s].to_numpy())] for s in scorers})
    gt = names.index(ground_truth) if ground_truth in names else None
    metric_rows = []
    for s in scorers:
        vals = scores_df[s].to_numpy()
        row = {"scorer": s, "top1": names[int(np.argmax(vals))]}
        if gt is not None:
            row["gt_rank"] = rank_of(vals, gt)
            row["gt_hit@1"] = float(int(np.argmax(vals)) == gt)
        metric_rows.append(row)
    return RetrievalResult(query_id=query_id, scores=scores_df,
                           metrics=pd.DataFrame(metric_rows), rankings=rankings)
