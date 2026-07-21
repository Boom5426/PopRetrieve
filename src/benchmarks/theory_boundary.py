"""Analytical flip boundary for HIR-Bench (§6 of the protocol).

Two-subpopulation, two-candidate core:

    d_M = majority-biased drug   (best for subpop 0, worst for subpop 1)
    d_C = coverage drug           (moderately good for all)

    A = u[d_M, 0] - u[d_C, 0]    majority prefers d_M by this margin
    B = u[d_C, 1] - u[d_M, 1]    minority prefers d_C by this margin

    Mean-welfare chooses d_M over d_C when  alpha*A - (1-alpha)*B > 0.
    => flip boundary  alpha* = B / (A + B)

When alpha > alpha*, collapsed mean-welfare agrees with the majority (d_M);
when alpha < alpha*, collapsed mean-welfare agrees with the minority (d_C);
worst-subpop welfare always picks d_C (if B > 0).

The boundary is *analytical* — no fitting.
"""
from __future__ import annotations

import numpy as np

from .heterogeneous_retrieval_benchmark import HIRCell


def compute_boundary(cell: HIRCell) -> dict | None:
    """Compute the analytical flip boundary for a 2-subpop cell.

    Returns dict with A, B, alpha_star, or None if n_subpops != 2 or no valid pair.
    """
    if cell.utility_matrix.shape[1] != 2:
        return None

    U = cell.utility_matrix  # (n_drugs, 2)
    # Find the drug that is best for subpop 0 (majority)
    d_M_idx = int(np.argmax(U[:, 0]))
    # Find the drug that is best for subpop 1 (minority)
    d_C_idx = int(np.argmax(U[:, 1]))

    if d_M_idx == d_C_idx:
        # No conflict — same drug is best for both
        return {"A": 0.0, "B": 0.0, "alpha_star": float("nan"),
                "d_M": cell.drug_ids[d_M_idx], "d_C": cell.drug_ids[d_C_idx],
                "no_conflict": True}

    A = float(U[d_M_idx, 0] - U[d_C_idx, 0])  # majority margin for d_M
    B = float(U[d_C_idx, 1] - U[d_M_idx, 1])  # minority margin for d_C

    if A + B <= 0:
        return {"A": A, "B": B, "alpha_star": float("nan"),
                "d_M": cell.drug_ids[d_M_idx], "d_C": cell.drug_ids[d_C_idx],
                "no_conflict": True}

    alpha_star = B / (A + B)

    return {
        "A": A, "B": B, "alpha_star": alpha_star,
        "d_M": cell.drug_ids[d_M_idx], "d_C": cell.drug_ids[d_C_idx],
        "no_conflict": False,
    }


def boundary_error(cell: HIRCell, empirical_boundary_alpha: float) -> float | None:
    """Difference between empirical and analytical boundary.

    boundary_error = empirical_boundary_alpha - alpha_star
    """
    b = compute_boundary(cell)
    if b is None or np.isnan(b["alpha_star"]):
        return None
    return empirical_boundary_alpha - b["alpha_star"]
