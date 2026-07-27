#!/usr/bin/env python
"""Build the seven Extended Data figures and sync them into manuscript/latex/figures/.

WHY THIS EXISTS. `build_all.py` covers the six main figures and copies them into the manuscript.
Extended Data was outside it and copied by hand, and the 2026-07-27 audit found what that costs:
every shipped Extended Data PDF was a stale render, and three of them printed numbers this project
has retracted, each contradicting its own caption on the same SI page.

  * `edfig2.pdf` showed the pre-sentinel-fix MoA-nDCG power analysis (n = 191, 27,794 queries for
    80% power) while its caption already stated the corrected n = 143 and 20,844 (CORRECTIONS.md R2).
  * `edfig3.pdf` printed "predictors collapse structure 5.1x" and "9 clustering methods", both
    retracted (R1, R10), while its caption said the opposite.
  * `edfig1.pdf` titled a panel "Metric correlation (54,180 queries)", the unit overstatement R29
    corrects two sentences later in the same paper.
  * `edfig6.pdf` could not be regenerated at all: `ed6.py` imported four panel functions from
    `fig6/`, which had since been re-cut into the two-gate figure, so the script drew four panels
    unrelated to its own caption.

Rebuilding from the current sources removes all four. Run this whenever an experiment that feeds
Extended Data is re-run, and before submitting.

    python figures/build_ed.py            # build all seven, report, sync nothing
    python figures/build_ed.py --write    # build all seven and sync to manuscript/latex/figures/

WHAT THIS DOES NOT FIX. ED1 to ED4 are authored far wider than the manuscript text block, so
LaTeX scales them down and their type prints below the Nature 5 pt floor. That is a layout defect
recorded in `figures/edfigs/README.md`, it is unrelated to staleness, and this script does not
touch it: rebuilding a figure with the same authored geometry reproduces the same scale factor.
"""
from __future__ import annotations

import argparse
import importlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
MANUSCRIPT_FIGDIR = REPO / "manuscript" / "latex" / "figures"

# Extended Data number -> (script to run, the file that script writes).
# ED1 to ED4 come from one script that writes four stems in a single pass, so they share an entry.
SPECS = {
    (1, 2, 3, 4): ("edfigs/ed_panels.py", {
        1: "edfigs/ed1_reproducibility.pdf",
        2: "edfigs/ed2_classB_robustness.pdf",
        3: "edfigs/ed3_identifiability.pdf",
        4: "edfigs/ed4_resistance_exploratory.pdf",
    }),
    (5,): ("ed5/ed5.py", {5: "ed5/edfig5.pdf"}),
    (6,): ("ed6/ed6.py", {6: "ed6/edfig6.pdf"}),
    (7,): ("ed7/ed7_tahoe.py", {7: "ed7/ed7_tahoe.pdf"}),
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true",
                    help="sync the built PDFs into manuscript/latex/figures/")
    args = ap.parse_args()

    failures = 0
    produced: dict[int, Path] = {}

    for _nums, (script, outputs) in SPECS.items():
        path = HERE / script
        proc = subprocess.run([sys.executable, str(path)], cwd=str(REPO),
                              capture_output=True, text=True)
        if proc.returncode != 0:
            failures += 1
            tail = (proc.stderr or proc.stdout).strip().splitlines()
            print(f"  {script}: FAILED\n         {tail[-1] if tail else '(no output)'}")
            continue
        for n, rel in outputs.items():
            out = HERE / rel
            if not out.exists():
                failures += 1
                print(f"  ED{n}: {script} exited 0 but did not write {rel}")
                continue
            produced[n] = out
            print(f"  ED{n}: built  {rel}")

    if args.write:
        for n in sorted(produced):
            dst = MANUSCRIPT_FIGDIR / f"edfig{n}.pdf"
            shutil.copyfile(produced[n], dst)
            print(f"         -> {dst.relative_to(REPO)}")
    elif produced:
        # Report staleness so a dry run is still informative, without writing anything.
        stale = [n for n in sorted(produced)
                 if not (MANUSCRIPT_FIGDIR / f"edfig{n}.pdf").exists()
                 or (MANUSCRIPT_FIGDIR / f"edfig{n}.pdf").read_bytes() != produced[n].read_bytes()]
        print(f"\n{len(stale)} of {len(produced)} shipped Extended Data PDF(s) differ from a fresh "
              f"build: {stale or 'none'}. Re-run with --write to sync.")

    print(f"\n{'PASS' if failures == 0 else 'FAIL'}: {failures} failure(s) across 7 "
          f"Extended Data figures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
