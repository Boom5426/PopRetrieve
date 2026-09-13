"""Run a small, deterministic population-retrieval example.

This example uses synthetic cell populations only. It demonstrates the shared
candidate ranking interface and does not reproduce a biological result.
"""

from __future__ import annotations

import numpy as np

from popretrieve.metrics import score_energy, score_mean_cosine, score_mean_l2


def main() -> None:
    rng = np.random.default_rng(7)
    n_cells, n_features = 80, 8
    query = rng.normal(size=(n_cells, n_features)).astype(np.float32)

    candidates = {
        "population_match": query + rng.normal(scale=0.15, size=query.shape),
        "mean_match": np.broadcast_to(query.mean(axis=0), query.shape)
        + rng.normal(scale=0.35, size=query.shape),
        "distractor": rng.normal(loc=1.5, size=query.shape),
    }

    scorers = {
        "mean_cosine": lambda cells: score_mean_cosine(cells, query),
        "mean_l2": lambda cells: score_mean_l2(cells, query),
        "energy": lambda cells: score_energy(cells, query, max_cells=80, seed=7),
    }

    print(f"synthetic query: {n_cells} cells x {n_features} features")
    for scorer_name, scorer in scorers.items():
        scores = {name: float(scorer(cells)) for name, cells in candidates.items()}
        ranking = sorted(scores, key=scores.get, reverse=True)
        print(f"{scorer_name:>13}: {ranking}  scores={scores}")


if __name__ == "__main__":
    main()

