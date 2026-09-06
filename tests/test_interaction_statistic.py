"""Sanity checks for the cross-fitted drug-by-state interaction, before it is used on real data.

Plan Phase 3.4 fixes five checks that must pass before the statistic is correlated with anything.
Three of them are synthetic and live here; the two that need real material (a constructed-mixture
positive control, and the effect-size audit) are in
analysis/phase2_transition/gate1_interaction.py and reported in
docs/phase2/P3_INTERACTION_STATISTIC.md.

Check 1  additive null:            an effect added identically to every cell gives S_int ~ 0
Check 2  state-label permutation:  shuffling the state labels returns S_int to its null
Check 4  cell-count sensitivity:   S_int must not drift with the number of cells

The old statistic, 1 - cos(r_1, r_2), is computed alongside in check 4 so the contrast is visible
in the test output rather than asserted only in prose.
"""
import numpy as np

from retrieval.interaction import cross_fitted_interaction, permutation_null

P = 200          # genes
N = 400          # cells per arm


def _world(rng, n=N, interaction=0.0, effect=1.0, noise=1.0):
    """Two states, a vehicle and a treated arm in each.

    The drug adds ``effect * u`` to every cell, plus ``interaction * v`` in state 1 only. The
    interaction term is the whole of what Gate 1 should be measuring; when it is zero the drug is
    additive across states.
    """
    u = rng.normal(size=P)
    v = rng.normal(size=P)
    base1 = rng.normal(size=P) * 2.0
    base2 = rng.normal(size=P) * 2.0

    def arm(mu, n_):
        return mu + rng.normal(size=(n_, P)) * noise

    c1, c2 = arm(base1, n), arm(base2, n)
    t1 = arm(base1 + effect * u + interaction * v, n)
    t2 = arm(base2 + effect * u, n)
    return t1, t2, c1, c2


def _old_D(t1, t2, c1, c2):
    r1 = t1.mean(0) - c1.mean(0)
    r2 = t2.mean(0) - c2.mean(0)
    cos = float(r1 @ r2 / (np.linalg.norm(r1) * np.linalg.norm(r2)))
    return 1.0 - cos


def test_additive_null_is_centred_on_zero():
    """Check 1. An additive drug must score ~0, regardless of how large its effect is."""
    vals = []
    for rep in range(24):
        rng = np.random.default_rng(rep)
        vals.append(cross_fitted_interaction(*_world(rng, interaction=0.0, effect=3.0),
                                             n_repeats=6, seed=rep)["S_int"])
    m = float(np.mean(vals))
    se = float(np.std(vals, ddof=1) / np.sqrt(len(vals)))
    assert abs(m) < 4 * se, f"additive null not centred: {m:.4g} +- {se:.4g}"


def test_real_interaction_is_detected_and_ordered():
    """A non-zero interaction must give a positive S_int that grows with its size."""
    out = []
    for lam in (0.0, 0.5, 1.0, 2.0):
        vals = [cross_fitted_interaction(*_world(np.random.default_rng(500 + rep),
                                                 interaction=lam, effect=1.0),
                                         n_repeats=6, seed=rep)["S_int"] for rep in range(12)]
        out.append(float(np.mean(vals)))
    assert out == sorted(out), f"S_int not monotone in the true interaction: {out}"
    assert out[-1] > 10 * abs(out[0]), f"a large interaction must dominate the null: {out}"


def test_state_label_permutation_returns_to_null():
    """Check 2. Shuffling the state labels destroys the interaction and nothing else."""
    rng = np.random.default_rng(7)
    res = permutation_null(*_world(rng, interaction=1.5, effect=1.0), n_perm=24, n_repeats=4,
                           seed=7)
    assert res["z"] > 3, f"a real interaction should stand out from its permutation null: {res}"
    assert abs(res["null_mean"]) < 3 * res["null_sd"], "the permutation null should sit at zero"

    rng = np.random.default_rng(8)
    res0 = permutation_null(*_world(rng, interaction=0.0, effect=3.0), n_perm=24, n_repeats=4,
                            seed=8)
    assert abs(res0["z"]) < 3, f"an additive drug should not stand out: {res0}"


def test_no_systematic_drift_with_cell_count():
    """Check 4. The old statistic rises as cells fall; the new one must not.

    Under the additive null the true value of both quantities is fixed: S_int is 0 and
    1 - cos(r_1, r_2) is 0. Only the second one moves with the sample size.
    """
    s_by_n, d_by_n = {}, {}
    for n in (50, 100, 200, 400):
        s, d = [], []
        for rep in range(16):
            rng = np.random.default_rng(900 + rep)
            w = _world(rng, n=n, interaction=0.0, effect=1.0)
            s.append(cross_fitted_interaction(*w, n_repeats=6, seed=rep)["S_int"])
            d.append(_old_D(*w))
        s_by_n[n], d_by_n[n] = float(np.mean(s)), float(np.mean(d))
    assert d_by_n[50] > 2 * d_by_n[400], (
        f"the old statistic should inflate at small n: {d_by_n}")
    spread = max(abs(v) for v in s_by_n.values())
    scale = max(abs(v) for v in d_by_n.values())
    assert spread < 0.05 * scale or spread < 1e-2, (
        f"S_int drifts with cell count: {s_by_n} against old {d_by_n}")


def test_interaction_share_is_scale_free():
    """The share must depend on the ratio of interaction to main effect, not on their size.

    Doubling both the additive effect and the interaction leaves the share where it was; doubling
    only the interaction raises it. This is the property the old statistic never had and the
    reason the share, not S_int, is what stratifies queries downstream.
    """
    def share(effect, inter, seed):
        vals = []
        for rep in range(12):
            rng = np.random.default_rng(seed + rep)
            vals.append(cross_fitted_interaction(*_world(rng, interaction=inter, effect=effect),
                                                 n_repeats=6, seed=rep)["interaction_share"])
        return float(np.mean(vals))

    small = share(1.0, 1.0, 100)
    doubled = share(2.0, 2.0, 200)
    assert abs(small - doubled) < 0.10, f"share is not scale-free: {small:.3f} vs {doubled:.3f}"
    more_interaction = share(1.0, 3.0, 300)
    assert more_interaction > small + 0.15, (
        f"share should rise with the interaction fraction: {small:.3f} -> {more_interaction:.3f}")


def test_share_is_near_zero_for_an_additive_drug():
    vals = []
    for rep in range(16):
        rng = np.random.default_rng(700 + rep)
        vals.append(cross_fitted_interaction(*_world(rng, interaction=0.0, effect=2.0),
                                             n_repeats=8, seed=rep)["interaction_share"])
    m = float(np.nanmean(vals))
    assert abs(m) < 0.05, f"additive drug should have ~0 interaction share, got {m:.4f}"


def test_reproducibility_index_separates_signal_from_noise():
    """R_int is near zero for an additive drug and high for a genuinely interacting one."""
    rng = np.random.default_rng(11)
    add = cross_fitted_interaction(*_world(rng, interaction=0.0, effect=2.0), n_repeats=10, seed=1)
    rng = np.random.default_rng(12)
    inter = cross_fitted_interaction(*_world(rng, interaction=2.0, effect=1.0), n_repeats=10, seed=2)
    assert abs(add["R_int"]) < 0.2, f"additive R_int should be near zero: {add['R_int']:.3f}"
    assert inter["R_int"] > 0.5, f"interacting R_int should be high: {inter['R_int']:.3f}"
