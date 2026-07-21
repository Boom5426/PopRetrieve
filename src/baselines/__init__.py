"""External baselines for the Phase-2 paper-level comparison.

Signature / latent retrieval rankers and predict-then-rank predictors, all speaking the
normalized-query interface in :mod:`baselines.base`.  Import submodules directly, e.g.::

    from baselines.cmap_signature import CMapSignatureRetrieval
    from baselines.pca_latent_retrieval import PCALatentRetrieval
    from baselines.average_effect_predictor import AverageEffectPredictor
    from baselines.nearest_neighbor_predictor import NearestNeighborPredictor
    from baselines.pdgrapher_adapter import PDGrapherAdapter
"""
from .base import (
    Candidate, NormalizedQuery, Predictor, Ranker,
    cosine, normalize_query, scores_to_vector,
)

__all__ = [
    "Candidate", "NormalizedQuery", "Predictor", "Ranker",
    "cosine", "normalize_query", "scores_to_vector",
]
