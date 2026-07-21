#!/usr/bin/env python
"""Stamp results/exp11_hir_benchmark/ with which layer came from which grid.

HIR-Bench has two layers with very different costs:

  method-INDEPENDENT layer  (oracle labels, conflict features, observable features)
      cheap; the FULL 13,440-instance grid runs in about an hour.

  method-PERFORMANCE layer  (9 retrieval methods x up to 100 candidates x an O(n^2 d)
      population distance, per instance)
      expensive; the FULL grid does not finish in a reasonable time, which is why
      `--skip-method-perf` exists.

So the two layers in this directory can legitimately come from different grids, and a reader
must not have to guess which. Silence here is exactly the failure this project audits: before
2026-07-12 the directory held a QUICK 144-instance run whose predictability CSV said AUC 0.5
while the manuscript quoted 0.640 from an out-of-tree runner, and nothing on disk said so.

    PYTHONPATH=src python src/experiments/exp11_write_provenance.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from utils.io import results_path
from utils.logging import log, section

OUT = "exp11_hir_benchmark"

FULL_ROWS = 13440          # 672 parameter configurations x 20 seeds
QUICK_ROWS = 144           # 48 configurations x 3 seeds


def _grid_of(path: Path, rows_per_instance: int = 1) -> tuple[str, int]:
    """Infer which grid produced a table from how many instances it covers."""
    if not path.exists():
        return "absent", 0
    df = pd.read_csv(path)
    n = len(df) // max(rows_per_instance, 1)
    if "grid_id" in df.columns:
        n = df.grid_id.nunique() * (df.seed.nunique() if "seed" in df.columns else 1)
    if n >= FULL_ROWS * 0.9:
        return "FULL", len(df)
    if n <= QUICK_ROWS * 2:
        return "QUICK", len(df)
    return "PARTIAL", len(df)


def main() -> None:
    section("EXP11 provenance stamp")
    base = Path(results_path(OUT, "x")).parent
    rows = []

    checks = [
        ("phase_grid_method_independent.csv", "method-independent; PAIRS with "
                                              "method_performance for exp13's boundary fit"),
        ("phase_grid_method_independent_FULL.csv", "method-independent, FULL grid; the layer "
                                                   "the predictability model was fitted on"),
        ("phase_grid_predictability.csv", "predictability; fitted on the FULL "
                                          "method-independent layer above"),
        ("phase_grid_method_performance.csv", "method-performance (9 retrieval methods)"),
        ("method_dominance.csv", "method-performance (derived)"),
        ("uncertainty_band.csv", "method-performance (derived)"),
        ("sanity_checks.csv", "method-independent + method-performance"),
        ("theoretical_boundary.csv", "method-independent"),
    ]
    for fname, layer in checks:
        p = base / fname
        grid, n = _grid_of(p)
        # a derived table inherits the grid of the layer it was computed from
        if fname == "phase_grid_predictability.csv" and p.exists():
            d = pd.read_csv(p)
            if "n_positive" in d.columns and "n_negative" in d.columns:
                inst = int(d.iloc[0]["n_positive"] + d.iloc[0]["n_negative"])
                grid = "FULL" if inst >= FULL_ROWS * 0.9 else "QUICK"
                n = inst
        rows.append({"file": fname, "layer": layer, "grid": grid, "n_rows_or_instances": n})
        log(f"  {fname:<42s} {layer:<40s} {grid}")

    df = pd.DataFrame(rows)
    df.to_csv(base / "PROVENANCE.csv", index=False)

    note = base / "PROVENANCE.md"
    full = df[df.grid == "FULL"].file.tolist()
    quick = df[df.grid == "QUICK"].file.tolist()
    note.write_text(
        "# Which HIR-Bench grid produced which file\n\n"
        "HIR-Bench has two layers with very different costs. The method-independent layer\n"
        "(oracle labels, conflict features, observable features) runs on the FULL\n"
        f"{FULL_ROWS:,}-instance grid in about an hour. The method-performance layer scores 9\n"
        "retrieval methods against up to 100 candidates per instance with an O(n^2 d) population\n"
        "distance, and does not finish on the FULL grid in a reasonable time.\n\n"
        "They therefore come from different grids, and this file says which is which so that no\n"
        "reader has to guess.\n\n"
        f"**FULL ({FULL_ROWS:,} instances = 672 configurations x 20 seeds):**\n"
        + "".join(f"- `{f}`\n" for f in full)
        + f"\n**QUICK ({QUICK_ROWS} instances = 48 configurations x 3 seeds):**\n"
        + "".join(f"- `{f}`\n" for f in quick)
        + "\n## Why the method-independent layer is here twice\n\n"
          "`phase_grid_method_independent.csv` is the QUICK one **on purpose**. exp13's regime\n"
          "boundary fit merges it with `phase_grid_method_performance.csv` on `(grid_id, seed)`,\n"
          "and the method-performance layer only exists on the QUICK grid, so the two must come\n"
          "from the same grid or the merge is empty. (It used to fail there with an unrelated\n"
          "`KeyError` several lines later; `fit_hir_boundary` now checks and says so.)\n\n"
          "`phase_grid_method_independent_FULL.csv` is the FULL layer, and it is what the\n"
          "predictability model was actually fitted on. That is why the predictability numbers\n"
          "are FULL while the file directly above them is QUICK.\n\n"
          "**Consequence for the paper:** the regime boundary that exp13 projects onto real data\n"
          "is fitted on 72 QUICK grid cells, not on 13,440 instances. The paper says so.\n\n"
          "## Do not quote the QUICK numbers\n\n"
          "At n=144 the Hit@1 granularity alone exceeds the effect sizes being compared.\n"
          "Regenerate the FULL method-independent layer with:\n\n"
          "    PYTHONPATH=src python src/experiments/exp11_hir_benchmark.py --skip-method-perf\n\n"
          "Before 2026-07-12 this directory held only a QUICK run, whose predictability CSV\n"
          "reported AUC 0.5 while the manuscript quoted 0.640 from a runner that lived outside\n"
          "the repository, and nothing on disk recorded the discrepancy.\n")
    log(f"\n  wrote {base / 'PROVENANCE.csv'} and PROVENANCE.md")


if __name__ == "__main__":
    main()
