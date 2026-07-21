"""Shared retrieval evaluation: score every query against the full drug library."""
from __future__ import annotations

from typing import Optional

import numpy as np
import torch

from .data.collate import collate_population
from .data.population_dataset import PopulationPairDataset
from .metrics.ranking import retrieval_metrics
from .training.drug_gallery import MatchingContext


@torch.no_grad()
def score_queries(
    model,
    data,
    ctx: MatchingContext,
    condition_keys: list[str],
    device: torch.device,
    n_source: int = 128,
    n_target: int = 128,
    query_batch: int = 32,
    n_repeats: int = 1,
    seed: int = 0,
) -> dict:
    """Return scores [Q, D], true library positions [Q], moa_same [Q, D], keys."""
    model.eval()
    ds = PopulationPairDataset(data, condition_keys, n_source, n_target,
                               deterministic=True, seed=seed)
    # base gallery once (dose applied per query)
    gallery_base = model.encode_all_drugs()["drug_proj"][ctx.candidate_indices]   # [D,128]

    all_scores, all_pos, keys = [], [], []
    for start in range(0, len(ds), query_batch):
        items = [ds[i] for i in range(start, min(start + query_batch, len(ds)))]
        batch = collate_population(items).to(device)
        acc = None
        for r in range(n_repeats):
            if r > 0:  # resample populations for a smoother estimate
                items_r = [PopulationPairDataset(data, [k], n_source, n_target,
                            deterministic=True, seed=seed + 100 * r + j)[0]
                           for j, k in enumerate(batch.condition_keys)]
                batch = collate_population(items_r).to(device)
            gap = model.encode_transition(batch)["gap_emb"]                       # [b,128]
            gallery_cond = model.gallery_cond(gallery_base, batch.log_dose)        # [b,D,128]
            s = (gap.unsqueeze(1) * gallery_cond).sum(-1)                          # [b,D]
            acc = s if acc is None else acc + s
        all_scores.append((acc / n_repeats).cpu().numpy())
        all_pos.append(ctx.lib_pos(batch.drug_idx).cpu().numpy())
        keys.extend(batch.condition_keys)

    scores = np.concatenate(all_scores, 0)
    true_pos = np.concatenate(all_pos, 0)
    moa_same = ctx.moa_lib[torch.as_tensor(
        [data.conditions[k].drug_idx for k in keys])].cpu().numpy()
    return {"scores": scores, "true_pos": true_pos, "moa_same": moa_same, "keys": keys}


def evaluate_retrieval(model, data, ctx, condition_keys, device, **kw) -> dict:
    r = score_queries(model, data, ctx, condition_keys, device, **kw)
    m = retrieval_metrics(r["scores"], r["true_pos"], r["moa_same"])
    return {"metrics": m, **r}
