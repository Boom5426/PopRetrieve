"""Cross-fitted drug-by-state interaction, the replacement for Gate 1's ``1 - cos``.

WHY THE OLD STATISTIC HAD TO GO
-------------------------------
Gate 1 measured differential response as

    D = 1 - cos(r_1, r_2),      r_s = mean(treated in state s) - mean(vehicle in state s)

and on real material that is largely a signal-to-noise measure rather than a pharmacological one.
Measured over 3,620 Tahoe query conditions, D
correlates -0.584 with the response norm and -0.529 with the number of treated cells: when both
state responses are small, their angle is set by sampling noise, the cosine falls, and D rises. The
drugs that scored highest on "differential response" were systematically the weakest and least
reliably measured ones.

WHAT REPLACES IT
----------------
The quantity of interest is whether the drug's effect depends on the cell state, that is whether
the interaction vector

    I = r_1 - r_2

is non-zero. Its squared norm is not usable directly, for the same reason as before: sampling noise
alone produces a large ||I|| when the arms are small. So I is estimated twice, on disjoint halves of
every arm, and the two estimates are multiplied:

    S_int  = (1/p) * <I_A, I_B>                        primary: cross-fitted interaction strength
    S_main = (1/p) * <M_A, M_B>,  M = (r_1 + r_2)/2    the state-independent part, same construction
    share  = S_int / (S_int + S_main)                  scale-free: what fraction is state-dependent
    R_int  = cos(I_A, I_B)                             is the interaction reproducible at all?

Under the additive null the expectation of I is the zero vector, and because the two halves are
disjoint the estimates are independent, so E[S_int] = <E I_A, E I_B>/p = 0 exactly. Noise no longer
buys interaction: it makes I_A and I_B point in unrelated directions and their inner product
averages to zero. A real state-dependent effect survives, because both halves estimate the same
non-zero I.

All four arms are split, the vehicle arms included. Sharing one vehicle mean between the two halves
would put the same control noise into I_A and I_B and correlate them under the null, which is the
bias this construction exists to avoid.

Units: S_int is a squared expression difference per gene, so it grows with the size of the drug's
effect. That is correct for the question "how many expression units of this response depend on the
state", and it is the wrong scale for "how state-dependent is this drug relative to itself". The
second question is answered by ``interaction_share``, whose numerator and denominator are BOTH
cross-fitted, so neither is inflated by noise. Dividing by a plain response norm would put a
single-sample, noise-inflated quantity in the denominator, which is precisely the mechanism that
sank the old statistic, and is not done anywhere here.

To ask whether a given S_int is large in absolute terms, compare it against the permutation null
this module also provides, not against the response norm.
"""
from __future__ import annotations

from typing import Optional

import numpy as np

__all__ = ["interaction_halves", "cross_fitted_interaction", "permutation_null"]


def _halves(n: int, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    p = rng.permutation(n)
    h = n // 2
    return p[:h], p[h:]


def interaction_halves(t1: np.ndarray, t2: np.ndarray, c1: np.ndarray, c2: np.ndarray,
                       rng: np.random.Generator,
                       groups: Optional[tuple] = None) -> tuple[np.ndarray, np.ndarray]:
    """One cross-fitted pair (I_A, I_B) from the four arms.

    ``t1``/``t2`` are the treated cells in states 1 and 2, ``c1``/``c2`` the vehicle cells in the
    same two states, each as cells x genes.

    ``groups``, when given, is a 4-tuple of per-cell group labels (one array per arm). The split is
    then made over whole groups rather than over cells, which is how a library-preparation-disjoint
    split is requested. When it is None the split is a plain random half.

    Returns ``((I_A, I_B), (M_A, M_B))``: the interaction contrast r_1 - r_2 and the main effect
    (r_1 + r_2)/2, each estimated once per half. The main effect is returned because the only
    scale-free way to ask "how much of this drug's response is state-dependent" is to divide one
    cross-fitted quantity by another; dividing by a single-sample response norm is what
    reintroduced the effect-size confound into the old statistic.
    """
    arms = (t1, t2, c1, c2)
    means = []
    for k, X in enumerate(arms):
        if len(X) < 4:
            raise ValueError(f"arm {k} has {len(X)} cells; a cross-fitted split needs at least 4")
        if groups is None:
            ia, ib = _halves(len(X), rng)
        else:
            g = np.asarray(groups[k])
            uniq = np.unique(g)
            if len(uniq) < 2:
                ia, ib = _halves(len(X), rng)
            else:
                ga, _ = _halves(len(uniq), rng)
                mask = np.isin(g, uniq[ga])
                ia, ib = np.flatnonzero(mask), np.flatnonzero(~mask)
                if len(ia) < 2 or len(ib) < 2:
                    ia, ib = _halves(len(X), rng)
        means.append((X[ia].mean(0), X[ib].mean(0)))
    (t1a, t1b), (t2a, t2b), (c1a, c1b), (c2a, c2b) = means
    r1a, r1b = t1a - c1a, t1b - c1b
    r2a, r2b = t2a - c2a, t2b - c2b
    return (r1a - r2a, r1b - r2b), ((r1a + r2a) / 2.0, (r1b + r2b) / 2.0)


def cross_fitted_interaction(t1: np.ndarray, t2: np.ndarray, c1: np.ndarray, c2: np.ndarray,
                             n_repeats: int = 10, seed: int = 0,
                             groups: Optional[tuple] = None) -> dict:
    """S_int and R_int, averaged over ``n_repeats`` independent A/B splits.

    Averaging over splits removes the arbitrariness of any one split without changing the
    expectation: each repeat is individually unbiased under the additive null.

    Returns S_int, R_int, their standard errors across repeats, and the mean per-half interaction
    norms, which are reported because a large S_int built from two enormous and barely-aligned
    vectors means something different from a small one built from two well-aligned ones.
    """
    rng = np.random.default_rng(seed)
    s, r, m, na = [], [], [], []
    for _ in range(n_repeats):
        (ia, ib), (ma, mb) = interaction_halves(t1, t2, c1, c2, rng, groups=groups)
        p = ia.shape[0]
        s.append(float(ia @ ib) / p)
        m.append(float(ma @ mb) / p)
        n1, n2 = float(np.linalg.norm(ia)), float(np.linalg.norm(ib))
        r.append(0.0 if n1 < 1e-12 or n2 < 1e-12 else float(ia @ ib) / (n1 * n2))
        na.extend([n1, n2])
    s_int, s_main = float(np.mean(s)), float(np.mean(m))
    total = s_int + s_main
    # The share is defined only where the cross-fitted total response energy is positive. Both
    # terms are unbiased, so either can come out negative on a drug with no detectable effect at
    # all, and a ratio built on that is meaningless rather than merely noisy. It is left undefined
    # there instead of being clipped into a plausible-looking number.
    share = s_int / total if total > 0 else float("nan")
    return {
        "S_int": s_int,
        "S_int_se": float(np.std(s, ddof=1) / np.sqrt(len(s))) if len(s) > 1 else float("nan"),
        "S_main": s_main,
        "interaction_share": share,
        "R_int": float(np.mean(r)),
        "R_int_se": float(np.std(r, ddof=1) / np.sqrt(len(r))) if len(r) > 1 else float("nan"),
        "half_norm_mean": float(np.mean(na)),
        "n_repeats": len(s),
    }


def permutation_null(t1: np.ndarray, t2: np.ndarray, c1: np.ndarray, c2: np.ndarray,
                     n_perm: int = 20, n_repeats: int = 4, seed: int = 0) -> dict:
    """Null distribution of S_int under state-label permutation.

    The state labels are shuffled within the treated cells and within the vehicle cells
    separately, which destroys any drug-by-state interaction while leaving the drug's main effect,
    the state's main effect and every sample size untouched. That is the null Gate 1 needs: not
    "no drug effect" but "the drug effect does not depend on the state".

    Returns the null mean and standard deviation, the observed value, a z-score and a two-sided
    empirical p-value. The p-value's resolution is 1/(n_perm+1), so it is a screening quantity, not
    a publication-grade significance.
    """
    obs = cross_fitted_interaction(t1, t2, c1, c2, n_repeats=n_repeats, seed=seed)["S_int"]
    rng = np.random.default_rng(seed + 1)
    T = np.concatenate([t1, t2], 0)
    C = np.concatenate([c1, c2], 0)
    nt1, nc1 = len(t1), len(c1)
    vals = []
    for i in range(n_perm):
        pt, pc = rng.permutation(len(T)), rng.permutation(len(C))
        vals.append(cross_fitted_interaction(T[pt[:nt1]], T[pt[nt1:]], C[pc[:nc1]], C[pc[nc1:]],
                                             n_repeats=n_repeats, seed=seed + 100 + i)["S_int"])
    vals = np.asarray(vals)
    sd = float(vals.std(ddof=1)) if len(vals) > 1 else float("nan")
    return {
        "S_int": obs,
        "null_mean": float(vals.mean()),
        "null_sd": sd,
        "z": float((obs - vals.mean()) / sd) if sd and sd > 0 else float("nan"),
        "p_two_sided": float((np.sum(np.abs(vals - vals.mean()) >= abs(obs - vals.mean())) + 1)
                             / (len(vals) + 1)),
        "n_perm": len(vals),
    }
