"""Stage 2: paired tests. scipy is not installed in any interpreter on this machine, so the
Wilcoxon signed-rank normal approximation is implemented here and cross-checked against the
p-values the manuscript's own (scipy-based) pipeline produced."""
import json, math
from pathlib import Path
import numpy as np

OUT = Path(__file__).resolve().parents[2] / "results" / "audit"


def _rankdata(a):
    order = np.argsort(a, kind="mergesort")
    ranks = np.empty(len(a), float)
    sa = a[order]
    i = 0
    while i < len(a):
        j = i
        while j + 1 < len(a) and sa[j + 1] == sa[i]:
            j += 1
        ranks[order[i:j + 1]] = 0.5 * (i + j) + 1.0
        i = j + 1
    return ranks


def _two_sided(z):
    return math.erfc(abs(z) / math.sqrt(2.0))


def wilcoxon(d, zero_method="wilcox"):
    """Two-sided Wilcoxon signed-rank, normal approximation with tie correction.
    zero_method: 'wilcox' drops zeros; 'zsplit' splits them between the two rank sums."""
    d = np.asarray(d, float)
    d = d[np.isfinite(d)]
    n_zero = int((d == 0).sum())
    if zero_method == "wilcox":
        d = d[d != 0]
    n = len(d)
    if n < 2:
        return None
    r = _rankdata(np.abs(d))
    Tp = float(r[d > 0].sum())
    Tm = float(r[d < 0].sum())
    if zero_method == "zsplit":
        half = 0.5 * float(r[d == 0].sum())
        Tp += half
        Tm += half
    T = min(Tp, Tm)
    mn = n * (n + 1) / 4.0
    _, cnt = np.unique(np.abs(d), return_counts=True)
    tie = float(((cnt ** 3) - cnt).sum())
    var = n * (n + 1) * (2 * n + 1) / 24.0 - tie / 48.0
    if var <= 0:
        return None
    z = (T - mn) / math.sqrt(var)
    return {"stat_T": T, "T_plus": Tp, "T_minus": Tm, "n_used": n, "n_zero": n_zero,
            "z": float(z), "p": float(_two_sided(z))}


z = np.load(OUT / "paired_diffs.npz")
res = {}
for k in z.files:
    d = z[k]
    res[k] = {"n_total": int(len(d)),
              "n_zero": int((d == 0).sum()),
              "median": float(np.median(d)),
              "mean": float(np.mean(d)),
              "sd": float(np.std(d, ddof=1)),
              "frac_improved": float((d > 0).mean()),
              "frac_worsened": float((d < 0).mean()),
              "frac_tied": float((d == 0).mean()),
              "wilcoxon_dropzero": wilcoxon(d, "wilcox"),
              "wilcoxon_zsplit": wilcoxon(d, "zsplit")}

(OUT / "audit_stage2.json").write_text(json.dumps(res, indent=1))
for k in sorted(res):
    v = res[k]
    w = v["wilcoxon_dropzero"]
    print(f'{k:40s} n={v["n_total"]:4d} zero={v["n_zero"]:3d} med={v["median"]:+.4f} '
          f'mean={v["mean"]:+.4f} imp={v["frac_improved"]:.3f} wor={v["frac_worsened"]:.3f} '
          f'tie={v["frac_tied"]:.3f} p={w["p"]:.3e}')
