"""Smoke tests for the external retrieval baselines (shape / finiteness / sanity).

Builds small synthetic controlled- and labeled-style queries where a ``covers-both``
candidate is aligned with the query response direction and distractors are random, then
asserts every baseline returns a finite score per candidate and ranks the aligned
candidate at #1 on this easy (non-divergent) query.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np

from baselines.base import normalize_query
from baselines.cmap_signature import CMapSignatureRetrieval, cmap_scores
from baselines.pca_latent_retrieval import PCALatentRetrieval, pca_latent_scores

G = 200


def _synth(seed=0):
    rng = np.random.default_rng(seed)
    ctrl = rng.normal(size=G) * 0.1
    gt_dir = rng.normal(size=G)

    def pop(direction, n=80, noise=0.5):
        return (ctrl + direction[None, :] + rng.normal(size=(n, G)) * noise).astype(np.float32)

    Q = pop(gt_dir, 120)
    cands = {"covers-both": pop(gt_dir, 80)}
    for i in range(6):
        cands[f"distractor{i}"] = pop(rng.normal(size=G), 80)
    return ctrl, Q, cands, gt_dir


def _controlled_query():
    ctrl, Q, cands, _ = _synth(0)
    rng = np.random.default_rng(1)
    q = {"target": Q, "target_labels": (rng.random(120) < 0.5).astype(int),
         "pseudo_control": ctrl, "candidates": cands}
    return normalize_query(q, query_id="ctrl", ground_truth="covers-both")


def _labeled_query():
    ctrl, Q, cands, _ = _synth(2)
    rng = np.random.default_rng(3)
    cd = {n: (P, (rng.random(len(P)) < 0.5).astype(int), ctrl) for n, P in cands.items()}
    q = {"target": Q, "tlab": (rng.random(len(Q)) < 0.5).astype(int),
         "ctrl_T": ctrl, "cands": cd}
    return normalize_query(q, query_id="lab", ground_truth="covers-both")


def _check_finite_and_top(nq, score_map):
    vals = np.array([score_map[n] for n in nq.names], dtype=float)
    assert np.all(np.isfinite(vals)), vals
    assert len(vals) == len(nq.names)
    return int(np.argmax(vals))


def test_cmap_cosine_controlled():
    nq = _controlled_query()
    assert _check_finite_and_top(nq, CMapSignatureRetrieval("cosine").score(nq)) == nq.gt_index


def test_cmap_wtcs_controlled():
    nq = _controlled_query()
    assert _check_finite_and_top(nq, cmap_scores(nq, scoring="wtcs")) == nq.gt_index


def test_pca_mean_controlled():
    nq = _controlled_query()
    assert _check_finite_and_top(nq, PCALatentRetrieval(mode="mean").score(nq)) == nq.gt_index


def test_pca_dist_controlled():
    nq = _controlled_query()
    assert _check_finite_and_top(nq, pca_latent_scores(nq, mode="dist")) == nq.gt_index


def test_baselines_on_labeled_query():
    nq = _labeled_query()
    for smap in (CMapSignatureRetrieval("cosine").score(nq),
                 CMapSignatureRetrieval("wtcs").score(nq),
                 PCALatentRetrieval(mode="mean").score(nq),
                 PCALatentRetrieval(mode="dist").score(nq)):
        top = _check_finite_and_top(nq, smap)
        assert top == nq.gt_index


def test_normalize_query_roundtrip_shapes():
    nq = _controlled_query()
    assert nq.Q.shape[1] == G
    assert nq.query_delta.shape == (G,)
    assert all(c.delta.shape == (G,) for c in nq.candidates)
