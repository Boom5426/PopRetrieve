"""Shared machinery for the Phase-II transition-to-intervention retrieval experiments.

Phase A (oracle response bank) and Phase B (leave-one-cell-line-out prediction) must be paired
cell for cell: they differ only in where a candidate's response comes from, so the source cells,
the sublibrary split and the query cells have to be identical in both. That is what the seeded
generators here guarantee. Each draw gets its own generator keyed by its purpose, so adding or
removing a draw in one phase cannot shift the stream that feeds another.

Everything else in this module is the scoring layer, held in one place so the two phases cannot
drift apart in how a ranking is computed.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import scipy.sparse as sp

# ---- frozen constants, see docs/phase2/01_TRANSITION_TASK_FREEZE.md ----
CONTROL_DRUG = "DMSO_TF"
N_SOURCE = 200
N_TARGET = 200
N_BANK = 100            # Phase A oracle bank; Phase B predicts N_SOURCE cells instead
SEEDS = (13, 29, 47, 71, 101)
SW_N_PROJ = 200
SW_N_QUANTILE = 100
N_BOOTSTRAP = 2000
SCORERS = ("mean_cosine", "mean_l2", "energy", "energy_v_statistic", "mmd", "sliced_wasserstein")
REFERENCES = ("mean_cosine", "mean_l2")

# Purpose tags for the generators. The integers are arbitrary and only have to be distinct.
RNG_SPLIT, RNG_SOURCE, RNG_BANK, RNG_TARGET, RNG_FIT = 1, 2, 3, 4, 5


def rng_for(purpose: int, seed: int, ctx_index: int, extra: int = 0) -> np.random.Generator:
    """A generator keyed by (purpose, seed, context, extra).

    Keying by purpose rather than by call order is what makes Phase A and Phase B draw the same
    source cells and the same query cells despite doing different amounts of sampling in between.
    """
    return np.random.default_rng([purpose, seed, ctx_index, extra])


def sublibrary_halves(n_sublibs: int, seed: int, ctx_index: int) -> np.ndarray:
    """Boolean mask over sublibraries: True = half H1 (queries), False = half H2 (oracle banks)."""
    r = rng_for(RNG_SPLIT, seed, ctx_index)
    perm = r.permutation(n_sublibs)
    h1 = np.zeros(n_sublibs, dtype=bool)
    h1[perm[: n_sublibs // 2]] = True
    return h1


def group_means(X: sp.csr_matrix, keys: pd.Series) -> tuple[pd.Index, np.ndarray, np.ndarray]:
    """Exact mean expression vector per group, via one sparse matmul with a row indicator.

    Ported from analysis/tahoe_pilot/tahoe_gate_pilot.py so the two use the same arithmetic.
    """
    cat = pd.Categorical(keys)
    codes = cat.codes
    if (codes < 0).any():
        raise ValueError("group key has NaN/unmapped entries; refusing to compute means")
    n_groups = len(cat.categories)
    counts = np.bincount(codes, minlength=n_groups).astype(np.float64)
    if (counts == 0).any():
        raise ValueError("empty group encountered")
    ind = sp.csr_matrix((np.ones(len(codes), dtype=np.float32), (codes, np.arange(len(codes)))),
                        shape=(n_groups, X.shape[0]))
    means = np.asarray((ind @ X).todense(), dtype=np.float64) / counts[:, None]
    return cat.categories, means, counts.astype(int)


# ---------------------------------------------------------------------------
# Scoring.
#
# One query population against a whole candidate library at once. Everything that depends only on
# the library is computed once in ``BankCache``; the per-query work is the cross terms alone.
#
# Two estimator conventions are reported for the energy distance:
#   energy               U-statistic, self-pairs excluded, unbiased at any sample size
#   energy_v_statistic   V-statistic, self-pairs included: the convention of
#                        src/retrieval/metrics.py and therefore of the manuscript. It carries an
#                        O(1/m) upward bias, harmless at equal sizes and a ranking artefact
#                        otherwise.
# ---------------------------------------------------------------------------


def pairwise_sqdist(A, B):
    """Squared Euclidean distances, clamped at zero against round-off."""
    d = (A * A).sum(1)[:, None] + (B * B).sum(1)[None, :] - 2.0 * (A @ B.T)
    return d.clamp_min_(0.0)


def _offdiag_sum(M):
    """Sum of a square matrix excluding its diagonal, accumulated in float64."""
    return M.double().sum() - M.double().diagonal().sum()


class BankCache:
    """Everything about a candidate library that does not depend on the query."""

    def __init__(self, B, sizes, gamma, dirs, qs, torch):
        self.B = B
        self.sizes = np.asarray(sizes, dtype=np.int64)
        self.gamma = gamma
        self.dirs = dirs
        self.qs = qs
        n_c = len(sizes)
        dev = B.device
        offs = np.concatenate([[0], np.cumsum(self.sizes)])
        self.seg = torch.as_tensor(np.repeat(np.arange(n_c), self.sizes), device=dev,
                                   dtype=torch.long)
        self.m = torch.as_tensor(self.sizes, device=dev, dtype=torch.float64)

        self.mean_b = torch.stack([B[offs[k]:offs[k + 1]].mean(0) for k in range(n_c)])
        self.mean_b_norm = self.mean_b.norm(dim=1)

        within_d = torch.empty(n_c, dtype=torch.float64, device=dev)
        within_k = torch.empty(n_c, dtype=torch.float64, device=dev)
        qb = []
        for k in range(n_c):
            Y = B[offs[k]:offs[k + 1]]
            d2 = pairwise_sqdist(Y, Y)
            within_d[k] = _offdiag_sum(d2.sqrt())
            within_k[k] = _offdiag_sum(torch.exp(-gamma * d2))
            qb.append(torch.quantile(Y @ dirs, qs, dim=0))
        self.qb = torch.stack(qb)
        self.term_y_u = within_d / (self.m * (self.m - 1))
        self.term_y_v = within_d / (self.m * self.m)
        self.k_yy_u = within_k / (self.m * (self.m - 1))


def score_all(T, cache, torch) -> dict[str, np.ndarray]:
    """Scorer name -> score over the candidates. Higher is better for every entry."""
    n = T.shape[0]
    m = cache.m

    d2_tt = pairwise_sqdist(T, T)
    within_t = _offdiag_sum(d2_tt.sqrt())
    term_t_u = within_t / (n * (n - 1))
    term_t_v = within_t / (n * n)
    k_tt_u = _offdiag_sum(torch.exp(-cache.gamma * d2_tt)) / (n * (n - 1))

    d2_tb = pairwise_sqdist(T, cache.B)
    cross_d = torch.zeros(len(cache.sizes), dtype=torch.float64, device=T.device)
    cross_d.index_add_(0, cache.seg, d2_tb.sqrt().sum(0).double())
    cross_k = torch.zeros(len(cache.sizes), dtype=torch.float64, device=T.device)
    cross_k.index_add_(0, cache.seg, torch.exp(-cache.gamma * d2_tb).sum(0).double())

    energy_u = 2.0 * cross_d / (n * m) - term_t_u - cache.term_y_u
    energy_v = 2.0 * cross_d / (n * m) - term_t_v - cache.term_y_v
    mmd_u = k_tt_u + cache.k_yy_u - 2.0 * cross_k / (n * m)

    mean_t = T.mean(0)
    cos = (cache.mean_b @ mean_t) / (cache.mean_b_norm * mean_t.norm() + 1e-12)
    # Diagnostic, not a route: the same mean signatures compared by Euclidean distance. Cosine
    # discards response magnitude and the energy distance does not, so a magnitude effect
    # masquerading as a population effect reappears here, in a scorer that keeps only the mean.
    l2 = (cache.mean_b - mean_t[None]).norm(dim=1)

    qt = torch.quantile(T @ cache.dirs, cache.qs, dim=0)
    sw = (cache.qb - qt[None]).abs().mean(dim=(1, 2)).double()

    return {
        "mean_cosine": cos.double().cpu().numpy(),
        "mean_l2": (-l2).double().cpu().numpy(),
        "energy": (-energy_u).cpu().numpy(),
        "energy_v_statistic": (-energy_v).cpu().numpy(),
        "mmd": (-mmd_u).cpu().numpy(),
        "sliced_wasserstein": (-sw).cpu().numpy(),
    }


def make_cache(B_np, sizes, ctx_index, seed, torch, dev):
    """Move a stacked candidate library to the device and precompute its query-independent parts.

    The Gaussian bandwidth is the median heuristic taken on this library alone, once, and then
    held fixed for every query scored against it, so the kernel cannot vary with the query it is
    being used to score.
    """
    Bt = B_np if torch.is_tensor(B_np) else torch.as_tensor(B_np, device=dev)
    if min(sizes) < 2:
        raise ValueError(f"a candidate library entry has {min(sizes)} cells; it cannot be scored")
    r = rng_for(RNG_FIT, seed, ctx_index)
    sub = Bt[torch.as_tensor(r.choice(len(Bt), min(2000, len(Bt)), replace=False), device=dev)]
    med = pairwise_sqdist(sub, sub).sqrt_().median()
    gamma = 1.0 / (2.0 * (med.double() ** 2 + 1e-12))
    gen = torch.Generator(device=dev).manual_seed(int(seed) * 100003 + ctx_index)
    dirs = torch.randn(Bt.shape[1], SW_N_PROJ, device=dev, generator=gen)
    dirs = dirs / dirs.norm(dim=0, keepdim=True)
    qs = torch.linspace(0.0, 1.0, SW_N_QUANTILE, device=dev, dtype=Bt.dtype)
    return BankCache(Bt, sizes, gamma, dirs, qs, torch)


def rank_of(scores: np.ndarray, gt_index: int) -> tuple[float, int]:
    """Rank of the ground truth under 'higher score is better', ties averaged.

    Ties are split rather than resolved in either direction: resolving them in favour of the
    ground truth would flatter any scorer that produces them, and against it would punish them.
    """
    s = scores[gt_index]
    better = int((scores > s).sum())
    tied = int((scores == s).sum()) - 1
    return 1.0 + better + tied / 2.0, tied


def cluster_bootstrap(df: pd.DataFrame, value_col: str, cluster_col: str,
                      n_boot: int = N_BOOTSTRAP, seed: int = SEEDS[0]) -> tuple[float, float]:
    """Percentile CI resampling whole contexts, because queries inside one context share a source
    population and an entire candidate library and are therefore not independent."""
    rng = np.random.default_rng(seed)
    groups = [g[value_col].to_numpy() for _, g in df.groupby(cluster_col, sort=True)]
    k = len(groups)
    stats = np.empty(n_boot)
    for b in range(n_boot):
        stats[b] = np.concatenate([groups[i] for i in rng.integers(0, k, k)]).mean()
    return float(np.percentile(stats, 2.5)), float(np.percentile(stats, 97.5))


def summarize(per_query: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    """MRR / Hit@k with a context-clustered bootstrap, per group."""
    rows = []
    for keys, d in per_query.groupby(group_cols, sort=True):
        keys = keys if isinstance(keys, tuple) else (keys,)
        rec = dict(zip(group_cols, keys))
        rec.update({"n_query_seed": len(d),
                    "n_queries": d.groupby(["cell_line", "drug"]).ngroups,
                    "n_contexts": d.cell_line.nunique()})
        for col, name in (("reciprocal_rank", "MRR"), ("hit@1", "Hit@1"),
                          ("hit@5", "Hit@5"), ("hit@10", "Hit@10")):
            rec[name] = float(d[col].mean())
            rec[f"{name}_lo"], rec[f"{name}_hi"] = cluster_bootstrap(d, col, "cell_line")
        rec["median_rank"] = float(d["rank"].median())
        rows.append(rec)
    return pd.DataFrame(rows)


def paired_deltas(per_query: pd.DataFrame, extra_keys: list[str]) -> pd.DataFrame:
    """Paired difference of every scorer against each reference scorer, on identical rankings."""
    key = ["cell_line", "drug", "seed"] + extra_keys
    rows = []
    for ref_name in REFERENCES:
        ref = per_query[per_query.scorer == ref_name].set_index(key)
        for name in SCORERS:
            if name == ref_name:
                continue
            cur = per_query[per_query.scorer == name].set_index(key)
            j = cur.join(ref, rsuffix="_ref", how="inner").reset_index()
            if not len(j):
                continue
            rec = {"scorer": name, "reference": ref_name, "n_paired": len(j)}
            for c in extra_keys:
                rec[c] = j[c].iloc[0] if j[c].nunique() == 1 else "mixed"
            for col, out_name in (("reciprocal_rank", "dMRR"), ("hit@1", "dHit@1"),
                                  ("hit@5", "dHit@5"), ("hit@10", "dHit@10")):
                j["_d"] = j[col] - j[f"{col}_ref"]
                rec[out_name] = float(j["_d"].mean())
                rec[f"{out_name}_lo"], rec[f"{out_name}_hi"] = cluster_bootstrap(j, "_d", "cell_line")
            j["_dr"] = j["rank_ref"] - j["rank"]
            rec["mean_delta_rank"] = float(j["_dr"].mean())
            rec["frac_delta_rank_positive"] = float((j["_dr"] > 0).mean())
            rec["frac_delta_rank_zero"] = float((j["_dr"] == 0).mean())
            rows.append(rec)
    return pd.DataFrame(rows)
