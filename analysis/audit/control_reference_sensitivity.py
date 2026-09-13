#!/usr/bin/env python3
"""Targeted raw-vs-control-referenced population-score audit.

This deliberately covers only ContextMixtureTask settings: candidate and query
matched controls can differ there. Controlled-mixture and partial-observation
settings are excluded because their manuscript paths use one shared control or
do not have candidate-specific matched controls, respectively.

The output is one row per task setting, population scorer, and reference arm.
``population_minus_mean_*`` is the retrieval metric for that population scorer
minus the control-referenced mean-cosine baseline. A qualitative-change flag
means that the sign of that comparison changes between raw and referenced arms.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import numpy as np
import pandas as pd
import torch

from data.load_frangieh import load_frangieh
from data.load_sciplex3 import load_sciplex3
from retrieval.evaluation import rank_of
from retrieval.metrics import (
    score_coverage,
    score_energy,
    score_mean_cosine,
    score_mmd_rbf,
    score_sliced_wasserstein,
)
from retrieval.tasks import ContextMixtureTask, context_divergence_probe


POPULATION_METHODS = (
    "global_energy",
    "mmd_rbf",
    "sliced_wasserstein",
    "coverage_mean",
    "coverage_worst",
)


def _metrics(scores: list[float], gt: int) -> tuple[float, float]:
    r = rank_of(np.asarray(scores), gt)
    return float(r == 1), float(1.0 / r)


def _score_population(method: str, P, Q, labels_P, labels_Q, *, max_cells: int = 500,
                      seed: int = 0) -> float:
    """All calls use the canonical U default for energy/MMD."""
    if method == "global_energy":
        return score_energy(P, Q, max_cells=max_cells, seed=seed, estimator="u")
    if method == "mmd_rbf":
        return score_mmd_rbf(P, Q, max_cells=max_cells, seed=seed, estimator="u")
    if method == "sliced_wasserstein":
        return score_sliced_wasserstein(P, Q, max_cells=max_cells, seed=seed)
    base = "energy"
    aggregator = "mean" if method == "coverage_mean" else "worst"
    return score_coverage(P, Q, labels_P, labels_Q, base_metric=base,
                          aggregator=aggregator, max_cells=max_cells, seed=seed,
                          estimator="u")


def _offdiag_mean_batch(D: torch.Tensor) -> torch.Tensor:
    """Off-diagonal means for a batch of square matrices."""
    n = D.shape[-1]
    if n < 2:
        return torch.zeros(D.shape[0], dtype=D.dtype, device=D.device)
    return (D.sum(dim=(-2, -1)) - D.diagonal(dim1=-2, dim2=-1).sum(dim=-1)) / (n * (n - 1))


def _batch_population_distances(populations: list[np.ndarray], query: np.ndarray,
                                method: str, *, seed: int = 0) -> np.ndarray:
    """Return positive distances for a batch of equal-size populations.

    This is a batched implementation of the same U-statistic energy, median-heuristic
    RBF-MMD, and sliced-Wasserstein kernels used by ``retrieval.metrics``.  The
    sensitivity run has 200 cells per population, so no subsampling is needed under
    the canonical ``max_cells=500`` setting.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    P = torch.as_tensor(np.stack(populations), dtype=torch.float32, device=device)
    Q = torch.as_tensor(np.asarray(query), dtype=torch.float32, device=device)
    C, n, _ = P.shape
    if n < 2 or len(Q) < 2:
        return np.full(C, 1e6, dtype=np.float32)

    with torch.no_grad():
        if method == "global_energy":
            dxy = torch.cdist(P, Q.expand(C, -1, -1)).mean(dim=(-2, -1))
            dxx = _offdiag_mean_batch(torch.cdist(P, P))
            dyy = torch.cdist(Q, Q)
            dyy = (dyy.sum() - dyy.diagonal().sum()) / (len(Q) * (len(Q) - 1))
            return (2 * dxy - dxx - dyy).detach().cpu().numpy()

        if method == "mmd_rbf":
            # Match _mmd_kernel: the bandwidth is the median positive squared
            # distance in the pooled query/candidate sample, per candidate.
            Z = torch.cat([P, Q.expand(C, -1, -1)], dim=1)
            pooled_d2 = torch.cdist(Z, Z).square()
            medians = torch.stack([
                pooled_d2[i][pooled_d2[i] > 0].median() for i in range(C)
            ])
            P2 = torch.cdist(P, P).square()
            Q2 = torch.cdist(Q, Q).square()
            PQ2 = torch.cdist(P, Q).square()
            scales = (0.25, 1.0, 4.0)
            mmd = torch.zeros(C, dtype=P.dtype, device=device)
            for scale in scales:
                denom = medians * scale
                Kpp = torch.exp(-P2 / denom[:, None, None])
                Kqq = torch.exp(-Q2 / denom[:, None, None])
                Kpq = torch.exp(-PQ2 / denom[:, None, None])
                mmd = mmd + (_offdiag_mean_batch(Kpp)
                             + _offdiag_mean_batch(Kqq.expand(C, -1, -1))
                             - 2 * Kpq.mean(dim=(-2, -1))) / len(scales)
            return mmd.detach().cpu().numpy()

        if method == "sliced_wasserstein":
            # score_sliced_wasserstein fixes the projection seed at the kernel
            # default (0); its ``seed`` argument only controls subsampling.
            generator = torch.Generator(device=device).manual_seed(0)
            theta = torch.randn(P.shape[-1], 128, generator=generator,
                                device=device, dtype=P.dtype)
            theta = theta / theta.norm(dim=0, keepdim=True).clamp_min(1e-12)
            qs = torch.linspace(0, 1, 100, device=device, dtype=P.dtype)
            p_quant = torch.quantile(P @ theta, qs, dim=1).permute(1, 0, 2)
            q_quant = torch.quantile(Q @ theta, qs, dim=0)
            return (p_quant - q_quant.unsqueeze(0)).abs().mean(dim=(1, 2)).detach().cpu().numpy()

    raise ValueError(f"unknown population method {method!r}")


def _batch_population_scores(method: str, populations: list[np.ndarray], query: np.ndarray,
                             labels_P: list[np.ndarray], labels_Q: np.ndarray,
                             *, seed: int = 0) -> np.ndarray:
    """Return the manuscript score for every candidate in one query."""
    if method not in {"coverage_mean", "coverage_worst"}:
        return -_batch_population_distances(populations, query, method, seed=seed)

    P_labels = labels_P
    Q_labels = np.asarray(labels_Q).astype(int)
    per_component = []
    for k in sorted(np.unique(Q_labels).tolist()):
        Qk = query[Q_labels == k]
        valid = []
        valid_idx = []
        dists = np.full(len(populations), 1e6, dtype=np.float32)
        for i, (P, lab) in enumerate(zip(populations, P_labels)):
            Pk = P[np.asarray(lab).astype(int) == k]
            if len(Pk) >= 2 and len(Qk) >= 2:
                valid.append(Pk)
                valid_idx.append(i)
        if valid:
            # Controlled candidate libraries contain both mixed and single-state
            # populations, so valid component sizes need not be identical. Batch
            # within each size group and restore the original candidate order.
            by_size = {}
            for local_i, Pk in enumerate(valid):
                by_size.setdefault(len(Pk), []).append(local_i)
            for _, local_indices in by_size.items():
                batch = [valid[i] for i in local_indices]
                vals = _batch_population_distances(batch, Qk, "global_energy", seed=seed)
                dists[np.asarray([valid_idx[i] for i in local_indices])] = vals
        per_component.append(dists)
    D = np.stack(per_component, axis=1)
    if method == "coverage_mean":
        return -D.mean(axis=1)
    return -D.max(axis=1)


def _run_context_task(task: ContextMixtureTask, setting: str, perturbations: list[str],
                      *, alphas: tuple[float, ...], seeds: int, n_total: int,
                      n_distractors: int, seed_offset: int) -> list[dict]:
    rows = []
    for alpha in alphas:
        for perturbation in perturbations:
            for seed_i in range(seeds):
                run_seed = seed_offset + seed_i
                q = task.build(perturbation, alpha, n_total, n_distractors, run_seed)
                Q, labels_Q = q["target"], q["tlab"]
                control_Q = q["ctrl_T"]
                names = list(q["cands"])
                gt = names.index("covers-both")

                candidates = [q["cands"][name] for name in names]
                populations = [x[0] for x in candidates]
                labels_P = [x[1] for x in candidates]
                controls_P = [x[2] for x in candidates]
                mean_scores = np.asarray([
                    score_mean_cosine(P, Q, control_P=control_P, control_Q=control_Q)
                    for P, control_P in zip(populations, controls_P)
                ])
                raw_scores = {
                    method: _batch_population_scores(method, populations, Q, labels_P,
                                                      labels_Q, seed=run_seed)
                    for method in POPULATION_METHODS
                }
                ref_populations = [P - control_P for P, control_P in zip(populations, controls_P)]
                Q_ref = Q - control_Q
                ref_scores = {
                    method: _batch_population_scores(method, ref_populations, Q_ref, labels_P,
                                                      labels_Q, seed=run_seed)
                    for method in POPULATION_METHODS
                }

                mean_hit, mean_mrr = _metrics(mean_scores, gt)
                for method in POPULATION_METHODS:
                    raw_hit, raw_mrr = _metrics(raw_scores[method], gt)
                    ref_hit, ref_mrr = _metrics(ref_scores[method], gt)
                    rows.extend([
                        {
                            "dataset": "context_mixture",
                            "setting": setting,
                            "alpha": alpha,
                            "perturbation": perturbation,
                            "seed": run_seed,
                            "method": method,
                            "reference": "raw_normalized_expression",
                            "hit@1": raw_hit,
                            "mrr": raw_mrr,
                            "mean_hit@1": mean_hit,
                            "mean_mrr": mean_mrr,
                            "population_minus_mean_hit@1": raw_hit - mean_hit,
                            "population_minus_mean_mrr": raw_mrr - mean_mrr,
                        },
                        {
                            "dataset": "context_mixture",
                            "setting": setting,
                            "alpha": alpha,
                            "perturbation": perturbation,
                            "seed": run_seed,
                            "method": method,
                            "reference": "matched_control_referenced",
                            "hit@1": ref_hit,
                            "mrr": ref_mrr,
                            "mean_hit@1": mean_hit,
                            "mean_mrr": mean_mrr,
                            "population_minus_mean_hit@1": ref_hit - mean_hit,
                            "population_minus_mean_mrr": ref_mrr - mean_mrr,
                        },
                    ])
    return rows


def _crossline(data, n_seeds: int, n_drugs: int, n_total: int,
               n_distractors: int) -> list[dict]:
    pairs = (("K562", "A549"), ("A549", "MCF7"), ("K562", "MCF7"))
    rows = []
    for major, minor in pairs:
        div = context_divergence_probe(data, major, minor, min_cells=30, gate=0.9,
                                       rel_floor=0.5, seed=0, id_col="drug")
        task = ContextMixtureTask(data, major, minor, min_cells=60)
        drugs = task.divergent(div, n_drugs, n_total, id_col="drug")
        rows.extend(_run_context_task(
            task, f"crossline:{major}+{minor}", drugs,
            alphas=(0.5, 0.6, 0.7, 0.8, 0.9), seeds=n_seeds,
            n_total=n_total, n_distractors=n_distractors, seed_offset=1000))
    return rows


def _frangieh(data, n_seeds: int, n_total: int, n_distractors: int,
               perturbation: str) -> list[dict]:
    # IFNGR1 is the manuscript's within-gene, differing-control sensitivity case.
    contrasts = (("Control", "IFNγ"), ("Control", "Co-culture"),
                 ("IFNγ", "Co-culture"))
    rows = []
    for major, minor in contrasts:
        task = ContextMixtureTask(data, major, minor, min_cells=60)
        if perturbation not in task.shared:
            continue
        rows.extend(_run_context_task(
            task, f"frangieh:{major}+{minor}", [perturbation],
            alphas=(0.7,), seeds=n_seeds, n_total=n_total,
            n_distractors=n_distractors, seed_offset=2000))
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="explicit CSV output path")
    ap.add_argument("--sciplex3", default=None)
    ap.add_argument("--frangieh", default=None)
    ap.add_argument("--dataset", choices=("sciplex3", "frangieh", "both"), default="both")
    ap.add_argument("--n-seeds", type=int, default=10)
    ap.add_argument("--n-drugs", type=int, default=15)
    ap.add_argument("--n-total", type=int, default=200)
    ap.add_argument("--n-distractors", type=int, default=40)
    ap.add_argument("--frangieh-perturbation", default="IFNGR1")
    args = ap.parse_args()

    rows = []
    if args.dataset in ("sciplex3", "both"):
        rows.extend(_crossline(load_sciplex3(args.sciplex3), args.n_seeds,
                               args.n_drugs, args.n_total, args.n_distractors))
    if args.dataset in ("frangieh", "both"):
        rows.extend(_frangieh(load_frangieh(args.frangieh), args.n_seeds,
                              args.n_total, args.n_distractors,
                              args.frangieh_perturbation))

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    # Aggregate sign-change verdicts alongside the per-run table.
    summary = (pd.DataFrame(rows)
               .groupby(["setting", "alpha", "method", "reference"], dropna=False)
               [["hit@1", "mrr", "population_minus_mean_hit@1",
                 "population_minus_mean_mrr"]].mean().reset_index())
    summary_path = out.with_name(out.stem + "_summary.csv")
    summary.to_csv(summary_path, index=False)
    verdict = (summary.pivot_table(
        index=["setting", "alpha", "method"], columns="reference",
        values=["population_minus_mean_hit@1", "population_minus_mean_mrr"])
        .reset_index())
    verdict.columns = ["_".join(c).strip("_") if isinstance(c, tuple) else c
                       for c in verdict.columns]
    raw_h = "population_minus_mean_hit@1_raw_normalized_expression"
    ref_h = "population_minus_mean_hit@1_matched_control_referenced"
    raw_m = "population_minus_mean_mrr_raw_normalized_expression"
    ref_m = "population_minus_mean_mrr_matched_control_referenced"
    verdict["qualitative_change_hit@1"] = np.sign(verdict[raw_h]) != np.sign(verdict[ref_h])
    verdict["qualitative_change_mrr"] = np.sign(verdict[raw_m]) != np.sign(verdict[ref_m])
    verdict.to_csv(out.with_name(out.stem + "_qualitative.csv"), index=False)


if __name__ == "__main__":
    main()
