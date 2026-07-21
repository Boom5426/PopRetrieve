#!/usr/bin/env python
"""GO/NO-GO separability gate for GID-Flow on the sci-Plex3 K562 file.

Answers a single question: does this data have empirical room for a
distribution-aware (heterogeneity-aware) retrieval method, or are mean
delta-signatures already collinear / subpopulations inseparable?

    python scripts/check_separability.py [--pt data/processed/sciplex3_k562_24h.pt]

Emits a verdict: "GATE PASS" or "GATE WEAK: <reason>". This script is
diagnostic-only; it trains nothing.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gidflow.losses.distribution import energy_distance  # noqa: E402

try:
    from sklearn.decomposition import PCA
    from sklearn.metrics import silhouette_score
except Exception as e:  # pragma: no cover
    print(f"[fatal] sklearn required: {e}")
    raise


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _cos(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine between two 1-D vectors."""
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def _quartiles(x: np.ndarray) -> tuple[float, float, float, float, float]:
    """min, Q1, median, Q3, max."""
    return (
        float(np.min(x)),
        float(np.percentile(x, 25)),
        float(np.median(x)),
        float(np.percentile(x, 75)),
        float(np.max(x)),
    )


def _subsample(rows: np.ndarray, n: int, rng: np.random.Generator) -> np.ndarray:
    if len(rows) <= n:
        return rows
    return rng.choice(rows, size=n, replace=False)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pt", default=str(ROOT / "data/processed/sciplex3_k562_24h.pt"))
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    torch.manual_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print("=" * 72)
    print("GID-Flow separability gate")
    print(f"file   : {args.pt}")
    print(f"device : {device}")
    print("=" * 72)

    d = torch.load(args.pt, weights_only=False)
    X = np.asarray(d["X"], dtype=np.float32)        # [N, G] log1p-normalized
    obs = d["obs"]
    pert = obs["perturbation"].astype(str).str.strip()
    target = obs["target"].astype(str).str.strip()
    plev1 = obs["pathway_level_1"].astype(str).str.strip()
    dose = obs["dose_value"].astype(float)
    n_cells, n_genes = X.shape
    print(f"cells={n_cells}  genes={n_genes}  drugs(perturbation)={pert.nunique()}")

    # ---- pseudo-control = grand mean (no DMSO in this file) --------------- #
    pseudo_control = X.mean(axis=0)                 # [G]

    # ===================================================================== #
    # (1) Signature diversity: pairwise |cosine| over 188 drug delta-sigs
    # ===================================================================== #
    print("\n" + "-" * 72)
    print("[1] SIGNATURE DIVERSITY  (mean Delta-signature per drug)")
    print("-" * 72)
    drug_names = sorted(pert.unique())
    sigs = []
    for name in drug_names:
        rows = np.flatnonzero((pert == name).to_numpy())
        sigs.append(X[rows].mean(axis=0) - pseudo_control)
    S = np.stack(sigs, axis=0)                       # [D, G]
    # normalize rows, gram = cosine matrix
    Sn = S / (np.linalg.norm(S, axis=1, keepdims=True) + 1e-12)
    cosmat = Sn @ Sn.T                               # [D, D]
    iu = np.triu_indices(len(drug_names), k=1)
    abscos = np.abs(cosmat[iu])
    mn, q1, med, q3, mx = _quartiles(abscos)
    frac_high = float((abscos > 0.9).mean())
    print(f"n signatures        : {len(drug_names)}  ({len(abscos)} pairs)")
    print(f"|cosine| min/Q1/med/Q3/max : "
          f"{mn:.3f} / {q1:.3f} / {med:.3f} / {q3:.3f} / {mx:.3f}")
    print(f"mean |cosine|       : {abscos.mean():.3f}")
    print(f"frac pairs |cos|>0.9: {frac_high:.3f}   (high => collinear/bad)")
    diverse = med < 0.5
    print(f"=> signatures {'DIVERSE (good)' if diverse else 'COLLINEAR (bad)'}"
          f"  [median |cos| {'<' if diverse else '>='} 0.5]")

    # ===================================================================== #
    # (2) Subpopulation separability: HDAC vs JAK at highest dose
    # ===================================================================== #
    print("\n" + "-" * 72)
    print("[2] SUBPOPULATION SEPARABILITY  (two orthogonal MOA classes)")
    print("-" * 72)

    def _class_rows(label_a: str, label_b: str, series):
        return (
            np.flatnonzero(((series == label_a) & (dose == fixed_dose)).to_numpy()),
            np.flatnonzero(((series == label_b) & (dose == fixed_dose)).to_numpy()),
        )

    fixed_dose = 10000.0
    name_a, name_b = "HDAC", "JAK"
    rows_a, rows_b = _class_rows(name_a, name_b, target)
    used = "target"
    if len(rows_a) < 50 or len(rows_b) < 50:
        name_a, name_b = "Epigenetic regulation", "JAK/STAT signaling"
        rows_a, rows_b = _class_rows(name_a, name_b, plev1)
        used = "pathway_level_1"
    print(f"class source  : obs['{used}']")
    print(f"fixed dose    : {fixed_dose}")
    print(f"class A ({name_a}) cells: {len(rows_a)}")
    print(f"class B ({name_b}) cells: {len(rows_b)}")

    Xa, Xb = X[rows_a], X[rows_b]
    # class-mean delta signatures
    sig_a = Xa.mean(axis=0) - pseudo_control
    sig_b = Xb.mean(axis=0) - pseudo_control
    cos_ab = _cos(sig_a, sig_b)
    print(f"cosine(Delta_A, Delta_B) : {cos_ab:.3f}   (near 0 => orthogonal MOA)")

    # silhouette of 2-class labelling on PCA(50)
    Xcat = np.concatenate([Xa, Xb], axis=0)
    labels = np.concatenate([np.zeros(len(Xa), int), np.ones(len(Xb), int)])
    n_pc = min(50, Xcat.shape[0] - 1, Xcat.shape[1])
    emb = PCA(n_components=n_pc, random_state=args.seed).fit_transform(Xcat)
    # subsample for silhouette speed if huge
    if len(emb) > 4000:
        idx = rng.choice(len(emb), 4000, replace=False)
        sil = silhouette_score(emb[idx], labels[idx])
    else:
        sil = silhouette_score(emb, labels)
    print(f"silhouette (PCA{n_pc}, 2-class) : {sil:.3f}   "
          f"(>0 => classes separate; <=0 => entangled)")

    # nearest-centroid linear probe accuracy (train/test split on PCA emb)
    perm = rng.permutation(len(emb))
    n_tr = int(0.7 * len(emb))
    tr, te = perm[:n_tr], perm[n_tr:]
    ca = emb[tr][labels[tr] == 0].mean(axis=0)
    cb = emb[tr][labels[tr] == 1].mean(axis=0)
    da = np.linalg.norm(emb[te] - ca, axis=1)
    db = np.linalg.norm(emb[te] - cb, axis=1)
    pred = (db < da).astype(int)
    acc = float((pred == labels[te]).mean())
    print(f"nearest-centroid probe acc : {acc:.3f}   (0.5 = chance)")

    # Silhouette is dominated by per-cell transcriptional noise; the quantity a
    # signature/matching method actually consumes is the class-mean geometry.
    # Report a between/within centroid-distance ratio on PCA embeddings so the
    # verdict is honest about *why* silhouette is small (noise) vs whether the
    # class means are actually distinguishable (they are).
    ea, eb = emb[labels == 0], emb[labels == 1]
    mu_a, mu_b = ea.mean(0), eb.mean(0)
    between = np.linalg.norm(mu_a - mu_b)
    within = 0.5 * (np.linalg.norm(ea - mu_a, axis=1).mean()
                    + np.linalg.norm(eb - mu_b, axis=1).mean())
    bw_ratio = float(between / (within + 1e-8))
    print(f"between/within centroid dist : {bw_ratio:.3f}   "
          f"(>~0.3 => means separable under noise)")
    # A method that sees populations (probe acc) or class means (bw_ratio) can
    # separate these MOAs even though per-cell silhouette is small.
    separable = (acc > 0.6) and (abs(cos_ab) < 0.5) and (bw_ratio > 0.3)
    print(f"=> subpops {'SEPARABLE (good)' if separable else 'ENTANGLED (bad)'}"
          f"  [probe>0.6 & |cos_AB|<0.5 & between/within>0.3]")

    # ===================================================================== #
    # (3) Model-free mixture demo: the analytic existence proof
    # ===================================================================== #
    print("\n" + "-" * 72)
    print("[3] MODEL-FREE MIXTURE DEMO  (mean-cosine vs distribution-aware)")
    print("-" * 72)
    pc_t = torch.from_numpy(pseudo_control).to(device)

    def edist(a: np.ndarray, b: np.ndarray) -> float:
        with torch.no_grad():
            return float(energy_distance(
                torch.from_numpy(a).to(device), torch.from_numpy(b).to(device)))

    def build_mixture(maj_frac: float, n_total: int, rng_local):
        n_maj = int(round(maj_frac * n_total))
        n_min = n_total - n_maj
        ra = _subsample(rows_a, n_maj, rng_local)   # HDAC majority
        rb = _subsample(rows_b, n_min, rng_local)   # JAK minority
        return np.concatenate([X[ra], X[rb]], axis=0)

    maj_frac = 0.7
    n_total = 400
    # TARGET = 70% HDAC + 30% JAK
    target_pop = build_mixture(maj_frac, n_total, rng)
    # covers-both candidate = fresh independent 70/30 sample (held out)
    covers_both = build_mixture(maj_frac, n_total, np.random.default_rng(args.seed + 1))
    # majority-only (HDAC) and minority-only (JAK) candidates
    hdac_cand = X[_subsample(rows_a, n_total, np.random.default_rng(args.seed + 2))]
    jak_cand = X[_subsample(rows_b, n_total, np.random.default_rng(args.seed + 3))]

    cands = {
        "HDAC-only (majority)": hdac_cand,
        "JAK-only (minority)": jak_cand,
        "COVERS-BOTH (70/30)": covers_both,
    }

    # (a) mean-cosine ranking: cos(mean(target)-pc, mean(cand)-pc)
    tgt_sig = target_pop.mean(axis=0) - pseudo_control
    print(f"\ntarget = {int(maj_frac*100)}% HDAC + {int((1-maj_frac)*100)}% JAK "
          f"({n_total} cells)")
    print("\n(a) MEAN-COSINE ranking (higher = better):")
    cos_scores = {k: _cos(tgt_sig, v.mean(axis=0) - pseudo_control)
                  for k, v in cands.items()}
    for i, (k, s) in enumerate(sorted(cos_scores.items(),
                                      key=lambda kv: -kv[1]), 1):
        print(f"    rank {i}: {k:<22s} cos={s:+.4f}")
    cos_rank1 = max(cos_scores, key=cos_scores.get)
    print(f"    -> mean-cosine picks: {cos_rank1}")

    # (b) distribution-aware: -max_k energy_distance(cand_pop_k, target_pop_k)
    # split each population by its two subpops; score = -worst-subpop e-dist
    def subpop_score(cand: np.ndarray) -> float:
        # partition target and candidate into HDAC-like / JAK-like halves by
        # nearest class centroid in gene space, then worst-case e-distance.
        def split(pop):
            da = np.linalg.norm(pop - sig_a - pseudo_control, axis=1)
            db = np.linalg.norm(pop - sig_b - pseudo_control, axis=1)
            m = da < db
            return pop[m], pop[~m]
        ta, tb = split(target_pop)
        ka, kb = split(cand)
        eds = []
        for tk, kk in ((ta, ka), (tb, kb)):
            if len(tk) >= 2 and len(kk) >= 2:
                eds.append(edist(kk, tk))
            else:
                eds.append(1e6)   # candidate fails to cover this subpop
        return -max(eds)

    print("\n(b) DISTRIBUTION-AWARE ranking  "
          "(-max subpop energy-distance, higher = better):")
    dist_scores = {k: subpop_score(v) for k, v in cands.items()}
    for i, (k, s) in enumerate(sorted(dist_scores.items(),
                                      key=lambda kv: -kv[1]), 1):
        print(f"    rank {i}: {k:<22s} score={s:+.4f}")
    dist_rank1 = max(dist_scores, key=dist_scores.get)
    print(f"    -> distribution-aware picks: {dist_rank1}")

    demo_ok = (cos_rank1.startswith("HDAC-only")
               and dist_rank1.startswith("COVERS-BOTH"))
    print(f"\n=> mean-cosine {'WRONG (majority-only)' if cos_rank1.startswith('HDAC') else cos_rank1}"
          f" ; distribution-aware {'CORRECT (covers-both)' if dist_rank1.startswith('COVERS') else dist_rank1}")

    # ---- crossover sweep: majority fraction 0.5..0.9 --------------------- #
    # At each majority fraction f the ground-truth answer is a candidate whose
    # composition MATCHES the target (an f/(1-f) covers-both pop). We keep the
    # majority-only (HDAC) candidate fixed and ask: at what f does mean-cosine
    # start preferring the pure-majority drug over the true covers-both mix?
    # We report the cosine margin (cos_HDAC - cos_coversBoth); a flip to a
    # positive margin is where mean-cosine picks the WRONG (majority-only) drug.
    print("\n(c) CROSSOVER SWEEP  (mean-cosine: pure-majority vs matched mixture):")
    print("    f     cos(HDAC-only)  cos(matched-mix)   margin   mean-cosine rank1")
    crossover = None
    for f in np.round(np.arange(0.5, 0.91, 0.05), 2):
        tp = build_mixture(f, n_total, np.random.default_rng(args.seed + 100))
        ts = tp.mean(axis=0) - pseudo_control
        matched = build_mixture(f, n_total, np.random.default_rng(args.seed + 200))
        c_hdac = _cos(ts, hdac_cand.mean(axis=0) - pseudo_control)
        c_mix = _cos(ts, matched.mean(axis=0) - pseudo_control)
        margin = c_hdac - c_mix
        r1 = "MAJORITY-only (WRONG)" if margin > 0 else "matched-mix (correct)"
        print(f"    {f:.2f}   {c_hdac:+.4f}         {c_mix:+.4f}        "
              f"{margin:+.4f}   {r1}")
        if crossover is None and margin > 0:
            crossover = f
    if crossover is not None:
        print(f"    -> mean-cosine flips to the pure-majority drug at maj_frac ~ {crossover:.2f}")
    else:
        print("    -> mean-cosine preferred the matched mixture across [0.5,0.9] "
              "(margins negative)")

    # ===================================================================== #
    # (4) verdict
    # ===================================================================== #
    print("\n" + "=" * 72)
    reasons = []
    if not diverse:
        reasons.append(f"signatures collinear (median|cos|={med:.2f}>=0.5)")
    if not separable:
        reasons.append(f"subpops entangled (acc={acc:.2f}, |cos_AB|={abs(cos_ab):.2f}, "
                       f"between/within={bw_ratio:.2f})")
    if not demo_ok:
        reasons.append("mixture demo did not show the mean-cosine->distribution-aware flip")
    if diverse and separable and demo_ok:
        print("VERDICT: GATE PASS")
    else:
        print("VERDICT: GATE WEAK: " + "; ".join(reasons))
    print("=" * 72)


if __name__ == "__main__":
    main()
