#!/usr/bin/env python
"""Keep figures/source_data/ honest against the files the panels actually read.

WHY THIS EXISTS. figures/source_data/ ships the per-panel data so a reader can check a figure
without re-running an experiment. Nothing generated those files: they were copied by hand, there
was no record of what each one mirrored, and they drifted. The 2026-07-27 audit found four:

  * ed2_power_analysis.csv and ed2_divergence_stratified.csv still carried the pre-sentinel-fix
    MoA-nDCG sample sizes (n = 191 per stratum, n for 80% power = 27,794). Those are exactly the
    numbers CORRECTIONS.md R2 retracts, and the Extended Data Fig. 2 caption already states the
    corrected ones, so the released source data contradicted the caption above it.
  * fig3g_exp13_projection.csv held the 37-row QUICK sanity subset rather than the 239-row real
    run, i.e. the denominator behind the retracted "0 of 37" (R13).
  * fig4a_theoretical_boundary.csv was 104 rows against the live 120.

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
    "fig2b_task_heatmap.csv":        "results/exp08_signature_baselines/summary_by_task.csv",
    "fig3d_recommendation_vs_outcome.csv": "results/exp12_partial_observed_retrieval/recommendation_vs_outcome.csv",
    "fig3g_exp13_projection.csv":    "results/exp13_real_data_projection/projection.csv",
    "fig4a_theoretical_boundary.csv": "results/exp11_hir_benchmark/theoretical_boundary.csv",
    # ADDED 2026-09-03, and the reason is the failure this whole module exists to prevent.
    # These two feed Figure 3 panels h, i, j and k. figures/source_data/README.md called them
    # PRIMARY ("nothing regenerates it") and they were in none of the three tables here, so when
    # the U-arm Class-C results were installed into results/upgrade/ the two views under
    # figures/ stayed on the V-arm run and nothing could notice: the panels built clean off
    # numbers their own results directory had already replaced.
    "fig3hi_class_c_functional.csv": "results/upgrade/class_c_functional_oracle.csv",
    "fig3hi_class_c_potency.csv":    "results/upgrade/class_c_magnitude_control_v2.csv",

    # FIGURES 5 AND 6, added 2026-09-03 with the split. Every panel on both pages reads one of
    # these through figures/phase2_data.py, and none of them was under sync before: the Phase-II
    # rebuild landed eight panels on Figure 5 without source data while the other four figures
    # had it. The two per-query files those panels read are large and are projected instead, in
    # GENERATED below.
    "fig5b_oracle_ladder.csv":        "results/phase2_transition/phase_a/summary.csv",
    "fig5bd_oracle_deltas.csv":       "results/phase2_transition/phase_a/delta_vs_reference.csv",
    "fig5c_decision_relevance.csv":   "results/phase2_transition/synthesis/gate3_decision_relevance.csv",
    "fig5e_headroom_null.json":       "results/phase2_transition/bottleneck/summary.json",
    "fig5g_interaction_checks.json":  "results/phase2_transition/gate1_interaction/checks.json",
    "fig5h_conditional_regression.csv": "results/phase2_transition/bottleneck/regression.csv",
    "fig6bcd_predicted_summary.csv":  "results/phase2_transition/phase_b/summary.csv",
    "fig6cd_predicted_deltas.csv":    "results/phase2_transition/phase_b/delta_vs_reference.csv",
    "fig6cf_state_conditioned.csv":   "results/phase2_transition/phase_b_p5/summary.csv",
    "fig6c_state_conditioned_deltas.csv": "results/phase2_transition/phase_b_p5/delta_vs_reference.csv",
    "fig6g_oracle_to_prediction.csv": "results/phase2_transition/synthesis/oracle_to_prediction.csv",
}

# derived view -> the parent it was built from. Not rewritten; existence-checked only.
DERIVED: dict[str, str] = {
    "fig2c_regret_reduction.csv":     "results/exp12_partial_observed_retrieval/per_query_scores.csv",
    # PRIMARY until 2026-08-31, when panels 2e and 2f moved onto the results/ files these were
    # copied from. Both are hand-built views with no generator, so they stay DERIVED (existence
    # of the parent is checked, the content is not rewritten) rather than becoming MIRRORs: a
    # mirror is a byte-for-byte copy, and neither of these is one. They are no longer read by any
    # figure; each panel asserts its agreement with the retired view at draw time.
    "fig2e_classA_robustness.csv":    "results/exp12_partial_observed_retrieval/per_query_scores.csv",
    "fig3ef_gate_divergence.csv":     "results/exp16_gate_diagnosis/_merged_query_divergence.csv",
}
# RETIRED 2026-09-03, moved to source_data/_stale/: "fig5b_predictor_gaps.csv" (from
# results/exp09_predict_then_rank/summary.csv) and the GENERATED "fig5cd_structure_diagnostics.csv".
# Both were views of Figure 5 panels that the Phase-II rebuild removed, and after the 5/6 split
# their names point at panels that now mean something else entirely: fig5b is the oracle MRR
# ladder and fig5c the decision-correction counts. A source-data file named for a panel it does
# not describe is worse than a missing one, because a reader checks the panel against it.
# The experiments behind them are untouched and still under results/.


# generated view -> (builder, the parents it is built from).
#
# WHY THIS CATEGORY EXISTS. A DERIVED view is existence-checked only: sync verifies its parent is
# on disk and never looks at the view's contents. fig5cd_structure_diagnostics.csv sat in DERIVED
# and silently kept the numbers of a run that figures/fig5/fig5c.py's own docstring retracts (real
# 0.046, predictors ~0.009, i.e. the "5.1x collapse" claim), together with a predictor named
# scgen_cpa_linear that exists in no file under results/. The panels had moved to the faithful
# 'cells' synthesizer; the shipped Source Data had not, and nothing could notice. Nature ships
# Source Data to reviewers, so the drift was reader-visible.
#
# A GENERATED view is rebuilt from its parents on every sync and drift-checked like a MIRROR, so
# the same divergence fails the gate instead of shipping. Put a view here whenever a builder can
# be written; keep DERIVED only for hand-built views that have no generator.
def _build_fig5cd(repo: Path) -> str:
    """Structure diagnostics and induced-response divergence, faithful synthesizer only.

    Row selection mirrors what the panels plot: figures/fig5/fig5c.py selects synth='real' for
    real_blend and synth='cells' for each predictor, and figures/fig5/fig5d.py takes the same
    rows as ratios. The legacy 'gaussian' synthesizer is excluded; it measured an isotropic cloud
    rather than the predictor.
    """
    import pandas as pd

    diag = repo / "results" / "exp09_structure_diagnostics"
    sd = pd.read_csv(diag / "exp09_structure_diagnostics_summary.csv")
    g1 = pd.read_csv(diag / "gate1_response_divergence_summary.csv")
    order = ["real_blend", "average_effect", "scgen", "nearest_neighbor"]

    def pick(df, pred):
        synth = "real" if pred.startswith("real") else "cells"
        sub = df[(df.predictor == pred) & (df.synth == synth)]
        if sub.empty:
            raise KeyError(f"no row predictor={pred!r} synth={synth!r} in {diag}; "
                           f"re-run exp09_structure_diagnostics.py --synth both")
        return sub.iloc[0]

    rows = []
    for pred in order:
        s, g = pick(sd, pred), pick(g1, pred)
        rec = {"predictor": pred, "synth": s.synth}
        for c in sd.columns:
            if c not in ("synth", "predictor"):
                rec[c] = s[c]
        for c, out in [("mean", "induced_response_cosine_mean"),
                       ("std", "induced_response_cosine_std"),
                       ("median", "induced_response_cosine_median"),
                       ("count", "induced_response_cosine_n")]:
            rec[out] = g[c]
        rows.append(rec)
    return pd.DataFrame(rows).to_csv(index=False)


def _group_mean(rel: str, by: str, value: str):
    """A group-mean view of one results table, as a GENERATED view builder.

    Figure 2a plots one macro-mean per scoring method over the seven task-setting cells. Shipping
    the 63-row parent would not be the panel's data and hand-building the aggregate is how the
    released table came to be missing a whole method and carrying three pre-repair values; the
    aggregate is therefore computed here and drift-checked like any other generated view.
    """
    def build(repo: Path) -> str:
        import pandas as pd
        d = pd.read_csv(repo / rel)
        missing = [c for c in (by, value) if c not in d.columns]
        if missing:
            raise KeyError(f"{rel} no longer has {missing}; the panel that reads them would have "
                           f"failed too, so fix the panel and this together.")
        # A plain row mean equals the macro-mean only while the grid is balanced. fig2a.py
        # asserts that at draw time; assert it here too, so an unbalanced parent fails loudly
        # rather than silently rewriting the released table with a differently defined average.
        n = d.groupby(by).size()
        if n.nunique() != 1:
            raise ValueError(f"{rel} is no longer balanced across {by}: group sizes {dict(n)}. "
                             f"A row mean is not the macro-mean here; fix the parent or the builder.")
        return d.groupby(by)[value].mean().reset_index().to_csv(index=False)
    return build


def _project(rel: str, cols: list[str]):
    """A column projection of one large per-query file, as a GENERATED view builder.

    Two Figure 5 panels read a file of tens of columns and plot two or three of them. Mirroring
    the whole file byte for byte would ship 1.6 MB of columns no panel touches; projecting it
    here keeps the view small AND drift-checked, which a hand-built DERIVED view would not be.
    """
    def build(repo: Path) -> str:
        import pandas as pd
        d = pd.read_csv(repo / rel)
        missing = [c for c in cols if c not in d.columns]
        if missing:
            raise KeyError(f"{rel} no longer has {missing}; the panel that reads them would have "
                           f"failed too, so fix the panel and this together.")
        return d[cols].to_csv(index=False)
    return build


GENERATED: dict[str, tuple] = {
    # Figures 2a and 2d. DERIVED until 2026-09-07, i.e. existence-checked and never rewritten,
    # and both had drifted from the files their panels read: the 2a table was missing `mean_l2`
    # entirely (the magnitude-aware mean the figure is built around) and carried the pre-repair
    # V-statistic energy value, and the 2d table disagreed in the single cell the panel's
    # crossover reading depends on. A view that is only existence-checked will drift; these are
    # computed from their parents now.
    "fig2a_hit1_ladder.csv": (
        _group_mean("results/exp08_signature_baselines/summary.csv", "method", "hit@1"),
        ("results/exp08_signature_baselines/summary.csv",),
    ),
    "fig2d_alpha_crossover.csv": (
        _project("results/exp01_sciplex3_controlled/metrics_summary.csv",
                 ["cell_line", "alpha", "mean_cosine_hit@1", "global_energy_hit@1"]),
        ("results/exp01_sciplex3_controlled/metrics_summary.csv",),
    ),
    # Figures 5d and 5f: the two panels that read a per-query file of many columns.
    "fig5d_ceiling.csv": (
        _project("results/phase2_transition/bottleneck/bottleneck_per_query.csv",
                 ["cell_line", "drug", "RR_ref_oracle_vs_cos", "RR_pop_oracle_vs_cos",
                  "G_oracle_vs_cos"]),
        ("results/phase2_transition/bottleneck/bottleneck_per_query.csv",),
    ),
    "fig5f_recoverability.csv": (
        _project("results/phase2_transition/phase_c/gate2_observed.csv",
                 ["cell_line", "drug", "n_per_arm", "A_sup", "A_unsup"]),
        ("results/phase2_transition/phase_c/gate2_observed.csv",),
    ),
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

    for name, (build, parents) in GENERATED.items():
        absent = [p for p in parents if not (REPO / p).exists()]
        if absent:
            missing += [(name, p + "  (parent of a GENERATED view)") for p in absent]
            continue
        view = SD / name
        fresh = build(REPO)
        if view.exists() and view.read_text() == fresh:
            continue
        drifted.append((name, parents[0]))
        if not args.check:
            view.write_text(fresh)
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
    print(f"\nOK: {len(MIRRORS)} mirrors, {len(GENERATED)} generated, {len(DERIVED)} derived views"
          + (f", {len(synced)} resynced." if synced else ", none drifted."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
