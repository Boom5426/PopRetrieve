import os, sys, time, json, numpy as np, pandas as pd
sys.path.insert(0, "src")
t0=time.time()
# capture the exact (y, y_pred) passed to roc_auc_score inside predictability_auc
import benchmarks.predictability as P
from sklearn.metrics import roc_auc_score as _real_auc
_cap = {}
def _capauc(y, s, *a, **k):
    _cap["y"] = np.asarray(y); _cap["score"] = np.asarray(s)
    return _real_auc(y, s, *a, **k)
P.roc_auc_score = _capauc
# redirect OUT to a clean dir so existing QUICK files are untouched
import experiments.exp11_hir_benchmark as E
E.OUT = "_audit/exp11_full"
os.makedirs("results/_audit/exp11_full", exist_ok=True)
print("launching FULL exp11 (13440 cells)...", flush=True)
df_ind, df_perf = E.run(quick=False)
# dump ROC arrays
if "y" in _cap:
    roc = pd.DataFrame({"y_true": _cap["y"].astype(int), "y_score": _cap["score"]})
    roc.to_csv("results/_audit/exp11_full/fig6f_roc_points.csv", index=False)
    from sklearn.metrics import roc_curve, roc_auc_score
    fpr, tpr, thr = roc_curve(_cap["y"], _cap["score"])
    pd.DataFrame({"fpr":fpr,"tpr":tpr}).to_csv("results/_audit/exp11_full/fig6f_roc_curve.csv", index=False)
    auc = float(roc_auc_score(_cap["y"], _cap["score"]))
    summ = dict(auc=auc, n=int(len(_cap["y"])), n_pos=int(_cap["y"].sum()),
                n_neg=int(len(_cap["y"])-_cap["y"].sum()), wall_s=round(time.time()-t0,1))
    json.dump(summ, open("results/_audit/exp11_full/fig6f_roc_summary.json","w"), indent=2)
    print("ROC_SUMMARY", json.dumps(summ), flush=True)
else:
    print("WARNING: roc_auc_score was not called (predictability layer may have skipped)", flush=True)
print("DONE full exp11 in %.0fs" % (time.time()-t0), flush=True)