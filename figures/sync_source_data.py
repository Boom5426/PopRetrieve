#!/usr/bin/env python
"""Keep figures/source_data/ honest against the files the panels actually read.

WHY THIS EXISTS. figures/source_data/ ships the per-panel data so a reader can check a figure
without re-running an experiment. Nothing generated those files: they were copied by hand, there
was no record of what each one mirrored, and they drifted. The 2026-07-27 audit found four:

  * ed2_power_analysis.csv and ed2_divergence_stratified.csv still carried the pre-sentinel-fix
    MoA-nDCG sample sizes (n = 191 per stratum, n for 80% power = 27,794). Those are exactly the
    numbers CORRECTIONS.md R2 retracts, and the Extended Data Fig. 2 caption already states the
    corrected ones, so the released source data contradicted the caption above it.
  * fig4g_exp13_projection.csv held the 37-row QUICK sanity subset rather than the 239-row real
    run, i.e. the denominator behind the retracted "0 of 37" (R13).
  * fig5a_theoretical_boundary.csv was 104 rows against the live 120.

In every case the PANEL was right (it reads results/ directly) and the released mirror was wrong,
which is the worst way round: the figure is defensible and the file offered to check it is not.

TWO KINDS OF FILE LIVE IN source_data/, and the point of this script is that they stop being
indistinguishable.

  MIRRORS   a byte-for-byte copy of one file under results/. Regenerated here. Never edit by hand.
  DERIVED   a hand-built view (a column projection, a filtered subset, a hand-entered constant)
            with no single upstream file to copy. This script does not rewrite them; it only
            asserts that the parent it was derived from still exists, so a deleted or renamed
            upstream is caught instead of silently leaving an orphan.
  PRIMARY   read directly by a panel, so it IS the input and has no upstream at all. Listed in
            source_data/README.md, untouched here.

Usage:
    python figures/sync_source_data.py            # rewrite every MIRROR from its live parent
    python figures/sync_source_data.py --check    # exit 1 if any MIRROR has drifted, write nothing
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SD = REPO / "figures" / "source_data"

# mirror filename -> the file under results/ it is a copy of.
# A file belongs here ONLY if a straight copy is correct. If the panel needs a projection or a
# subset, it belongs in DERIVED instead, so that nobody "fixes" the mirror by overwriting a view.
MIRRORS: dict[str, str] = {
    "ed2_divergence_stratified.csv": "results/exp17_true_divergence_subset/divergence_stratified.csv",
    "ed2_power_analysis.csv":        "results/exp17_true_divergence_subset/power_analysis.csv",
    "fig3b_task_heatmap.csv":        "results/exp08_signature_baselines/summary_by_task.csv",
    "fig4d_recommendation_vs_outcome.csv": "results/exp12_partial_observed_retrieval/recommendation_vs_outcome.csv",
    "fig4g_exp13_projection.csv":    "results/exp13_real_data_projection/projection.csv",
    "fig5a_theoretical_boundary.csv": "results/exp11_hir_benchmark/theoretical_boundary.csv",
}

# derived view -> the parent it was built from. Not rewritten; existence-checked only.
DERIVED: dict[str, str] = {
    "fig3a_hit1_ladder.csv":          "results/exp08_signature_baselines/summary.csv",
    "fig3c_regret_reduction.csv":     "results/exp12_partial_observed_retrieval/per_query_scores.csv",
    "fig4ef_gate_divergence.csv":     "results/exp16_gate_diagnosis/_merged_query_divergence.csv",
    "fig6b_predictor_gaps.csv":       "results/exp09_predict_then_rank/summary.csv",
    "fig6cd_structure_diagnostics.csv": "results/exp09_structure_diagnostics/exp09_structure_diagnostics_summary.csv",
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="report drift and exit 1 without writing anything")
    args = ap.parse_args()

    drifted, missing, synced = [], [], []

    for name, rel in MIRRORS.items():
        mirror, live = SD / name, REPO / rel
        if not live.exists():
            missing.append((name, rel))
            continue
        same = mirror.exists() and mirror.read_bytes() == live.read_bytes()
        if same:
            continue
        drifted.append((name, rel))
        if not args.check:
            shutil.copyfile(live, mirror)
            synced.append(name)

    for name, rel in DERIVED.items():
        if not (REPO / rel).exists():
            missing.append((name, rel + "  (parent of a DERIVED view)"))

    for name, rel in missing:
        print(f"  MISSING PARENT  {name}  <-  {rel}")
    for name, rel in drifted:
        print(f"  {'DRIFTED' if args.check else 'SYNCED '}         {name}  <-  {rel}")

    if missing:
        # A missing parent is never acceptable: the mirror can no longer be checked against
        # anything, so the figure's provenance claim is unbacked.
        print(f"\nFAIL: {len(missing)} source_data file(s) have no live parent.")
        return 1
    if args.check and drifted:
        print(f"\nFAIL: {len(drifted)} mirror(s) drifted. Run without --check to resync.")
        return 1
    print(f"\nOK: {len(MIRRORS)} mirrors, {len(DERIVED)} derived views"
          + (f", {len(synced)} resynced." if synced else ", none drifted."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
