"""Public namespace for the PopRetrieve retrieval and evaluation package.

The implementation remains in the historical top-level packages used by the
paper scripts. This namespace provides a compact import surface without
duplicating any numerical code.
"""

__version__ = "0.1.0"

from .metrics import (
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
    "__version__",
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

