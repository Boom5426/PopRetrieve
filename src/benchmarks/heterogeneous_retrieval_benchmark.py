"""HIR-Bench synthetic benchmark generator.

``generate_hir_cell`` builds one benchmark cell: a query population with K subpopulations,
a candidate drug library with controlled preference conflict, latent targets per subpop,
and a utility matrix u[d,k] = -E||x - t_k||^2.

The generator is method-neutral: DART is one evaluated method entry, not the benchmark
definition.  Oracle welfare and flip risk are computed by ``oracle_utility``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np


@dataclass
class HIRCell:
    """One benchmark cell — everything needed to evaluate any retrieval method."""
    query_X: np.ndarray                          # (n_query_cells, dim)
    query_labels: np.ndarray                     # (n_query_cells,) subpop id
    candidate_populations: Dict[str, np.ndarray] # drug_id -> (n_cells, dim)
    latent_targets: np.ndarray                   # (n_subpops, dim) — oracle only
    true_weights: np.ndarray                     # (n_subpops,)
    utility_matrix: np.ndarray                   # (n_drugs, n_subpops)
    drug_ids: List[str]                          # parallel to utility_matrix rows
    metadata: dict = field(default_factory=dict)


def generate_hir_cell(
    n_subpops: int = 2,
    dim: int = 50,
    library_size: int = 20,
    majority_fraction: float = 0.7,
    conflict_level: float = 0.5,
    cells_per_subpop: int = 60,
    noise_sigma: float = 0.5,
    information_condition: str = "observed",
    seed: int = 0,
) -> HIRCell:
    """Generate one HIR-Bench cell.

    Parameters
    ----------
    n_subpops : number of subpopulations (2 for core; 3, 5 for robustness)
    dim : gene/feature dimension
    library_size : number of candidate drugs
    majority_fraction : weight of the first subpopulation (alpha)
    conflict_level : 0 = no conflict (all drugs serve all subpops equally),
                     1 = max conflict (best drug for subpop k is worst for others)
    cells_per_subpop : cells sampled per subpopulation per candidate
    noise_sigma : within-cluster Gaussian noise scale
    information_condition : 'observed' | 'predicted_mean' | 'predicted_structure'
    seed : random seed
    """
    rng = np.random.default_rng(seed)

    # ── subpopulation weights ──
    weights = np.zeros(n_subpops)
    if n_subpops == 1:
        weights[0] = 1.0
    else:
        weights[0] = majority_fraction
        weights[1:] = (1 - majority_fraction) / (n_subpops - 1)

    # ── latent targets (one per subpop, orthogonal) ──
    targets = rng.standard_normal((n_subpops, dim)).astype(np.float32)
    if n_subpops <= dim:
        q, _ = np.linalg.qr(targets.T)
        targets = q[:, :n_subpops].T * np.sqrt(dim)
    else:
        targets = targets / np.linalg.norm(targets, axis=1, keepdims=True) * np.sqrt(dim)

    # ── candidate drug response centres: bias-continuum design ──
    #
    # Each drug d has a bias parameter b_d ∈ [-1, +1].
    #   b = 0    → balanced (symmetric across subpops)
    #   b = +1   → majority specialist (closer to target[0], farther from target[1+])
    #   b = -1   → minority specialist (mirror)
    #
    # The effective bias is b_d * conflict_level.  At conflict_level=0, ALL drugs
    # are balanced regardless of b_d.  At conflict_level=1, specialists are maximally
    # differentiated.
    #
    # The first n_structured drugs are evenly spaced on [-1, +1]; the rest are
    # distractors (random, far from targets).
    #
    # Design invariant: at conflict_level=1 and majority_fraction=0.7,
    #   - mean_welfare picks the majority specialist (alpha amplifies subpop-0 advantage)
    #   - worst_welfare picks a balanced drug (lowest worst-case loss)
    #   → oracle_flip_risk = 1.

    base_dist = 0.3 * np.sqrt(dim)
    n_distract = max(1, library_size // 5)
    n_structured = library_size - n_distract

    drug_ids = []
    response_centres = np.zeros((library_size, n_subpops, dim), dtype=np.float32)

    for i in range(n_structured):
        # Bias parameter: linear sweep from -1 to +1
        if n_structured > 1:
            bias_t = 2.0 * i / (n_structured - 1) - 1.0
        else:
            bias_t = 0.0

        eff_bias = bias_t * conflict_level

        # Shared random direction (ensures perfect symmetry at conflict=0)
        direction = rng.normal(0, 1, dim).astype(np.float32)
        direction /= np.linalg.norm(direction)

        for k in range(n_subpops):
            # For subpop 0 (majority): positive eff_bias → scale < 1 (closer to target)
            # For subpop 1+ (minority): positive eff_bias → scale > 1 (farther from target)
            if k == 0:
                scale = 1.0 - eff_bias * 0.5
            else:
                scale = 1.0 + eff_bias * 0.5
            response_centres[i, k] = targets[k] + direction * base_dist * scale

        # Name by role
        if bias_t > 0.3:
            drug_ids.append(f"maj_specialist_{i}")
        elif bias_t < -0.3:
            drug_ids.append(f"min_specialist_{i}")
        else:
            drug_ids.append(f"balanced_{i}")

    # Distractors: far from all targets
    for i in range(n_distract):
        idx = n_structured + i
        for k in range(n_subpops):
            response_centres[idx, k] = rng.normal(0, np.sqrt(dim) * 2, dim)
        drug_ids.append(f"distractor_{i}")

    assert len(drug_ids) == library_size

    # ── utility matrix u[d,k] = -E||x - t_k||^2 ──
    # E||x - t_k||^2 = ||c_dk - t_k||^2 + dim * sigma^2
    utility = np.zeros((library_size, n_subpops), dtype=np.float64)
    for d in range(library_size):
        for k in range(n_subpops):
            sq_dist = float(np.sum((response_centres[d, k] - targets[k]) ** 2))
            utility[d, k] = -(sq_dist + dim * noise_sigma ** 2)

    # ── generate actual cell populations ──
    candidate_pops = {}
    for d in range(library_size):
        cells_list = []
        for k in range(n_subpops):
            cells_k = response_centres[d, k] + rng.normal(0, noise_sigma, (cells_per_subpop, dim))
            cells_list.append(cells_k.astype(np.float32))
        candidate_pops[drug_ids[d]] = np.vstack(cells_list)

    # ── apply information condition ──
    if information_condition == "predicted_mean":
        for d_id in drug_ids:
            pop = candidate_pops[d_id]
            mean = pop.mean(axis=0)
            n = len(pop)
            candidate_pops[d_id] = (mean + rng.normal(0, noise_sigma, (n, dim))).astype(np.float32)
    elif information_condition == "predicted_structure":
        from sklearn.decomposition import PCA
        n_comp = max(2, dim // 5)
        for d_id in drug_ids:
            pop = candidate_pops[d_id]
            pca = PCA(n_components=min(n_comp, min(pop.shape) - 1), random_state=0)
            reduced = pca.fit_transform(pop)
            reconstructed = pca.inverse_transform(reduced)
            candidate_pops[d_id] = (reconstructed +
                                     rng.normal(0, noise_sigma * 0.3, pop.shape)).astype(np.float32)

    # ── query population ──
    query_cells = []
    query_labels = []
    for k in range(n_subpops):
        n_q = max(5, int(weights[k] * cells_per_subpop * n_subpops))
        q_k = targets[k] + rng.normal(0, noise_sigma * 0.8, (n_q, dim))
        query_cells.append(q_k.astype(np.float32))
        query_labels.append(np.full(n_q, k, dtype=np.int32))
    query_X = np.vstack(query_cells)
    query_lab = np.concatenate(query_labels)

    metadata = {
        "n_subpops": n_subpops, "dim": dim, "library_size": library_size,
        "majority_fraction": majority_fraction, "conflict_level": conflict_level,
        "cells_per_subpop": cells_per_subpop, "noise_sigma": noise_sigma,
        "information_condition": information_condition, "seed": seed,
        "n_structured": n_structured, "n_distract": n_distract,
    }

    return HIRCell(
        query_X=query_X, query_labels=query_lab,
        candidate_populations=candidate_pops, latent_targets=targets,
        true_weights=weights, utility_matrix=utility, drug_ids=drug_ids,
        metadata=metadata,
    )
