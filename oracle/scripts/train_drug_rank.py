#!/usr/bin/env python
"""Train DrugRank-Flow (two-phase: BCE warmup -> BCE + full-library InfoNCE).

    python scripts/train_drug_rank.py --config configs/drug_rank.yaml [--debug]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gidflow.data.collate import collate_population           # noqa: E402
from gidflow.data.population_dataset import PopulationPairDataset  # noqa: E402
from gidflow.eval_retrieval import evaluate_retrieval          # noqa: E402
from gidflow.losses.drug_alignment_loss import (               # noqa: E402
    FullLibraryInfoNCE, protein_space_bce, recon_loss)
from gidflow.training.drug_gallery import DrugGallery          # noqa: E402
from gidflow.training.phase_scheduler import PhaseScheduler    # noqa: E402
from gidflow.utils import (build_data, build_matching, build_model,  # noqa: E402
                           get_device, load_config, set_seed)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args()
    cfg = load_config(args.config)
    set_seed(cfg.get("seed", 0))
    device = get_device(cfg.get("device", "cuda"))

    tcfg = cfg["train"]
    if args.debug:
        tcfg["epochs"] = 4
        tcfg["phase1_epochs"] = 2
        tcfg["batch_size"] = 16
        tcfg["max_train_conditions"] = 64
        cfg["eval"]["query_batch"] = 16

    data = build_data(cfg)
    print("[data]", data.summary(), flush=True)
    model = build_model(cfg, data).to(device)
    ctx = build_matching(data, device=str(device))
    gallery = DrugGallery(ctx, refresh_every=tcfg.get("gallery_refresh_every", 1))
    infonce = FullLibraryInfoNCE(soft_weight=tcfg.get("moa_soft_weight", 0.3))
    sched = PhaseScheduler(
        phase1_epochs=tcfg["phase1_epochs"],
        temp0=tcfg.get("temp0", 0.20), temp1=tcfg.get("temp1", 0.10),
        temp_end=tcfg.get("temp_end", 120),
        lam0=tcfg.get("lam0", 50.0), lam1=tcfg.get("lam1", 5.0),
        lam_end=tcfg.get("lam_end", 120), lambda_recon=tcfg.get("lambda_recon", 0.1))

    # split
    split_path = Path(cfg["data"]["splits_dir"]) / f"{cfg['data']['split']}.json"
    train_keys = data.split_keys(split_path, "train")
    val_keys = data.split_keys(split_path, cfg["data"].get("val_fold", "val"))
    if not val_keys:
        val_keys = data.split_keys(split_path, "test")
    if args.debug:
        train_keys = train_keys[: tcfg["max_train_conditions"]]
        val_keys = val_keys[:64]
    print(f"[split] {cfg['data']['split']}: train={len(train_keys)} val={len(val_keys)}", flush=True)

    ds = PopulationPairDataset(data, train_keys, tcfg["n_source"], tcfg["n_target"])
    loader = DataLoader(ds, batch_size=tcfg["batch_size"], shuffle=True,
                        num_workers=tcfg.get("num_workers", 4), collate_fn=collate_population,
                        drop_last=True, persistent_workers=tcfg.get("num_workers", 4) > 0)

    prot_labels = torch.as_tensor(data.ann.protein_targets, device=device)      # [n_drugs, P]
    annotated = (prot_labels.sum(1) > 0)                                        # [n_drugs]

    opt = torch.optim.AdamW(model.parameters(), lr=tcfg["lr_phase1"],
                            weight_decay=tcfg.get("weight_decay", 1e-5))
    use_bf16 = device.type == "cuda" and torch.cuda.is_bf16_supported()
    ckpt_dir = Path(cfg["out"]["ckpt_dir"]); ckpt_dir.mkdir(parents=True, exist_ok=True)

    best = {"p1": -1e9, "p2": -1e9}
    step = 0
    for epoch in range(tcfg["epochs"]):
        st = sched.state(epoch)
        for g in opt.param_groups:
            g["lr"] = tcfg["lr_phase1"] if st.phase == 1 else tcfg["lr_phase2"]
        model.train()
        t0 = time.time()
        agg = {"total": 0.0, "bce": 0.0, "recon": 0.0, "infonce": 0.0, "n": 0}
        for batch in loader:
            batch = batch.to(device)
            opt.zero_grad(set_to_none=True)
            with torch.autocast(device_type=device.type, dtype=torch.bfloat16, enabled=use_bf16):
                out = model(batch)
                labels = prot_labels[batch.drug_idx]
                ann_b = annotated[batch.drug_idx]
                bce = protein_space_bce(out["target_logits"], labels, ann_b,
                                        pos_weight=tcfg.get("bce_pos_weight", 20.0))
                if st.phase == 1:
                    rdelta = model.gap_encoder.reconstruct_delta(out["gap_pre"])
                    rec = recon_loss(rdelta, batch.source_cells, batch.target_cells,
                                     batch.source_mask, batch.target_mask)
                    total = bce + st.lambda_recon * rec
                    inf = torch.zeros((), device=device)
                else:
                    gbase = gallery.get(model, step)
                    gcond = model.gallery_cond(gbase, batch.log_dose)
                    res = infonce(out["gap_emb"], out["drug_proj_cond"], gcond,
                                  ctx.lib_pos(batch.drug_idx),
                                  ctx.moa_same_lib(batch.drug_idx),
                                  ctx.moa_same_batch(batch.drug_idx),
                                  temperature=st.temperature)
                    inf = res["infonce"]
                    total = inf + st.lambda_dt * bce
                    rec = torch.zeros((), device=device)
            total.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), tcfg.get("grad_clip", 1.0))
            opt.step()
            step += 1
            bs = batch.batch_size
            agg["total"] += total.item() * bs; agg["bce"] += bce.item() * bs
            agg["recon"] += float(rec) * bs; agg["infonce"] += float(inf) * bs; agg["n"] += bs

        n = max(1, agg["n"])
        # profile diversity: spread of gallery embeddings (collapse guard)
        with torch.no_grad():
            gb = model.encode_all_drugs()["drug_proj"][ctx.candidate_indices]
            gb = torch.nn.functional.normalize(gb, dim=-1)
            diversity = (1 - (gb @ gb.t())).mean().item()
        msg = (f"[e{epoch:03d} P{st.phase}] total={agg['total']/n:.4f} bce={agg['bce']/n:.4f} "
               f"recon={agg['recon']/n:.4f} infonce={agg['infonce']/n:.4f} "
               f"temp={st.temperature:.3f} lam={st.lambda_dt:.1f} div={diversity:.3f} "
               f"({time.time()-t0:.1f}s)")

        # periodic val retrieval
        if (epoch + 1) % cfg["eval"].get("every", 1) == 0 or epoch == tcfg["epochs"] - 1:
            ev = evaluate_retrieval(model, data, ctx, val_keys, device,
                                    n_source=tcfg["n_source"], n_target=tcfg["n_target"],
                                    query_batch=cfg["eval"]["query_batch"])
            m = ev["metrics"]
            msg += (f" | val hit@1={m['hit@1']:.3f} hit@10={m['hit@10']:.3f} "
                    f"mrr={m['mrr']:.3f} medrank={m['median_rank']:.0f}/{ev['scores'].shape[1]} "
                    f"moaAUC={m.get('moa_auc', float('nan')):.3f}")
            score_key = "moa_auc" if st.phase == 1 else "hit@10"
            val = m.get(score_key, 0.0)
            tag = "p1" if st.phase == 1 else "p2"
            if val > best[tag]:
                best[tag] = val
                torch.save({"model": model.state_dict(), "cfg": cfg, "epoch": epoch,
                            "metrics": m, "phase": st.phase},
                           ckpt_dir / f"{'phase1_best' if st.phase==1 else 'phase2_best'}.pt")
                msg += f"  <=best {tag}"
        print(msg, flush=True)

    torch.save({"model": model.state_dict(), "cfg": cfg, "epoch": tcfg["epochs"] - 1},
               ckpt_dir / "last.pt")
    print(f"[done] best={best} ckpts in {ckpt_dir}", flush=True)


if __name__ == "__main__":
    main()
