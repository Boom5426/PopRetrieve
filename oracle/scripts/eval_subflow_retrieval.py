#!/usr/bin/env python
"""SubFlow retrieval eval: rank the drug library by how well each candidate's
GENERATED treated population matches the observed treated population.

For query condition (source = matched control pool, target = observed treated
cells) and candidate drug d: generate Yhat_d = SubFlow.generate(source, d, dose,
cell_line); score by coverage (worst-subpop energy distance) and by plain energy
distance. Rank; the true drug should rank highest.

    python scripts/eval_subflow_retrieval.py --checkpoint checkpoints/subflow_last.pt \
        --split random --fold test [--top-m 188] [--drug-chunk 32]
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

from gidflow.data.population_dataset import PopulationPairDataset  # noqa: E402
from gidflow.metrics.ranking import bootstrap_ci, retrieval_metrics  # noqa: E402
from gidflow.utils import build_data, build_matching, get_device   # noqa: E402

# reuse the trainer's model builder for an identical architecture
sys.path.insert(0, str(ROOT / "scripts"))
from train_subflow import build_subflow                            # noqa: E402


def build_mean_deltas(data, cand_idx, device, train_keys, cell_lines):
    """Per-(candidate drug, cell line) mean expression delta from TRAIN conditions
    ONLY -- the 'population-in, mean-out' ablation, matched to SubFlow's drug+line
    conditioning and leakage-free (never uses the test target).

    Returns [D, L, G] (nan where a drug has no train condition in that line) and a
    validity mask [D, L]."""
    X = data.X
    ctrl_mean = {c: X[r].mean(0) for c, r in data.control_rows.items() if len(r)}
    grand = X.mean(0)
    L = len(cell_lines); line_ix = {c: i for i, c in enumerate(cell_lines)}
    acc = torch.zeros(len(cand_idx), L, X.shape[1])
    cnt = torch.zeros(len(cand_idx), L)
    a2row = {int(a): i for i, a in enumerate(cand_idx)}
    for k in train_keys:
        cond = data.conditions[k]
        i = a2row.get(cond.drug_idx)
        if i is None:
            continue
        li = line_ix[cond.cell_line]
        acc[i, li] += X[cond.rows].mean(0) - ctrl_mean.get(cond.cell_line, grand)
        cnt[i, li] += 1
    valid = cnt > 0
    deltas = torch.where(valid[..., None], acc / cnt.clamp_min(1)[..., None],
                         torch.full_like(acc, float("nan")))
    return deltas.to(device), valid.to(device)


@torch.no_grad()
def score_query(model, ctx, source, source_mask, target, target_mask, cell_line_idx,
                log_dose, cand_idx, beta, n_steps, drug_chunk, device,
                transport="subflow", mean_deltas=None, mean_valid=None):
    """Return (coverage[D], energy[D]) scores over the candidate library for a query.

    transport='subflow'   -> generate via the learned per-cell flow field.
    transport='meanshift' -> ablation: Yhat = source + train-estimated per-(drug,line)
                             mean delta (uniform additive shift = the mean-out failure
                             mode). If this matches 'subflow', the learned field adds
                             nothing. OOD drugs (no train delta) are ranked last.
    transport='identity'  -> sanity control: Yhat = source (drug-agnostic). Should give
                             ~random retrieval; if high, the scoring itself leaks."""
    Ns = source.shape[1]
    src_assign = model.subpop_head(model.pop_encoder.encode_cells(source))     # [1,Ns,K]
    line = int(cell_line_idx.item())
    D = len(cand_idx)
    cov = np.empty(D, np.float32); eng = np.empty(D, np.float32)
    for s in range(0, D, drug_chunk):
        chunk = cand_idx[s:s + drug_chunk]
        c = len(chunk)
        src_c = source.expand(c, Ns, source.shape[2])                          # [c,Ns,G]
        invalid = None
        if transport == "meanshift":
            delta = mean_deltas[s:s + c, line]                                 # [c,G]
            invalid = ~mean_valid[s:s + c, line]                               # [c] OOD -> no train delta
            Yhat = src_c + torch.nan_to_num(delta)[:, None, :]
        elif transport == "identity":
            Yhat = src_c                                                       # drug-agnostic
        else:
            smask_c = source_mask.expand(c, Ns)
            didx = torch.as_tensor(chunk, dtype=torch.long, device=device)
            Yhat = model.generate(src_c, smask_c, didx, log_dose.expand(c),
                                   cell_line_idx.expand(c), n_steps=n_steps)   # [c,Ns,G]
        tgt_c = target.expand(c, target.shape[1], target.shape[2])
        tmask_c = target_mask.expand(c, target.shape[1])
        e = model.energy_score(Yhat, tgt_c, tmask_c)
        sa_c = src_assign.expand(c, Ns, src_assign.shape[-1])
        cv = model.coverage_score(Yhat, sa_c, tgt_c, tmask_c, beta=beta)
        if invalid is not None and invalid.any():           # OOD drug -> rank last
            e = e.masked_fill(invalid, -1e9); cv = cv.masked_fill(invalid, -1e9)
        eng[s:s + c] = e.cpu().numpy(); cov[s:s + c] = cv.cpu().numpy()
    return cov, eng


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--split", default=None)
    ap.add_argument("--fold", default="test")
    ap.add_argument("--out", default=None)
    ap.add_argument("--n-source", type=int, default=128)
    ap.add_argument("--n-target", type=int, default=128)
    ap.add_argument("--n-steps", type=int, default=8)
    ap.add_argument("--drug-chunk", type=int, default=32)
    ap.add_argument("--max-queries", type=int, default=None, help="cap #queries (speed)")
    ap.add_argument("--score", choices=["coverage", "energy"], default="coverage")
    ap.add_argument("--transport", choices=["subflow", "meanshift", "identity"], default="subflow",
                    help="subflow=learned field; meanshift=train-only uniform mean-delta "
                         "ablation; identity=drug-agnostic sanity control")
    args = ap.parse_args()

    ckpt = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    cfg = ckpt["cfg"]
    device = get_device(cfg.get("device", "cuda"))
    data = build_data(cfg)
    model = build_subflow(cfg, data).to(device)
    model.load_state_dict(ckpt["model"]); model.eval()
    ctx = build_matching(data, device=str(device))
    beta = cfg["flow"].get("beta", 8.0)

    split = args.split or cfg["data"]["split"]
    split_path = Path(cfg["data"]["splits_dir"]) / f"{split}.json"
    keys = data.split_keys(split_path, args.fold)
    if args.max_queries:
        keys = keys[: args.max_queries]
    cand_idx = ctx.candidate_indices.cpu().numpy()
    mean_deltas = mean_valid = None
    if args.transport == "meanshift":
        train_keys = data.split_keys(split_path, "train")
        mean_deltas, mean_valid = build_mean_deltas(data, cand_idx, device,
                                                    train_keys, data.cell_lines)
    print(f"[eval] split={split} fold={args.fold} queries={len(keys)} "
          f"candidates={len(cand_idx)} score={args.score} transport={args.transport}", flush=True)

    ds = PopulationPairDataset(data, keys, args.n_source, args.n_target,
                               deterministic=True, seed=0)
    cov_all, eng_all, true_pos = [], [], []
    for qi in range(len(ds)):
        it = ds[qi]
        source = it["source_cells"][None].to(device)
        target = it["target_cells"][None].to(device)
        smask = torch.ones(1, source.shape[1], dtype=torch.bool, device=device)
        tmask = torch.ones(1, target.shape[1], dtype=torch.bool, device=device)
        cli = torch.tensor([it["cell_line_idx"]], device=device)
        ld = torch.log1p(torch.tensor([it["dose"]], dtype=torch.float32, device=device))
        cov, eng = score_query(model, ctx, source, smask, target, tmask, cli, ld,
                               cand_idx, beta, args.n_steps, args.drug_chunk, device,
                               transport=args.transport, mean_deltas=mean_deltas,
                               mean_valid=mean_valid)
        cov_all.append(cov); eng_all.append(eng)
        true_pos.append(int(ctx.lib_pos(torch.tensor([it["drug_idx"]])).item()))
        if (qi + 1) % 20 == 0:
            print(f"  scored {qi+1}/{len(ds)} queries", flush=True)

    cov_all = np.stack(cov_all); eng_all = np.stack(eng_all)
    true_pos = np.array(true_pos)
    scores = cov_all if args.score == "coverage" else eng_all
    moa_same = ctx.moa_lib[torch.as_tensor(
        [data.conditions[k].drug_idx for k in keys])].cpu().numpy()

    m = retrieval_metrics(scores, true_pos, moa_same)
    for metric in ("hit@1", "hit@5", "hit@10", "mrr"):
        p, lo, hi = bootstrap_ci(scores, true_pos, metric, moa_same)
        m[metric + "_ci95"] = [round(lo, 4), round(hi, 4)]
    print("[metrics]", json.dumps({k: (round(v, 4) if isinstance(v, float) else v)
                                   for k, v in m.items()}), flush=True)

    out = Path(args.out) if args.out else Path(cfg["out"]["results_dir"])
    out.mkdir(parents=True, exist_ok=True)
    tag = f"{split}_{args.fold}_{args.transport}"
    np.savez(out / f"subflow_scores_{tag}.npz",
             coverage=cov_all, energy=eng_all, true_pos=true_pos,
             keys=np.array(keys), cand_idx=cand_idx)
    with open(out / f"subflow_report_{tag}.json", "w") as f:
        json.dump({"split": split, "fold": args.fold, "score": args.score,
                   "transport": args.transport, "n_queries": len(keys),
                   "n_candidates": len(cand_idx), "metrics": m}, f, indent=2)
    print(f"[eval] wrote scores + report to {out}", flush=True)


if __name__ == "__main__":
    main()
