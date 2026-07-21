"""Smoke tests for the PDGrapher adapter's drug<->target conversions.

Uses a small synthetic drug<->target map and score dicts (no data files needed) so the
conversion logic is tested in isolation; exp10 exercises the real benchmark loader.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np

from baselines.pdgrapher_adapter import (
    DrugTargetMap, target_ranking_to_drug_ranking, drug_ranking_to_target_ranking,
)

# drugA hits geneX; drugB hits geneX,geneY; drugC hits geneZ
D2T = {"drugA": ["geneX"], "drugB": ["geneX", "geneY"], "drugC": ["geneZ"]}


def test_map_bidirectional():
    m = DrugTargetMap(D2T)
    assert set(m.targets_of("drugB")) == {"geneX", "geneY"}
    assert set(m.drugs_of("geneX")) == {"drugA", "drugB"}
    assert m.drugs_of("geneZ") == ["drugC"]


def test_target_to_drug_max_agg():
    m = DrugTargetMap(D2T)
    # geneX is the only good target
    tscore = {"geneX": 1.0, "geneY": 0.0, "geneZ": 0.0}
    ds = target_ranking_to_drug_ranking(tscore, m, agg="max")
    # drugA and drugB (both hit geneX) score 1.0; drugC (geneZ) scores 0.0
    assert ds["drugA"] == 1.0 and ds["drugB"] == 1.0
    assert ds["drugC"] == 0.0
    # ranking puts drugA/drugB above drugC
    assert max(ds, key=ds.get) in {"drugA", "drugB"}


def test_target_to_drug_unknown_drug_is_neg_inf():
    m = DrugTargetMap(D2T)
    ds = target_ranking_to_drug_ranking({"geneX": 1.0}, m, drugs=["drugA", "drugUnknown"])
    assert ds["drugA"] == 1.0
    assert ds["drugUnknown"] == float("-inf")


def test_drug_to_target_max_agg():
    m = DrugTargetMap(D2T)
    dscore = {"drugA": 0.2, "drugB": 0.9, "drugC": 0.5}
    ts = drug_ranking_to_target_ranking(dscore, m, agg="max")
    # geneX hit by drugA(0.2),drugB(0.9) -> max 0.9; geneY by drugB -> 0.9; geneZ by drugC -> 0.5
    assert abs(ts["geneX"] - 0.9) < 1e-9
    assert abs(ts["geneY"] - 0.9) < 1e-9
    assert abs(ts["geneZ"] - 0.5) < 1e-9


def test_drug_to_target_mean_agg():
    m = DrugTargetMap(D2T)
    dscore = {"drugA": 0.2, "drugB": 0.8}
    ts = drug_ranking_to_target_ranking(dscore, m, targets=["geneX"], agg="mean")
    assert abs(ts["geneX"] - 0.5) < 1e-9   # mean(0.2, 0.8)
