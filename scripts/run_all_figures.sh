#!/usr/bin/env bash
# Rebuild every figure in the manuscript and sync it into manuscript/latex/figures/.
#   bash scripts/run_all_figures.sh
#
# CORRECTED 2026-07-27. This script used to drive src/plotting/plot_main_figures.py, which is the
# SUPERSEDED v1 pipeline: it belongs to an earlier six-figure deck ("Distributional Inverse Drug
# Retrieval..."), it reads results/exp01_sciplex3_controlled/ which no longer exists, so it dies
# with FileNotFoundError on any clone, and even if it ran it would write a different deck into
# results/main_figures/, a directory .gitignore excludes. Neither of its outputs is what the
# manuscript compiles. The live pipeline is figures/build_all.py plus figures/build_ed.py.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PY:-python}"                             # override e.g. PY=~/.venvs/dartfig/bin/python

$PY figures/build_all.py --write               # main Figs 1-6  -> manuscript/latex/figures/figN.pdf
$PY figures/build_ed.py  --write               # Extended Data 1-7 -> manuscript/latex/figures/edfigN.pdf
$PY figures/sync_source_data.py                # per-panel source CSVs, resynced from results/

echo
echo "main figures     -> manuscript/latex/figures/fig{1..6}.pdf"
echo "extended data    -> manuscript/latex/figures/edfig{1..7}.pdf"
echo "per-panel source -> figures/source_data/  (see its README for what each file is)"
