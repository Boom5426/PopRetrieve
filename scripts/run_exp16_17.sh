#!/usr/bin/env bash
# Reproduce the exp16/17 gate-diagnosis + true-divergence audit end to end.
#
# PREREQUISITE: exp12 must be re-run with the true_divergence patch so that
# results/exp12_partial_observed_retrieval/per_query_scores.csv carries the
# 'true_divergence' column. This script re-runs exp12 FULL first (add --skip-exp12
# to reuse an existing patched CSV), then exp16, exp17, and the verdict generator.
#
#   bash scripts/run_exp16_17.sh            # full: re-run exp12 FULL then audit
#   bash scripts/run_exp16_17.sh --skip-exp12   # reuse patched exp12 CSV
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=src
PY=${PY:-python}

if [[ "${1:-}" != "--skip-exp12" ]]; then
  echo "[1/4] exp12 FULL (patched, emits true_divergence) ..."
  $PY src/experiments/exp12_partial_observed_retrieval.py
fi
echo "[2/4] exp16 gate diagnosis (Phase 1 + Phase 2) ..."
$PY src/experiments/exp16_gate_diagnosis.py
echo "[3/4] exp17 true-divergence stratification + power ..."
$PY src/experiments/exp17_true_divergence_subset.py
echo "[4/4] verdict document ..."
$PY src/experiments/exp16_17_verdict.py
echo "Done. See results/exp16_17_verdict.md"
