#!/bin/bash
# Drug-count scaling curve: does OOD (drug_disjoint) retrieval improve as we add
# training drugs? Rising => "not enough data" hypothesis supported.
set -e
# Reference/oracle script from the original GID-Flow implementation (SubFlow scaling,
# out of scope for DART). Expects the original data/ + checkpoints/ layout; not wired
# to run standalone in this repo — see oracle/README.md.
cd "$(dirname "$0")/.."
source .venv/bin/activate 2>/dev/null || true
CFG=configs/subflow_drugdisjoint.yaml
LOG=results/subflow/scaling.log
: > "$LOG"
echo "drug-count scaling on drug_disjoint (eval on held-out test drugs, energy score)" | tee -a "$LOG"
for N in 30 60 90 130; do
  echo "===== TRAIN N_drugs=$N =====" | tee -a "$LOG"
  python scripts/train_subflow.py --config $CFG --processed data/processed/sciplex3_all.pt \
    --max-train-drugs $N --ckpt-name subflow_$N.pt 2>&1 | grep -E "scaling|e059|done" | tee -a "$LOG"
  echo "===== EVAL N_drugs=$N (OOD test) =====" | tee -a "$LOG"
  python scripts/eval_subflow_retrieval.py --checkpoint checkpoints/drug_disjoint/subflow_$N.pt \
    --split drug_disjoint --fold test --score energy --transport subflow --max-queries 80 2>&1 \
    | grep -E "metrics" | sed "s/^/N=$N /" | tee -a "$LOG"
done
echo "===== SCALING CURVE DONE =====" | tee -a "$LOG"
