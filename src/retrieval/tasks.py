"""Retrieval task builders (unified from the original scattered scripts).

Three near-identical alpha-mixture builders in the old code collapse to two classes:

* ``ControlledMixtureTask``   — SciPlex3 two-MOA (HDAC vs JAK) controlled mixture
  (ports ``build_mixture_queries.MixtureBuilder``); also exposes the build/cand
  halves used by the divergence + power sweeps.
* ``ContextMixtureTask``      — two-context mixture where the divergent modes are two
  real biological contexts under the SAME perturbation (ports both
  ``CrossLineBuilder`` [context=cell line] and ``FrangiehBuilder`` [context=immune
  condition] — they were line-for-line identical).

Plus shared, de-duplicated helpers: ``split_half_reliability`` (was copied 4x),
``context_divergence_probe`` (crossline / frangieh divergence probes), and
``NaturalSubpops`` (PCA+KMeans natural-subpopulation assignment, copied 4x for CD34).

Query dicts keep the EXACT field names of the originals so the scorers in
``rankers.py`` are a 1:1 port and the reproduction matches FINDINGS.
"""
from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd

from data.population import Dataset


def _cos(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return 0.0 if na < 1e-12 or nb < 1e-12 else float(a @ b / (na * nb))


def split_half_reliability(X: np.ndarray, rows: np.ndarray, ctrl_mean: np.ndarray,
                           rng: np.random.Generator, n_rep: int = 5) -> float:
    """Mean cos between two disjoint-half response directions (within-context noise
    floor). Unifies the 4 copies in crossline/frangieh divergence + cd34 robustness."""
    if len(rows) < 8:
        return float("nan")
    vals = []
    for _ in range(n_rep):
        p = rng.permutation(rows)
        h = len(p) // 2
        d1 = X[p[:h]].mean(0) - ctrl_mean
        d2 = X[p[h:]].mean(0) - ctrl_mean
        vals.append(_cos(d1, d2))
    return float(np.mean(vals))


# ---------------------------------------------------------------------------
# Controlled two-MOA mixture (SciPlex3), ports MixtureBuilder
# ---------------------------------------------------------------------------


class ControlledMixtureTask:
    def __init__(self, data: Dataset, cell_line: str = "K562", class_a: str = "HDAC",
                 class_b: str = "JAK", label_col: str = "target",
                 dose: Optional[float] = 10000.0, n_total: int = 400, seed: int = 0):
        self.data = data
        self.X = data.X
        obs = data.obs
        self.n_total = n_total
        self.rng = np.random.default_rng(seed)
        self.cell_line, self.class_a, self.class_b = cell_line, class_a, class_b

        lab = obs[label_col].astype(str).str.strip()
        line = obs["cell_line"].astype(str)
        dv = obs["dose_value"].astype(float)
        is_ctrl = data.is_control
        base = (line == cell_line).to_numpy()
        if dose is not None and (dv == dose).any():
            base = base & (dv == dose).to_numpy()

        self.rows_a = np.flatnonzero(base & (lab == class_a).to_numpy() & ~is_ctrl)
        self.rows_b = np.flatnonzero(base & (lab == class_b).to_numpy() & ~is_ctrl)
        if len(self.rows_a) < 40 or len(self.rows_b) < 40:
            raise ValueError(f"too few cells: {class_a}={len(self.rows_a)} "
                             f"{class_b}={len(self.rows_b)} in {cell_line}@{dose}")

        cr = data.control_rows(cell_line)
        self.pseudo_control = (self.X[cr].mean(0) if len(cr)
                               else self.X.mean(0)).astype(np.float32)

        self._a_build, self._a_cand = self._halve(self.rows_a)
        self._b_build, self._b_cand = self._halve(self.rows_b)
        self.distractor_rows = self._distractors(base & ~is_ctrl, lab, obs, {class_a, class_b})

    def _halve(self, rows):
        r = self.rng.permutation(rows)
        h = len(r) // 2
        return r[:h], r[h:]

    def _distractors(self, base_mask, lab, obs, exclude):
        pert = obs["perturbation"].astype(str).str.strip()
        out = {}
        for name in pert[base_mask].unique():
            if lab[pert == name].iloc[0] in exclude:
                continue
            rows = np.flatnonzero(base_mask & (pert == name).to_numpy())
            if len(rows) >= 20:
                out[name] = rows
        return out

    def _sample(self, rows, n, rng):
        return rng.choice(rows, n, replace=len(rows) < n)

    def build(self, alpha: float, n_distractors: int = 40, seed: Optional[int] = None):
        rng = self.rng if seed is None else np.random.default_rng(seed)
        n_maj = int(round(alpha * self.n_total))
        n_min = self.n_total - n_maj

        def mix(a_pool, b_pool, r):
            ra = self._sample(a_pool, n_maj, r)
            rb = self._sample(b_pool, n_min, r)
            X = np.concatenate([self.X[ra], self.X[rb]], 0)
            lab = np.concatenate([np.zeros(n_maj, int), np.ones(n_min, int)])
            return X.astype(np.float32), lab

        target, target_lab = mix(self._a_build, self._b_build, rng)
        covers_both, _ = mix(self._a_cand, self._b_cand, rng)
        majority = self.X[self._sample(self._a_cand, self.n_total, rng)].astype(np.float32)
        minority = self.X[self._sample(self._b_cand, self.n_total, rng)].astype(np.float32)

        cands = {"covers-both": covers_both, "majority-only": majority,
                 "minority-only": minority}
        names = list(self.distractor_rows)
        rng.shuffle(names)
        for name in names[:n_distractors]:
            cands[f"distractor:{name}"] = self.X[
                self._sample(self.distractor_rows[name], self.n_total, rng)].astype(np.float32)

        return {"alpha": alpha, "target": target, "target_labels": target_lab,
                "candidates": cands, "ground_truth": "covers-both",
                "pseudo_control": self.pseudo_control,
                "class_a": self.class_a, "class_b": self.class_b,
                "cell_line": self.cell_line}


def subsample_controlled_query(q: dict, N: int, seed: int) -> dict:
    """Power-axis subsample: keep N cells/subpop in target, 2N/candidate (ports
    eval_power_sweep.subsample)."""
    r = np.random.default_rng(seed)
    lab = q["target_labels"]
    T = q["target"]
    keep = []
    for c in (0, 1):
        idx = np.where(lab == c)[0]
        keep.append(r.choice(idx, min(N, len(idx)), replace=False))
    keep = np.concatenate(keep)
    q2 = dict(q)
    q2["target"] = T[keep]
    q2["target_labels"] = lab[keep]
    q2["candidates"] = {name: P[r.choice(len(P), min(2 * N, len(P)), replace=False)]
                        for name, P in q["candidates"].items()}
    return q2


def build_divergence_query(task: ControlledMixtureTask, lam: float, alpha: float,
                           ntot: int, n_distractors: int, seed: int) -> tuple[dict, float]:
    """Divergence-axis query: minority = majority(class-A) shifted by lam*(mu_B-mu_A),
    so lam=0 -> identical subpops, lam>=1 -> orthogonal (ports eval_divergence_sweep /
    eval_metric_robustness build_q). Returns (query, subpop_cos)."""
    X = task.X
    a_build, a_cand, b_build = task._a_build, task._a_cand, task._b_build
    ctrl = task.pseudo_control
    mu_a = X[a_build].mean(0)
    v = (X[b_build].mean(0) - mu_a).astype(np.float32)
    n_maj = int(round(alpha * ntot))
    n_min = ntot - n_maj
    dist_names = list(task.distractor_rows)

    r = np.random.default_rng(seed)

    def pick(rows, n, rr):
        return X[rr.choice(rows, n, replace=len(rows) < n)]

    maj_t = pick(a_build, n_maj, r)
    min_t = pick(a_build, n_min, r) + lam * v
    target = np.concatenate([maj_t, min_t]).astype(np.float32)
    lab = np.concatenate([np.zeros(n_maj, int), np.ones(n_min, int)])
    cb = np.concatenate([pick(a_cand, n_maj, r),
                         pick(a_cand, n_min, r) + lam * v]).astype(np.float32)
    cands = {"covers-both": cb,
             "majority-only": pick(a_cand, ntot, r).astype(np.float32),
             "minority-only": (pick(a_cand, ntot, r) + lam * v).astype(np.float32)}
    r.shuffle(dist_names)
    for nm in dist_names[:n_distractors]:
        cands[f"distractor:{nm}"] = pick(task.distractor_rows[nm], ntot, r).astype(np.float32)

    subpop_cos = _cos(mu_a - ctrl, (mu_a + lam * v) - ctrl)
    q = {"target": target, "target_labels": lab, "pseudo_control": ctrl,
         "candidates": cands}
    return q, subpop_cos


# ---------------------------------------------------------------------------
# Two-context mixture (cross-line OR frangieh), ports CrossLineBuilder/FrangiehBuilder
# ---------------------------------------------------------------------------


class ContextMixtureTask:
    """Heterogeneous mixture whose two divergent modes are two real biological
    CONTEXTS (cell lines, or immune conditions) under the SAME perturbation."""

    def __init__(self, data: Dataset, ctx_maj: str, ctx_min: str,
                 min_cells: int = 60, seed: int = 0):
        self.data = data
        self.X = data.X
        self.rng = np.random.default_rng(seed)
        self.ctx_maj, self.ctx_min = ctx_maj, ctx_min

        ctx = data.context
        pert = data.pert
        is_ctrl = data.is_control

        self.ctrl_mean = {L: data.control_mean(L) for L in (ctx_maj, ctx_min)}
        self.pool = {ctx_maj: {}, ctx_min: {}}
        for L in (ctx_maj, ctx_min):
            m = (ctx == L) & ~is_ctrl
            idx = np.flatnonzero(m)
            g = pert[m]
            for name in pd.unique(g):
                r = idx[g == name]
                if len(r) >= min_cells:
                    p = self.rng.permutation(r)
                    h = len(p) // 2
                    self.pool[L][name] = (p[:h], p[h:])   # (build, cand)
        self.shared = sorted(set(self.pool[ctx_maj]) & set(self.pool[ctx_min]))

    def _samp(self, rows, n, r):
        return self.X[r.choice(rows, n, replace=len(rows) < n)].astype(np.float32)

    def build(self, pert_star: str, alpha: float, n_total: int, distractors: int,
              seed: int) -> dict:
        r = np.random.default_rng(seed)
        n_maj = int(round(alpha * n_total))
        n_min = n_total - n_maj
        Lp, Lm = self.ctx_maj, self.ctx_min
        cmix = (alpha * self.ctrl_mean[Lp] + (1 - alpha) * self.ctrl_mean[Lm]).astype(np.float32)

        def mix(pname, half):  # half: 0=build, 1=cand
            a = self._samp(self.pool[Lp][pname][half], n_maj, r)
            b = self._samp(self.pool[Lm][pname][half], n_min, r)
            X = np.concatenate([a, b], 0)
            lab = np.concatenate([np.zeros(n_maj, int), np.ones(n_min, int)])
            return X, lab

        target, tlab = mix(pert_star, 0)
        cb, cblab = mix(pert_star, 1)
        maj = self._samp(self.pool[Lp][pert_star][1], n_total, r)
        mino = self._samp(self.pool[Lm][pert_star][1], n_total, r)
        cands = {
            "covers-both": (cb, cblab, cmix),
            "majority-only": (maj, np.zeros(n_total, int), self.ctrl_mean[Lp]),
            "minority-only": (mino, np.ones(n_total, int), self.ctrl_mean[Lm]),
        }
        pool = [d for d in self.shared if d != pert_star]
        r.shuffle(pool)
        for d in pool[:distractors]:
            X, lab = mix(d, 1)
            cands[f"distractor:{d}"] = (X, lab, cmix)
        return {"target": target, "tlab": tlab, "ctrl_T": cmix, "cands": cands}

    def divergent(self, div_df: pd.DataFrame, n: int, min_cells_pool: int,
                  id_col: str = "drug") -> list[str]:
        """Pick divergent, reliable, gate-clearing perturbations with enough cells,
        most-divergent first (ports CrossLineBuilder.divergent_drugs / divergent_kos)."""
        ok = [d for d in self.shared
              if min(len(self.pool[self.ctx_maj][d][0]),
                     len(self.pool[self.ctx_min][d][0])) >= min_cells_pool // 2]
        if div_df is None or len(div_df) == 0:
            return ok[:n]
        df = div_df
        gate = df.get("clears_gate", df["cross_cos"] < 0.9)
        df = df[gate & df[id_col].isin(ok)]
        return df.sort_values("cross_cos")[id_col].head(n).tolist()


# ---------------------------------------------------------------------------
# Context-divergence probe (model-free), ports crossline_divergence / frangieh_divergence
# ---------------------------------------------------------------------------


def context_divergence_probe(data: Dataset, ctx_a: str, ctx_b: str, min_cells: int = 30,
                             gate: float = 0.9, rel_floor: float = 0.5, seed: int = 0,
                             id_col: str = "drug") -> pd.DataFrame:
    """Per-perturbation cross-context response-divergence probe with a within-context
    split-half reliability floor (the CD34 lesson: don't call sampling noise
    divergence). Returns a DataFrame sorted by ``cross_cos`` with a ``clears_gate``
    flag, matching the schema the mixture task's ``divergent`` reader expects."""
    X = data.X
    ctx = data.context
    pert = data.pert
    is_ctrl = data.is_control
    rng = np.random.default_rng(seed)

    ctrl = {L: data.control_mean(L) for L in (ctx_a, ctx_b)}

    def context_pert_rows(L):
        m = (ctx == L) & ~is_ctrl
        idx = np.flatnonzero(m)
        d = pert[m]
        return {name: idx[d == name] for name in pd.unique(d)
                if len(idx[d == name]) >= min_cells}

    rows_a, rows_b = context_pert_rows(ctx_a), context_pert_rows(ctx_b)
    shared = sorted(set(rows_a) & set(rows_b))

    recs = []
    for name in shared:
        ra, rb = rows_a[name], rows_b[name]
        dA = X[ra].mean(0) - ctrl[ctx_a]
        dB = X[rb].mean(0) - ctrl[ctx_b]
        recs.append({
            id_col: name, "n_a": len(ra), "n_b": len(rb),
            "eff_a": float(np.linalg.norm(dA)), "eff_b": float(np.linalg.norm(dB)),
            "cross_cos": _cos(dA, dB),
            "rel_a": split_half_reliability(X, ra, ctrl[ctx_a], rng),
            "rel_b": split_half_reliability(X, rb, ctrl[ctx_b], rng),
        })
    df = pd.DataFrame(recs)
    if len(df):
        df["reliable"] = (df["rel_a"] >= rel_floor) & (df["rel_b"] >= rel_floor)
        df["clears_gate"] = df["reliable"] & (df["cross_cos"] < gate)
        df = df.sort_values("cross_cos").reset_index(drop=True)
    return df


# ---------------------------------------------------------------------------
# Natural subpopulations (unsupervised), ports the CD34 PCA+KMeans assignment
# ---------------------------------------------------------------------------


class NaturalSubpops:
    """PCA(30)+KMeans(K) subpopulations fit on control cells; nearest-centroid
    assignment for any population. Ports the 4 CD34 copies."""

    def __init__(self, control_X: np.ndarray, K: int = 4, random_state: int = 0):
        from sklearn.cluster import KMeans
        from sklearn.decomposition import PCA
        self.K = K
        self.pca = PCA(30, random_state=random_state).fit(control_X)
        Z = self.pca.transform(control_X)
        self.km = KMeans(K, n_init=10, random_state=random_state).fit(Z)
        self.centroids = self.km.cluster_centers_
        self.control_labels = self.km.labels_
        self.fractions = np.bincount(self.control_labels, minlength=K) / len(self.control_labels)

    def assign(self, P: np.ndarray) -> np.ndarray:
        Z = self.pca.transform(P)
        return ((Z[:, None, :] - self.centroids[None]) ** 2).sum(-1).argmin(1)
