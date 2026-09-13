"""Stable public aliases for the retrieval score implementations."""

from retrieval.metrics import (
    DEFAULT_ESTIMATOR,
    available_scorers,
    energy_distance,
    energy_distance_u,
    energy_distance_v,
    mmd_rbf,
    mmd_rbf_u,
    mmd_rbf_v,
    score_coverage,
    score_energy,
    score_mean_cosine,
    score_mean_l2,
    score_mmd_rbf,
    score_sliced_wasserstein,
    sliced_wasserstein,
)

__all__ = [
    "DEFAULT_ESTIMATOR",
    "available_scorers",
    "energy_distance",
    "energy_distance_u",
    "energy_distance_v",
    "mmd_rbf",
    "mmd_rbf_u",
    "mmd_rbf_v",
    "score_coverage",
    "score_energy",
    "score_mean_cosine",
    "score_mean_l2",
    "score_mmd_rbf",
    "score_sliced_wasserstein",
    "sliced_wasserstein",
]

