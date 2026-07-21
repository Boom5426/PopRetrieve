#!/usr/bin/env bash
# Regenerate main Figures 1-6 (PDF + SVG) and their per-panel source CSVs from the
# already-computed results/ CSVs. No new experiments. One-click reproducible.
#   bash scripts/run_all_figures.sh
#   DIDR_FIG_PNG=/tmp/prev bash scripts/run_all_figures.sh   # also dump PNG previews
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PY:-python}"                             # override e.g. PY=../.venv/bin/python
$PY src/plotting/plot_main_figures.py "$@"
echo
echo "figures -> results/main_figures/*.{pdf,svg}"
echo "source  -> results/main_figures/source_data/*.csv"
