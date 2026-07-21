import torch, numpy as np, pandas as pd, os, json, time
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score
# --- repo-root path resolution (added for public release; replaces hardcoded /data/boom/DART) ---
from pathlib import Path as _P
REPO = _P(__file__).resolve().parents[2]
SRC = str(REPO / "src")
RESULTS_AUDIT = str(REPO / "results" / "upgrade")
DATA_PROC = str(REPO / "data" / "processed")
DATA_ANNO = str(REPO / "data" / "annotation")
# ------------------------------------------------------------------------------------------------

t0=time.time()
RS=np.random.RandomState(0)
d = torch.load(str(_P(DATA_PROC) / "sciplex3_all.pt"), weights_only=False)
X = d["X"]; X = X.numpy() if hasattr(X,"numpy") else np.asarray(X)
obs = d["obs"].reset_index(drop=True)
# K562, dose 10000, not control
base = (obs["cell_line"]=="K562") & (obs["dose_value"]==10000.0) & (~obs["is_control"].astype(bool))
tgt = obs["target"].astype(str).str.upper()
H_mask = base & tgt.str.contains("HDAC")
J_mask = base & tgt.str.contains("JAK")
Hidx = np.where(H_mask.values)[0]; Jidx = np.where(J_mask.values)[0]
print(f"n_HDAC={len(Hidx)} n_JAK={len(Jidx)}", flush=True)
XH = X[Hidx].astype(np.float64); XJ = X[Jidx].astype(np.float64)

BUDGETS = [25,50,100,200,400]
SEPS    = [1.0,1.5,2.0,3.0,5.0,8.0]
SEEDS   = list(range(20))
maxn = min(len(Hidx), len(Jidx))
BUDGETS = [b for b in BUDGETS if b <= maxn]
print("effective budgets:", BUDGETS, "maxn per source:", maxn, flush=True)

# Separation is defined ONCE, on the full source populations, and is therefore a fixed,
# sample-independent transformation.
#
# It used to be computed on the SAMPLED n cells and then applied to those same cells:
#     g = vstack([H, J]).mean(0);  cH = H.mean(0);  cJ = J.mean(0)
# At small n those sample centroids are noisy, so the shift amplified whatever separation
# each draw happened to contain. That is why the resulting phase diagram showed ARI
# DECREASING with cell budget at fixed separation (median ARI 1.000 at 25 cells/source
# falling to 0.289 at 400, at s=2.0), which is indefensible on its face: clustering does not
# get harder as you collect more cells. It was an artifact of fitting the manipulation on the
# same sample it was evaluated on, not a property of identifiability.
G_ALL = np.vstack([XH, XJ]).mean(0)
CH_FULL = XH.mean(0)
CJ_FULL = XJ.mean(0)

rows=[]
for s in SEPS:
    for n in BUDGETS:
        for seed in SEEDS:
            rng = np.random.RandomState(1000+seed)
            hi = rng.choice(len(XH), n, replace=False)
            ji = rng.choice(len(XJ), n, replace=False)
            H = XH[hi].copy(); J = XJ[ji].copy()
            # separation scaling: push each source along (full-source centroid - global centroid)
            H2 = H + (s-1.0)*(CH_FULL - G_ALL)
            J2 = J + (s-1.0)*(CJ_FULL - G_ALL)
            Xm = np.vstack([H2,J2])
            y  = np.array([0]*n + [1]*n)
            km = KMeans(n_clusters=2, n_init=10, random_state=seed).fit(Xm)
            ari = adjusted_rand_score(y, km.labels_)
            try:
                sil = silhouette_score(Xm, y)  # silhouette of TRUE labels = separability proxy
            except Exception:
                sil = np.nan
            rows.append(dict(separation_scale=s, cells_per_source=n, seed=seed,
                             ari_kmeans_k2=ari, sil_true_labels=sil, n_total=2*n))
    print(f"sep={s} done t={time.time()-t0:.0f}s", flush=True)

df = pd.DataFrame(rows)
out = str(_P(RESULTS_AUDIT) / "identifiability_phase_diagram.csv")
df.to_csv(out, index=False)
# summary grid (mean ARI per sep x budget) + real-data anchor (s=1)
grid = df.groupby(["separation_scale","cells_per_source"])["ari_kmeans_k2"].mean().reset_index()
real = df[df.separation_scale==1.0].groupby("cells_per_source").agg(
        ari=("ari_kmeans_k2","mean"), sil=("sil_true_labels","mean")).reset_index()
summ = dict(
  out_file=out, n_rows=len(df), budgets=BUDGETS, seps=SEPS,
  real_sep1_ari=real.set_index("cells_per_source")["ari"].round(4).to_dict(),
  real_sep1_sil=real.set_index("cells_per_source")["sil"].round(4).to_dict(),
  ari_at_n400=grid[grid.cells_per_source==max(BUDGETS)].set_index("separation_scale")["ari_kmeans_k2"].round(3).to_dict(),
  wall_s=round(time.time()-t0,1))
json.dump(summ, open(str(_P(RESULTS_AUDIT) / "identifiability_phase_diagram_summary.json"),"w"), indent=2)
print("SUMMARY", json.dumps(summ))