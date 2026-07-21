import os, sys, time, json, numpy as np, pandas as pd
sys.path.insert(0, "src")
t0=time.time()
import experiments.exp11_hir_benchmark as E
from benchmarks.heterogeneous_retrieval_benchmark import generate_hir_cell
from benchmarks.preference_conflict import (
    topk_disagreement, weighted_kendall_conflict, standard_kendall_conflict, response_cosine)
from benchmarks.oracle_utility import oracle_flip_risk

grid_spec = E.FULL_GRID
cells = E._make_grid(grid_spec, 20)
n_total=len(cells)
print("LEAN method-independent FULL: %d cells" % n_total, flush=True)
rows=[]
for ci,(params,seed) in enumerate(cells):
    if ci>0 and ci%max(1,n_total//10)==0:
        el=time.time()-t0; rate=ci/el
        print("  [%d/%d] %.1f cells/s ETA %.0fs" % (ci,n_total,rate,(n_total-ci)/rate), flush=True)
    grid_id="a%.2f_c%.2f_n%d_s%s_L%s_I%s" % (params["alpha"],params["conflict_level"],
        params["cells_per_subpop"],params["noise_sigma"],params["library_size"],params["info_cond"])
    cell=generate_hir_cell(n_subpops=params["n_subpops"],dim=params["dim"],library_size=params["library_size"],
        majority_fraction=params["alpha"],conflict_level=params["conflict_level"],
        cells_per_subpop=params["cells_per_subpop"],noise_sigma=params["noise_sigma"],
        information_condition=params["info_cond"],seed=seed)
    td=topk_disagreement(cell); wkc=weighted_kendall_conflict(cell)
    skc=standard_kendall_conflict(cell); rc=response_cosine(cell)
    for wt in ["mean","worst"]:
        flip=oracle_flip_risk(cell,welfare=wt)
        rows.append(dict(grid_id=grid_id,seed=seed,alpha=params["alpha"],conflict_level=params["conflict_level"],
            cells_per_subpop=params["cells_per_subpop"],information_condition=params["info_cond"],
            topk_disagreement=td,weighted_kendall_conflict=wkc,standard_kendall_conflict=skc,response_cosine=rc,
            welfare_type=wt,oracle_flip_risk=flip))
df_ind=pd.DataFrame(rows)
os.makedirs("results/_audit/exp11_lean",exist_ok=True)
df_ind.to_csv("results/_audit/exp11_lean/method_independent_full.csv",index=False)
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, roc_curve
df=df_ind[df_ind.welfare_type=="worst"].copy()
fc=["topk_disagreement","weighted_kendall_conflict","standard_kendall_conflict","response_cosine"]
y=df["oracle_flip_risk"].values.astype(int); X=df[fc].values
gids=df.grid_id.values; uq=np.unique(gids); ypred=np.zeros(len(y)); sc=StandardScaler()
for g in uq:
    m=gids==g; Xtr,ytr=X[~m],y[~m]; Xte=X[m]
    if len(set(ytr))<2: ypred[m]=ytr.mean(); continue
    Xs=sc.fit_transform(Xtr); lr=LogisticRegression(max_iter=1000,random_state=0); lr.fit(Xs,ytr)
    ypred[m]=lr.predict_proba(sc.transform(Xte))[:,1]
auc=float(roc_auc_score(y,ypred)); fpr,tpr,_=roc_curve(y,ypred)
pd.DataFrame({"y_true":y,"y_score":ypred}).to_csv("results/_audit/exp11_lean/fig6f_roc_points.csv",index=False)
pd.DataFrame({"fpr":fpr,"tpr":tpr}).to_csv("results/_audit/exp11_lean/fig6f_roc_curve.csv",index=False)
summ=dict(auc=auc,n=int(len(y)),n_pos=int(y.sum()),n_neg=int(len(y)-y.sum()),wall_s=round(time.time()-t0,1))
json.dump(summ,open("results/_audit/exp11_lean/fig6f_roc_summary.json","w"),indent=2)
print("LEAN_ROC_SUMMARY "+json.dumps(summ),flush=True)
