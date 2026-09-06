#!/usr/bin/env bash
# Phase 2 (P0-A): re-run every legacy result that depends on a population scorer, under whichever
# estimator POPRETRIEVE_ESTIMATOR names. Run it twice, once per arm, in two separate checkouts, so
# the two results/ trees can be diffed file by file.
#
#   POPRETRIEVE_ESTIMATOR=v bash analysis/estimator_audit/run_legacy_suite.sh
#   POPRETRIEVE_ESTIMATOR=u bash analysis/estimator_audit/run_legacy_suite.sh
#
# Two kinds of script are listed.
#
#   1. Anything that CALLS score_energy / score_mmd_rbf / score_coverage / energy_distance /
#      mmd_rbf. The list was taken from a grep of the whole tree, recorded in
#      docs/phase2/P0_CLAIM_DEPENDENCY_MATRIX.md.
#   2. Anything that READS another experiment's output, whether or not it calls a kernel itself.
#
# The second kind was missing until 2026-09-03 and the omission cost a reversal. This header used
# to say that everything outside (1) is "estimator-independent", which confuses estimator-
# independent CODE with estimator-independent OUTPUT: exp16 calls no kernel at all and is a pure
# re-analysis of exp12's per-query CSV, so leaving it out left a V-arm merge sitting downstream of
# a U-arm exp12, and Figure 3 asserted two different gate verdict splits in two different panels.
# See docs/phase2/POST_REPAIR_MASTER_RESULTS.md section A5c. Anything added to this file from here
# must be placed AFTER whatever it reads.
#
# What is NOT here, and why:
#   analysis/class_c/class_c_functional_oracle.py   needs GDSC2_fitted_dose_response.xlsx, which is
#                                                   not redistributable and is absent from both
#                                                   machines (DATA.md). Blocked, not skipped.
#   analysis/natural/*                              cosine-based; no population scorer is called.
#   analysis/tahoe_pilot/*                          cosine and logistic probes only.
set -uo pipefail
cd "$(dirname "$0")/../.."
PY="${PY:-$HOME/anaconda3/envs/boom/bin/python}"
EST="${POPRETRIEVE_ESTIMATOR:-v}"
export POPRETRIEVE_ESTIMATOR="$EST"
export PYTHONPATH="src:${PYTHONPATH:-}"
LOG="results/_estimator_audit_run_${EST}.log"
: > "$LOG"

run () {
  echo "=== [$EST] $* ===" | tee -a "$LOG"
  local t0=$SECONDS
  if "$@" >> "$LOG" 2>&1; then
    echo "    OK   ($((SECONDS - t0))s)" | tee -a "$LOG"
  else
    # A failure is recorded and the suite continues: one missing input must not silently truncate
    # the audit table, and it must not look like a completed run either.
    echo "    FAIL ($((SECONDS - t0))s)  <-- see $LOG" | tee -a "$LOG"
  fi
}

# 1. core retrieval (exp01-07). exp01/02/03/05 rank through retrieval.rankers, which calls the
#    energy kernel; exp06 calls it directly and through coverage_aggregate.
run $PY src/experiments/exp01_sciplex3_controlled.py --n-seeds 20
run $PY src/experiments/exp02_divergence_gate.py     --n-seeds 20
run $PY src/experiments/exp03_crossline_semireal.py  --n-seeds 10 --n-drugs 15
run $PY src/experiments/exp04_cd34_negative.py       --n-seeds 8
run $PY src/experiments/exp05_frangieh_natural.py    --n-seeds 20
run $PY src/experiments/exp06_theory_limits.py
run $PY src/experiments/exp07_ranking_flip.py

# 2. signature baselines and predict-then-rank (exp08-09)
run $PY src/experiments/exp08_signature_baselines.py
run $PY src/experiments/exp09_predict_then_rank.py
run $PY src/experiments/exp09_structure_diagnostics.py

# 3. HIR-Bench and the synthetic phase diagram (exp11)
run $PY src/experiments/exp11_hir_benchmark.py
run $PY src/experiments/exp11_synthetic_phase_diagram.py

# 4. partial-observation retrieval and the projection (exp12, exp13)
run $PY src/experiments/exp12_partial_observed_retrieval.py
run $PY src/experiments/exp13_real_data_projection.py

# 4b. the pure re-analyses of exp12. They call no energy kernel; they read one experiment's output,
#     which is what makes them estimator-dependent. exp17 reads the merge exp16 writes, so the
#     order here is load-bearing.
run $PY src/experiments/exp16_gate_diagnosis.py
run $PY src/experiments/exp17_true_divergence_subset.py

# 5. the individual analyses that carry a claim of their own
run $PY analysis/class_c/oracle_shape_test.py
run $PY analysis/class_c/class_c_protein_oracle.py
run $PY analysis/class_c/class_c_magnitude_control_v2.py
run $PY analysis/predictors/exp_nonadditive_gate1.py
run $PY analysis/identifiability/subpop_identifiability_landscape.py
run $PY analysis/diagnostics/protocol_validation.py

echo "=== [$EST] suite finished ===" | tee -a "$LOG"
