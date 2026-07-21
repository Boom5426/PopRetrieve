#!/usr/bin/env python
"""Evaluate SciPlex3 drug retrieval: rank the full candidate library per query.

    python scripts/eval_drug_retrieval_sciplex3.py \
        --checkpoint checkpoints/phase2_best.pt --split random --fold test \
        --out results/drug_ranking
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gidflow.eval_retrieval import score_queries              # noqa: E402
from gidflow.metrics.ranking import bootstrap_ci, retrieval_metrics  # noqa: E402
from gidflow.utils import (build_data, build_matching, build_model,  # noqa: E402
                           get_device)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--split", default=None, help="override split; else use ckpt cfg")
    ap.add_argument("--fold", default="test")
    ap.add_argument("--out", default="results/drug_ranking")
    ap.add_argument("--n-source", type=int, default=128)
    ap.add_argument("--n-target", type=int, default=128)
    ap.add_argument("--n-repeats", type=int, default=3)
    ap.add_argument("--top-k", type=int, default=10)
    args = ap.parse_args()

    ckpt = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    cfg = ckpt["cfg"]
    device = get_device(cfg.get("device", "cuda"))
    data = build_data(cfg)
    model = build_model(cfg, data).to(device)
    model.load_state_dict(ckpt["model"])
    model.eval()
    ctx = build_matching(data, device=str(device))

    split = args.split or cfg["data"]["split"]
    split_path = Path(cfg["data"]["splits_dir"]) / f"{split}.json"
    keys = data.split_keys(split_path, args.fold)
    print(f"[eval] split={split} fold={args.fold} queries={len(keys)}", flush=True)

    r = score_queries(model, data, ctx, keys, device, n_source=args.n_source,
                      n_target=args.n_target, query_batch=cfg["eval"]["query_batch"],
                      n_repeats=args.n_repeats)
    scores, true_pos, keys = r["scores"], r["true_pos"], r["keys"]
    m = retrieval_metrics(scores, true_pos, r["moa_same"])
    for metric in ("hit@1", "hit@5", "hit@10", "mrr"):
        p, lo, hi = bootstrap_ci(scores, true_pos, metric, r["moa_same"])
        m[metric + "_ci95"] = [round(lo, 4), round(hi, 4)]
    print("[metrics]", json.dumps({k: (round(v, 4) if isinstance(v, float) else v)
                                   for k, v in m.items()}, indent=0), flush=True)

    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    cand = ctx.candidate_indices.cpu().numpy()
    drug_order = data.ann.drug_order
    rows = []
    for qi, key in enumerate(keys):
        order = np.argsort(-scores[qi])                         # best first
        true_drug = drug_order[data.conditions[key].drug_idx].strip()
        true_rank = int((scores[qi] > scores[qi, true_pos[qi]]).sum() + 1)
        for rank, li in enumerate(order[: args.top_k], start=1):
            rows.append({"query_id": key, "true_drug": true_drug, "true_rank": true_rank,
                         "rank": rank, "drug": drug_order[cand[li]].strip(),
                         "score": float(scores[qi, li])})
    df = pd.DataFrame(rows)
    df.to_csv(out / f"predicted_rankings_{split}_{args.fold}.csv", index=False)

    with open(out / f"report_{split}_{args.fold}.md", "w") as f:
        f.write(f"# DrugRank-Flow retrieval — split={split} fold={args.fold}\n\n")
        f.write(f"Queries: {len(keys)} | Candidate library: {len(cand)} drugs\n\n")
        f.write("## Metrics\n\n")
        for k in ("hit@1", "hit@5", "hit@10", "mrr", "ndcg@10", "median_rank",
                  "median_rank_frac", "moa_auc"):
            v = m.get(k)
            ci = m.get(k + "_ci95")
            f.write(f"- **{k}**: {v:.4f}" + (f"  (95% CI {ci})\n" if ci else "\n"))
        f.write("\n## Example queries (first 5)\n\n")
        for key in keys[:5]:
            sub = df[df.query_id == key]
            td = sub.iloc[0]["true_drug"]; tr = int(sub.iloc[0]["true_rank"])
            f.write(f"### {key}\n- true drug: **{td}** (rank {tr})\n- top-5: "
                    + ", ".join(f"{x.drug}({x.score:.2f})" for x in sub.head(5).itertuples()) + "\n\n")
    print(f"[eval] wrote {out}/predicted_rankings_{split}_{args.fold}.csv + report", flush=True)


if __name__ == "__main__":
    main()
