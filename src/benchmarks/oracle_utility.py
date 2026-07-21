"""Oracle welfare functions and decision metrics for HIR-Bench.

Oracle = uses true latent targets and utility matrix (u[d,k]).
Predictability layer must NOT import this module.
"""
from __future__ import annotations

import numpy as np

from .heterogeneous_retrieval_benchmark import HIRCell


# ── welfare functions ────────────────────────────────────────────────────────

def welfare_mean(cell: HIRCell) -> np.ndarray:
    """U_mean[d] = sum_k w_k * u[d,k].  Shape (n_drugs,)."""
    return cell.utility_matrix @ cell.true_weights


def welfare_worst(cell: HIRCell) -> np.ndarray:
    """U_worst[d] = min_k u[d,k].  Shape (n_drugs,)."""
    return cell.utility_matrix.min(axis=1)


def welfare_cvar(cell: HIRCell, q: float = 0.5) -> np.ndarray:
    """CVaR welfare: average of the bottom q fraction of subpop utilities per drug."""
    K = cell.utility_matrix.shape[1]
    n_bottom = max(1, int(np.ceil(q * K)))
    sorted_u = np.sort(cell.utility_matrix, axis=1)  # ascending
    return sorted_u[:, :n_bottom].mean(axis=1)


WELFARE_FUNCTIONS = {
    "mean": welfare_mean,
    "worst": welfare_worst,
    "cvar_0.5": lambda cell: welfare_cvar(cell, q=0.5),
}


# ── oracle decisions ─────────────────────────────────────────────────────────

def oracle_population_optimal(cell: HIRCell, welfare: str = "mean") -> tuple:
    """Return (optimal_drug_id, optimal_welfare_value) under the given welfare."""
    U = WELFARE_FUNCTIONS[welfare](cell)
    idx = int(np.argmax(U))
    return cell.drug_ids[idx], float(U[idx])


def oracle_mean_optimal(cell: HIRCell) -> tuple:
    """Return the drug that is optimal under collapsed mean-signature matching.

    This is the drug whose *mean response* (averaged across subpops, weighted) is closest
    to the *mean query*.  Equivalent to argmax of welfare_mean — the same as
    oracle_population_optimal with welfare='mean'.
    """
    U = welfare_mean(cell)
    idx = int(np.argmax(U))
    return cell.drug_ids[idx], float(U[idx])


def oracle_flip_risk(cell: HIRCell, welfare: str = "worst") -> int:
    """1 if mean-optimal drug differs from population-optimal drug under the given welfare.

    Handles ties: if the welfare gap between the population-optimal and mean-optimal
    drugs is within numerical tolerance, there is no meaningful flip.
    """
    U_welf = WELFARE_FUNCTIONS[welfare](cell)
    U_mean = welfare_mean(cell)
    pop_idx = int(np.argmax(U_welf))
    mean_idx = int(np.argmax(U_mean))
    if pop_idx == mean_idx:
        return 0
    # Check if the welfare difference is within tolerance
    welfare_range = float(U_welf.max() - U_welf.min())
    tol = max(1e-8, welfare_range * 1e-6)
    gap = float(U_welf[pop_idx] - U_welf[mean_idx])
    if abs(gap) < tol:
        return 0  # tie — no meaningful flip
    return 1


def oracle_utility_gap(cell: HIRCell, welfare: str = "worst") -> float:
    """U[population_optimal] - U[mean_optimal] under the given welfare.  >= 0."""
    U = WELFARE_FUNCTIONS[welfare](cell)
    pop_idx = int(np.argmax(U))
    mean_U = welfare_mean(cell)
    mean_idx = int(np.argmax(mean_U))
    return float(U[pop_idx] - U[mean_idx])


def decision_regret(cell: HIRCell, selected_drug: str, welfare: str = "mean") -> float:
    """regret = U[oracle_optimal] - U[selected].  >= 0 when oracle is better."""
    U = WELFARE_FUNCTIONS[welfare](cell)
    opt_val = float(U.max())
    sel_idx = cell.drug_ids.index(selected_drug) if selected_drug in cell.drug_ids else -1
    if sel_idx < 0:
        return float("inf")
    return opt_val - float(U[sel_idx])
