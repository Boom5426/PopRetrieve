#!/usr/bin/env python3

"""signal_decode_run.py: EvalShift-vs-mean pick divergence + drug attributes on SciPlex3."""

# --- repo-root path resolution (added for public release; replaces hardcoded /data/boom/DART) ---
from pathlib import Path as _P
REPO = _P(__file__).resolve().parents[2]
SRC = str(REPO / "src")
RESULTS_AUDIT = str(REPO / "results" / "upgrade")
DATA_PROC = str(REPO / "data" / "processed")
DATA_ANNO = str(REPO / "data" / "annotation")
# ------------------------------------------------------------------------------------------------
import sys, os, json, time
sys.path.insert(0, SRC)
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from data.load_sciplex3 import load_sciplex3
from retrieval.metrics import score_energy, score_mean_cosine

SEEDS = [42, 123, 456]
DOSE = 10000; MIN_CELLS = 30; MAX_CELLS = 150
ADIR = RESULTS_AUDIT
ANNODIR = DATA_ANNO
OUT = os.path.join(ADIR, "signal_decode.csv")
os.makedirs(ADIR, exist_ok=True)

# ---- helpers ----
def tani(a, b):
    x = np.dot(fp[a], fp[b]); u = fp[a].sum() + fp[b].sum() - x
    return float(x / u) if u > 0 else 0.0

def tjac(a, b):
    ta, tb = tgt[a].astype(float), tgt[b].astype(float)
    x = np.dot(ta, tb); u = ta.sum() + tb.sum() - x
    return float(x / u) if u > 0 else 0.0

def welfare_vec(cmeans, qX, ctrl, seed=42):
    """min-over-KMeans-states cosine(cand_delta, state_delta). Shape (n_cands,)."""
    if len(qX) < 4:
        return np.full(len(cmeans), np.nan)
    lb = KMeans(2, random_state=seed, n_init=10).fit_predict(qX)
    sd = [qX[lb == s].mean(0) - ctrl for s in range(2) if (lb == s).sum() > 0]
    if not sd:
        return np.full(len(cmeans), np.nan)
    sd = np.array(sd)
    cd = cmeans - ctrl
    cn = np.linalg.norm(cd, axis=1, keepdims=True).clip(1e-10)
    sn = np.linalg.norm(sd, axis=1, keepdims=True).clip(1e-10)
    return ((cd / cn) @ (sd / sn).T).min(axis=1)

# ---- load ----
t0 = time.time()
print("[load] SciPlex3", flush=True)
ds = load_sciplex3()
X = np.asarray(ds.X, dtype=np.float32)
obs = ds.obs.copy()
print(f"  X={X.shape} cols={list(obs.columns)}", flush=True)

print("[load] annotation", flush=True)
with open(f"{ANNODIR}/drug_order.json") as f:
    drug_order = json.load(f)
anno = pd.read_csv(f"{ANNODIR}/drug_annotation_master.csv")
fp = (np.load(f"{ANNODIR}/drug_morgan_ecfp4.npy") > 0).astype(np.float32)
tgt = np.load(f"{ANNODIR}/drug_protein_targets.npy")
d2i = {d: i for i, d in enumerate(drug_order)}
annd = {r.drug_name: {"moa": r.moa_class if pd.notna(r.moa_class) else None,
                       "nt": int(r.n_targets) if pd.notna(r.n_targets) else 0}
        for _, r in anno.iterrows()}

# dose column
dcol = None
for c in ("dose", "dose_value", "dose_nM", "Dose", "product_dose"):
    if c in obs.columns:
        dcol = c; break
print(f"  dose_col={dcol}", flush=True)

# ---- main ----
rows = []
EHIS = None  # energy_higher_is_similar

for cl in ("K562", "A549", "MCF7"):
    print(f"\n{'='*50}\n[{cl}]", flush=True)
    cm = obs.cell_line.values == cl
    cX = X[cm]; co = obs[cm].reset_index(drop=True)
    ctrl = co.is_control.values.astype(bool)
    ctrl_mean = cX[ctrl].mean(axis=0)

    # build drug -> cells
    dcells = {}
    for drug in co[~ctrl].perturbation.unique():
        m = (~co.is_control.values) & (co.perturbation.values == drug)
        if dcol is not None:
            m = m & (co[dcol].values == DOSE)
        dx = cX[m]
        if len(dx) >= MIN_CELLS and drug in d2i:
            dcells[drug] = dx
    drugs = sorted(dcells); N = len(drugs)
    print(f"  drugs={N}  (>={MIN_CELLS} cells, in annotation)", flush=True)
    if N < 2:
        print("  SKIP", flush=True); continue

    # score direction check (once across all cell lines)
    if EHIS is None:
        a, b = drugs[0], drugs[-1]
        xa = dcells[a]; h = min(len(xa) // 2, 75)
        ss = score_energy(xa[:h], xa[h:2*h], max_cells=500, seed=42)
        cs = score_energy(xa[:h], dcells[b][:min(h, len(dcells[b]))],
                          max_cells=500, seed=42)
        EHIS = (ss > cs)
        print(f"  [direction] self={ss:.6f} cross={cs:.6f} "
              f"=> higher_is_similar={EHIS}", flush=True)

    # full means for welfare (all cells, not subsampled)
    dmeans = np.array([dcells[d].mean(0) for d in drugs])

    for seed in SEEDS:
        rng = np.random.RandomState(seed)
        ts = time.time()
        print(f"  seed={seed}", flush=True)

        # subsample each drug for scoring
        sub = {}
        for d in drugs:
            v = dcells[d]
            idx = rng.choice(len(v), min(len(v), MAX_CELLS), replace=False)
            sub[d] = v[idx]

        # NxN score matrices (symmetric, upper triangle only)
        emat = np.full((N, N), np.nan)
        mmat = np.full((N, N), np.nan)
        done = 0; tot = N * (N - 1) // 2
        for i in range(N):
            for j in range(i + 1, N):
                try:
                    e = score_energy(sub[drugs[i]], sub[drugs[j]],
                                     max_cells=500, seed=seed)
                except Exception as ex:
                    print(f"    ERR energy {drugs[i]} vs {drugs[j]}: {ex}",
                          flush=True)
                    e = np.nan
                try:
                    mc = score_mean_cosine(sub[drugs[i]], sub[drugs[j]],
                                           control_P=ctrl_mean,
                                           control_Q=ctrl_mean)
                except Exception as ex:
                    print(f"    ERR mean_cos {drugs[i]} vs {drugs[j]}: {ex}",
                          flush=True)
                    mc = np.nan
                emat[i, j] = emat[j, i] = e
                mmat[i, j] = mmat[j, i] = mc
                done += 1
                if done % 300 == 0:
                    print(f"    pairs {done}/{tot}", flush=True)
        print(f"    matrix {time.time() - ts:.0f}s", flush=True)

        # per-query picks + features
        for qi in range(N):
            qd = drugs[qi]; qi_i = d2i[qd]
            qa = annd.get(qd, {"moa": None, "nt": 0}); qmoa = qa["moa"]

            # EvalShift (energy) pick
            es = emat[qi].copy()
            es[qi] = -np.inf if EHIS else np.inf
            dp = int(np.nanargmax(es) if EHIS else np.nanargmin(es))

            # mean-cosine pick (higher = more similar)
            ms = mmat[qi].copy()
            ms[qi] = -np.inf
            mp = int(np.nanargmax(ms))

            dd, md = drugs[dp], drugs[mp]
            ddi, mdi = d2i[dd], d2i[md]
            da = annd.get(dd, {"moa": None, "nt": 0})
            ma_ = annd.get(md, {"moa": None, "nt": 0})

            # welfare + regret
            ci = [k for k in range(N) if k != qi]
            wf = welfare_vec(dmeans[ci], dcells[qd], ctrl_mean, seed=seed)
            mxw = float(np.nanmax(wf))
            dw = float(wf[ci.index(dp)])
            mw = float(wf[ci.index(mp)])

            rows.append(dict(
                cell_line=cl, seed=seed, query_drug=qd, query_moa=qmoa,
                dart_pick=dd, mean_pick=md, picks_differ=int(dd != md),
                # EvalShift pick attributes
                dart_tanimoto=tani(ddi, qi_i),
                dart_ntargets=da["nt"],
                dart_target_jaccard=tjac(ddi, qi_i),
                dart_moa_match=int(da["moa"] is not None and da["moa"] == qmoa),
                # mean pick attributes
                mean_tanimoto=tani(mdi, qi_i),
                mean_ntargets=ma_["nt"],
                mean_target_jaccard=tjac(mdi, qi_i),
                mean_moa_match=int(ma_["moa"] is not None and ma_["moa"] == qmoa),
                # welfare / regret
                dart_welfare=dw, mean_welfare=mw,
                dart_regret=mxw - dw, mean_regret=mxw - mw,
                regret_advantage=dw - mw,  # positive = EvalShift lower regret
            ))
        print(f"  seed={seed} done {time.time() - ts:.0f}s", flush=True)

    # checkpoint after each cell line
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"  [checkpoint] {len(rows)} rows -> {OUT}", flush=True)

df = pd.DataFrame(rows)
df.to_csv(OUT, index=False)
print(f"\n[DONE] {len(df)} rows -> {OUT}", flush=True)
print(f"wall={time.time() - t0:.0f}s", flush=True)
print(f"differ={df.picks_differ.mean():.4f}", flush=True)
for f_ in ("tanimoto", "ntargets", "target_jaccard", "moa_match"):
    d_ = df[f"dart_{f_}"].mean(); m_ = df[f"mean_{f_}"].mean()
    print(f"  {f_}: EvalShift={d_:.4f} Mean={m_:.4f}", flush=True)
print(f"regret_adv={df.regret_advantage.mean():.4f}", flush=True)
