#!/usr/bin/env python
"""Train SubFlow: subpopulation-aware conditional flow matching for drug ranking.

Loss = lambda_fm * flow_matching(control->treated) + lambda_tgt * protein_target_BCE
       [+ lambda_ed * energy_distance(generated, treated) after ed_start_epoch].

The flow-matching term learns a per-cell conditional velocity field (no mean
collapse); the BCE term keeps drug identity informative; the optional energy
term fine-tunes the *generated population* to match the real treated population.

    python scripts/train_subflow.py --config configs/subflow.yaml [--debug] [--processed PATH]
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import torch
from torch.utils.data import DataLoader

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gidflow.data.collate import collate_population              # noqa: E402
from gidflow.data.population_dataset import PopulationPairDataset  # noqa: E402
from gidflow.losses.distribution import energy_distance          # noqa: E402
from gidflow.losses.drug_alignment_loss import protein_space_bce  # noqa: E402
from gidflow.models.subflow_model import SubFlowModel            # noqa: E402
from gidflow.utils import (build_data, get_device, load_config,  # noqa: E402
                           set_seed)


def build_subflow(cfg: dict, data) -> SubFlowModel:
    m, fl = cfg["model"], cfg["flow"]
    return SubFlowModel(
        n_genes=data.n_genes, n_drugs=data.ann.n_drugs, n_proteins=data.ann.n_proteins,
        drug_features=data.drug_features, n_cell_lines=data.n_cell_lines,
        pop_hidden=m.get("pop_hidden", 512), pop_dim=m.get("pop_dim", 256),
        drug_dim=m.get("drug_dim", 256), emb_dim=m.get("emb_dim", 128),
        K=fl.get("K", 4), flow_hidden=fl.get("flow_hidden", 512),
        flow_blocks=fl.get("flow_blocks", 3),
        include_source_context=fl.get("include_source_context", True),
        dropout=m.get("dropout", 0.1))


def _energy_term(model: SubFlowModel, batch, n_steps: int) -> torch.Tensor:
    """Differentiable energy-distance between generated and real treated pops.

    Mirrors SubFlowModel.generate but keeps gradients (Euler with grad), so the
    field is pushed to match the target *distribution*, not just the OT pairing.
    """
    z_source = model.source_context(batch.source_cells, batch.source_mask) \
        if model.include_source_context else None
    dc = model.drug_condition(batch.drug_idx, batch.log_dose, z_source=z_source)
    cl = model.cell_line_emb(batch.cell_line_idx)
    cond_b = torch.cat([dc["cond_partial"], cl], dim=-1)              # [B, cond_dim]
    B = batch.batch_size
    dt = 1.0 / max(1, n_steps)
    terms = []
    for b in range(B):
        sv = batch.source_mask[b].bool(); tv = batch.target_mask[b].bool()
        if sv.sum() < 2 or tv.sum() < 2:
            continue
        x = batch.source_cells[b][sv]                                # [ns, G]
        cond = cond_b[b][None, :].expand(x.shape[0], model.cond_dim)
        for i in range(n_steps):
            t = x.new_full((x.shape[0],), i * dt)
            x = x + dt * model.field(x, t, cond)
        terms.append(energy_distance(x, batch.target_cells[b][tv]))
    if not terms:
        return batch.source_cells.sum() * 0.0
    return torch.stack(terms).mean()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--debug", action="store_true")
    ap.add_argument("--processed", default=None, help="override data.processed_path")
    ap.add_argument("--max-train-drugs", type=int, default=None,
                    help="subsample the training DRUG set to N (data-scaling curve)")
    ap.add_argument("--ckpt-name", default="subflow_last.pt")
    args = ap.parse_args()
    cfg = load_config(args.config)
    if args.processed:
        cfg["data"]["processed_path"] = args.processed
    set_seed(cfg.get("seed", 0))
    device = get_device(cfg.get("device", "cuda"))

    tcfg, fcfg = cfg["train"], cfg["flow"]
    if args.debug:
        tcfg.update(epochs=3, batch_size=8, num_workers=0, max_train_conditions=48)
        cfg["eval"]["every"] = 1

    proc = Path(cfg["data"]["processed_path"])
    if not proc.exists():
        raise FileNotFoundError(
            f"processed data not found: {proc}. Run scripts/prepare_sciplex3.py first "
            f"(or pass --processed data/processed/sciplex3_k562_24h.pt).")
    data = build_data(cfg)
    print("[data]", data.summary(), flush=True)
    assert data.drug_features is not None, "drug_features missing; run build_drug_features.py"

    model = build_subflow(cfg, data).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"[model] SubFlow params={n_params/1e6:.2f}M cond_dim={model.cond_dim} "
          f"K={model.K} device={device}", flush=True)

    split_path = Path(cfg["data"]["splits_dir"]) / f"{cfg['data']['split']}.json"
    train_keys = data.split_keys(split_path, "train")
    if args.max_train_drugs is not None:
        import numpy as _np
        drugs = sorted({data.conditions[k].drug_idx for k in train_keys})
        rng = _np.random.default_rng(cfg.get("seed", 0))
        keep = set(rng.choice(drugs, min(args.max_train_drugs, len(drugs)), replace=False).tolist())
        train_keys = [k for k in train_keys if data.conditions[k].drug_idx in keep]
        print(f"[scaling] limited to {len(keep)} train drugs -> {len(train_keys)} conditions", flush=True)
    if args.debug:
        train_keys = train_keys[: tcfg["max_train_conditions"]]
    print(f"[split] {cfg['data']['split']}: train_conditions={len(train_keys)}", flush=True)

    ds = PopulationPairDataset(data, train_keys, tcfg["n_source"], tcfg["n_target"])
    loader = DataLoader(ds, batch_size=tcfg["batch_size"], shuffle=True,
                        num_workers=tcfg.get("num_workers", 6), collate_fn=collate_population,
                        drop_last=True, persistent_workers=tcfg.get("num_workers", 6) > 0)

    prot = torch.as_tensor(data.ann.protein_targets, device=device)   # [n_drugs, P]
    annotated = (prot.sum(1) > 0)

    opt = torch.optim.AdamW(model.parameters(), lr=tcfg["lr"],
                            weight_decay=tcfg.get("weight_decay", 1e-5))
    use_bf16 = device.type == "cuda" and torch.cuda.is_bf16_supported()
    ckpt_dir = Path(cfg["out"]["ckpt_dir"]); ckpt_dir.mkdir(parents=True, exist_ok=True)

    for epoch in range(tcfg["epochs"]):
        model.train()
        t0 = time.time()
        agg = {"total": 0.0, "fm": 0.0, "bce": 0.0, "ed": 0.0, "n": 0}
        use_ed = fcfg.get("lambda_ed", 0.0) > 0 and epoch >= fcfg.get("ed_start_epoch", 10**9)
        last_batch = None
        for batch in loader:
            batch = batch.to(device); last_batch = batch
            opt.zero_grad(set_to_none=True)
            # bf16 autocast around the field/encoders; energy term kept in fp32
            with torch.autocast(device_type=device.type, dtype=torch.bfloat16, enabled=use_bf16):
                out = model.fm_loss(batch)
                bce = protein_space_bce(out["target_logits"], prot[batch.drug_idx],
                                        annotated[batch.drug_idx],
                                        pos_weight=tcfg.get("bce_pos_weight", 20.0))
            fm = out["fm"].float()
            total = fcfg.get("lambda_fm", 1.0) * fm + fcfg.get("lambda_tgt", 1.0) * bce.float()
            ed = torch.zeros((), device=device)
            if use_ed:
                ed = _energy_term(model, batch, fcfg.get("ed_n_steps", 4)).float()
                total = total + fcfg["lambda_ed"] * ed
            total.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), tcfg.get("grad_clip", 1.0))
            opt.step()
            bs = batch.batch_size
            agg["total"] += total.item() * bs; agg["fm"] += fm.item() * bs
            agg["bce"] += bce.item() * bs; agg["ed"] += float(ed) * bs; agg["n"] += bs

        n = max(1, agg["n"])
        dv = model.delta_variance(last_batch).item() if last_batch is not None else 0.0
        collapse = " COLLAPSE?" if dv < 1e-6 and epoch > 0 else ""
        print(f"[e{epoch:03d}] total={agg['total']/n:.4f} fm={agg['fm']/n:.4f} "
              f"bce={agg['bce']/n:.4f} ed={agg['ed']/n:.4f} delta_var={dv:.5f}{collapse} "
              f"({time.time()-t0:.1f}s)", flush=True)

    torch.save({"model": model.state_dict(), "cfg": cfg, "epoch": tcfg["epochs"] - 1},
               ckpt_dir / args.ckpt_name)
    print(f"[done] saved -> {ckpt_dir/args.ckpt_name}", flush=True)


if __name__ == "__main__":
    main()
