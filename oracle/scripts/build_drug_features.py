#!/usr/bin/env python
"""Build Morgan ECFP4 fingerprints [n_drugs, 2048] indexed by drug_order.json.

Drugs without a SMILES (e.g. 'control') get a zero vector and are excluded from
the candidate library at match time.

    python scripts/build_drug_features.py \
        --annotation-dir data/annotation --n-bits 2048 --radius 2
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--annotation-dir", default="data/annotation")
    ap.add_argument("--n-bits", type=int, default=2048)
    ap.add_argument("--radius", type=int, default=2)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    from rdkit import Chem, RDLogger
    from rdkit.Chem import rdFingerprintGenerator
    RDLogger.DisableLog("rdApp.*")

    ann = Path(args.annotation_dir)
    drug_order = json.load(open(ann / "drug_order.json"))
    master = pd.read_csv(ann / "drug_annotation_master.csv")
    name2smiles = dict(zip(master["drug_name"].astype(str), master["smiles"]))

    gen = rdFingerprintGenerator.GetMorganGenerator(radius=args.radius, fpSize=args.n_bits)
    fps = np.zeros((len(drug_order), args.n_bits), dtype=np.float32)
    n_ok, n_fail = 0, 0
    for i, name in enumerate(drug_order):
        smi = name2smiles.get(name, None)
        if smi is None or (isinstance(smi, float) and np.isnan(smi)) or str(smi).strip() == "":
            n_fail += 1
            continue
        mol = Chem.MolFromSmiles(str(smi))
        if mol is None:
            n_fail += 1
            continue
        fp = gen.GetFingerprintAsNumPy(mol).astype(np.float32)
        fps[i] = fp
        n_ok += 1

    out = Path(args.out) if args.out else ann / "drug_morgan_ecfp4.npy"
    np.save(out, fps)
    print(f"[build_drug_features] drugs={len(drug_order)} encoded={n_ok} zero(no-smiles)={n_fail}")
    print(f"[build_drug_features] mean bits set = {fps.sum(1).mean():.1f} -> {out}")


if __name__ == "__main__":
    main()
