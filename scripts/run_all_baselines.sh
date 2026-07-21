#!/usr/bin/env bash
# Run the full Phase-2 external-baseline comparison (exp08–exp11) then consolidate.
#
#   QUICK=1 bash scripts/run_all_baselines.sh      # fast sanity pass (reduced seeds/grid)
#   bash scripts/run_all_baselines.sh              # FULL run (paper numbers)
#   PY=/path/to/python bash scripts/run_all_baselines.sh   # override interpreter
#
# Mirrors scripts/run_all_core.sh: exp scripts honour QUICK=1 for reduced configs; FULL uses
# the per-experiment defaults below. Writes to results/exp08_*..exp11_* and finally
# results/baseline_comparison_master.csv.
set -euo pipefail
cd "$(dirname "$0")/.."

PY="${PY:-python}"
QUICK="${QUICK:-0}"

if [ "$QUICK" = "1" ]; then
  echo "== QUICK baseline pass (reduced) =="
  EXP08_ARGS="--n-seeds 2 --n-drugs 3 --n-kos 3"
  EXP09_ARGS=""            # exp09 reads QUICK=1 itself (n_seeds=2, K562+A549)
  EXP11_ARGS="--n-seeds 4 --grid 5"
  export QUICK=1
else
  echo "== FULL baseline run =="
  EXP08_ARGS="--n-seeds 10 --n-drugs 12 --n-kos 6"
  EXP09_ARGS="--n-seeds 8 --n-drugs 10"
  EXP11_ARGS="--n-seeds 12 --grid 9"
fi

echo "--- exp08 signature baselines ---"
$PY src/experiments/exp08_signature_baselines.py $EXP08_ARGS

echo "--- exp09 predict-then-rank ---"
$PY src/experiments/exp09_predict_then_rank.py $EXP09_ARGS

echo "--- exp10 PDGrapher comparison (precomputed closed-loop benchmark) ---"
$PY src/experiments/exp10_pdgrapher_comparison.py

echo "--- exp11 synthetic phase diagram ---"
$PY src/experiments/exp11_synthetic_phase_diagram.py $EXP11_ARGS

echo "--- consolidate -> results/baseline_comparison_master.csv ---"
$PY src/experiments/recompute_baselines.py

echo "== baseline comparison complete =="
