#!/usr/bin/env bash
# Run the HIR-Bench benchmark (exp11).
#
# Usage:
#   QUICK=1 bash scripts/run_hir_benchmark.sh   # quick sanity (~40s)
#   bash scripts/run_hir_benchmark.sh            # full run (~60 min)
#
# Set PY to override the interpreter:
#   PY=/path/to/python bash scripts/run_hir_benchmark.sh

set -euo pipefail
cd "$(dirname "$0")/.."

PY="${PY:-python}"
QUICK="${QUICK:-0}"

echo "============================================"
echo "  HIR-Bench — Heterogeneous Inverse Retrieval"
echo "  Mode: $([ "$QUICK" = "1" ] && echo QUICK || echo FULL)"
echo "============================================"
echo ""

if [ "$QUICK" = "1" ]; then
    # QUICK and FULL write to the SAME directory (results/exp11_hir_benchmark/), so a QUICK run
    # silently replaces the tracked FULL tables that the manuscript quotes. PROVENANCE.md in that
    # directory records this having already happened once: results/ shipped a QUICK run reporting
    # AUC 0.5 while the manuscript quoted the FULL grid, and nothing on disk recorded the swap.
    # Refuse by default rather than repeat it.
    if [ "${ALLOW_QUICK_OVERWRITE:-0}" != "1" ] && \
       git ls-files --error-unmatch results/exp11_hir_benchmark/phase_grid_method_performance.csv >/dev/null 2>&1; then
        echo "REFUSING: QUICK mode would overwrite the tracked FULL results in" >&2
        echo "  results/exp11_hir_benchmark/  (see its PROVENANCE.md)." >&2
        echo "Re-run with ALLOW_QUICK_OVERWRITE=1 if that is what you want, and re-stamp provenance" >&2
        echo "afterwards with:  \$PY src/experiments/exp11_write_provenance.py" >&2
        exit 1
    fi
    echo "[1/2] Running HIR-Bench QUICK..."
    $PY src/experiments/exp11_hir_benchmark.py --quick --n-seeds 3
else
    echo "[1/2] Running HIR-Bench FULL..."
    $PY src/experiments/exp11_hir_benchmark.py --n-seeds 20
fi

echo ""
echo "[2/2] Verifying outputs..."
OUTDIR="results/exp11_hir_benchmark"
EXPECTED="phase_grid_method_independent.csv phase_grid_method_performance.csv phase_grid_predictability.csv theoretical_boundary.csv method_dominance.csv uncertainty_band.csv sanity_checks.csv"
MISSING=0
for f in $EXPECTED; do
    if [ ! -f "$OUTDIR/$f" ]; then
        echo "  MISSING: $OUTDIR/$f"
        MISSING=$((MISSING + 1))
    else
        LINES=$(wc -l < "$OUTDIR/$f")
        echo "  OK: $OUTDIR/$f ($LINES lines)"
    fi
done

if [ "$MISSING" -gt 0 ]; then
    echo ""
    echo "ERROR: $MISSING expected files missing"
    exit 1
fi

echo ""
echo "  All HIR-Bench outputs verified."
echo ""

# Check sanity
if grep -q ",0$" "$OUTDIR/sanity_checks.csv"; then
    echo "  WARNING: Some sanity checks FAILED"
    cat "$OUTDIR/sanity_checks.csv"
    echo ""
else
    echo "  All sanity checks PASSED"
fi

echo ""
echo "HIR-Bench complete."
