#!/usr/bin/env bash
# Run the core reproduction (exp01-exp06) + ranking-flip (exp07) + consolidation.
# Usage:
#   bash scripts/run_all_core.sh              # full run (manuscript seed counts)
#   QUICK=1 bash scripts/run_all_core.sh      # fast sanity pass (few seeds)
#   PY=/path/to/python bash scripts/run_all_core.sh
set -euo pipefail
cd "$(dirname "$0")/.."                        # -> repo root
PY="${PY:-python}"                             # override e.g. PY=../.venv/bin/python

if [[ "${QUICK:-0}" == "1" ]]; then
  CTRL=3; XLINE=2; DRUGS=6; CD34=2; FRAN=4; GATE=3
  echo "== QUICK sanity pass (reduced seeds) =="
else
  CTRL=20; XLINE=10; DRUGS=15; CD34=8; FRAN=20; GATE=20
  echo "== FULL reproduction run =="
fi

set -x
$PY src/experiments/exp01_sciplex3_controlled.py --n-seeds "$CTRL"
$PY src/experiments/exp02_divergence_gate.py     --n-seeds "$GATE"
$PY src/experiments/exp03_crossline_semireal.py  --n-seeds "$XLINE" --n-drugs "$DRUGS"
$PY src/experiments/exp04_cd34_negative.py       --n-seeds "$CD34"
$PY src/experiments/exp05_frangieh_natural.py    --n-seeds "$FRAN"
$PY src/experiments/exp06_theory_limits.py
$PY src/experiments/exp07_ranking_flip.py
$PY src/experiments/recompute_all.py
set +x
echo "== done: see results/all_existing_results_recomputed.csv =="
