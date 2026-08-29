#!/usr/bin/env python
r"""Build the three Extended Data figures and sync them into manuscript/latex/figures/.

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
    `fig5/`, which had since been re-cut into the two-gate figure, so the script drew four panels
    unrelated to its own caption.

Rebuilding from the current sources removes all four. Run this whenever an experiment that feeds
Extended Data is re-run, and before submitting.

    python figures/build_ed.py            # build all three, report, sync nothing
    python figures/build_ed.py --write    # build all three and sync to manuscript/latex/figures/

THE PRINT-WIDTH GATE. Every Extended Data figure enters the SI with
`\includegraphics[width=\textwidth]`, so a canvas wider than the 6.93 in text block is scaled DOWN
and every nominal point size shrinks with it. ED1 to ED4 were authored at 10.2-12.6 in and printed
at 0.55-0.68x, which put 5 pt source text at 2.75-3.39 pt, and nothing reported it: the deck's
typography gate measures NOMINAL sizes, which are unaffected by the scale factor. Each figure is
now authored at 6.9 in and this script measures the PDF media box and fails the build if any
canvas exceeds the text block. That is the condition under which nominal size equals printed size,
so it is the invariant worth gating on.
"""
from __future__ import annotations

import argparse
import importlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
MANUSCRIPT_FIGDIR = REPO / "manuscript" / "latex" / "figures"

# Extended Data number -> (script to run, the file that script writes).
#
# SEVEN FIGURES BECAME THREE ON 2026-08-29. The old deck spread 26 panels over seven figures at
# about 5.9 in2 per panel, against the main deck's 3.7. Read back against the manuscript, the SI
# tables and the Supplementary Notes, five of those panels were carried in full somewhere else
# and are deleted rather than merged (old ED1a, ED1b, ED2c, ED3c and ED6a; edfigs/
# ed_consolidated.py names what carries each one). The surviving twenty-one are drawn by that one
# script, in three figures, at panel sizes the seven-figure split could not give them.
#
# ED4 WAS SHIPPING THE WRONG FIGURE UNTIL 2026-08-29. The dict here mapped 4 to
# edfigs/ed4_resistance_exploratory.pdf, which draws programme enrichment, an AXL/divergence
# scatter and a minority-rescue scatter, while the Extended Data Fig. 4 caption described
# compartment-assignment validation and threshold robustness in ZhaoSims2021. The figure that
# matches the caption is ed4/ed4_zhao_robustness.py; its four panels are now ED3a-d. The
# resistance-exploratory figure is referenced by nothing: no sentence in the manuscript or the SI
# mentions AXL, mesenchymal programmes, quiescence or minority rescue.
SPECS = {
    (1, 2, 3): ("edfigs/ed_consolidated.py", {
        1: "edfigs/ed1_scores_and_limits.pdf",
        2: "edfigs/ed2_identifiability_and_benchmark.pdf",
        3: "edfigs/ed3_tissue_and_scale.pdf",
    }),
}


# The SI text block, in inches: letterpaper with 2 cm margins gives 500.484 pt = 6.951 in of
# \textwidth. A canvas at or under this prints at scale 1.0, so nominal point size is printed
# point size; anything wider is silently shrunk by \includegraphics.
TEXT_BLOCK_IN = 6.951
_MEDIABOX = re.compile(rb"/MediaBox\s*\[\s*([\d.+-]+)\s+([\d.+-]+)\s+([\d.+-]+)\s+([\d.+-]+)")
# Matplotlib stamps a wall-clock /CreationDate into every PDF it writes, so a byte comparison
# between a shipped figure and a fresh render of the same code ALWAYS differs. The staleness
# report below was therefore stuck at "7 of 7 differ" whatever the state of the deck, including
# immediately after --write, which made it useless as a signal. Stripping the timestamp makes the
# comparison test the drawing rather than the clock.
_CREATIONDATE = re.compile(rb"/CreationDate\s*\([^)]*\)")


def _content(pdf: Path) -> bytes:
    return _CREATIONDATE.sub(b"", pdf.read_bytes())


def _canvas_inches(pdf: Path) -> tuple[float, float] | None:
    """(width, height) of the first MediaBox, in inches, or None if it cannot be read."""
    m = _MEDIABOX.search(pdf.read_bytes())
    if not m:
        return None
    x0, y0, x1, y1 = (float(g) for g in m.groups())
    return (abs(x1 - x0) / 72.0, abs(y1 - y0) / 72.0)


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
            box = _canvas_inches(out)
            if box is None:
                print(f"  ED{n}: built  {rel}  (media box unreadable; print width NOT checked)")
                continue
            w, h = box
            scale = TEXT_BLOCK_IN / w
            if w > TEXT_BLOCK_IN + 0.02:
                failures += 1
                print(f"  ED{n}: built  {rel}\n"
                      f"         PRINT WIDTH: canvas {w:.2f} in exceeds the {TEXT_BLOCK_IN:.2f} in "
                      f"text block, so it prints at {scale:.2f}x and every nominal point size\n"
                      f"         shrinks with it. Author the figure at {TEXT_BLOCK_IN:.2f} in or "
                      f"less; do not shrink the type to compensate.")
            else:
                print(f"  ED{n}: built  {rel}  ({w:.2f} x {h:.2f} in, prints at {scale:.2f}x)")

    if args.write:
        for n in sorted(produced):
            dst = MANUSCRIPT_FIGDIR / f"edfig{n}.pdf"
            shutil.copyfile(produced[n], dst)
            print(f"         -> {dst.relative_to(REPO)}")
    elif produced:
        # Report staleness so a dry run is still informative, without writing anything.
        stale = [n for n in sorted(produced)
                 if not (MANUSCRIPT_FIGDIR / f"edfig{n}.pdf").exists()
                 or _content(MANUSCRIPT_FIGDIR / f"edfig{n}.pdf") != _content(produced[n])]
        print(f"\n{len(stale)} of {len(produced)} shipped Extended Data PDF(s) differ from a fresh "
              f"build: {stale or 'none'}. Re-run with --write to sync.")

    n_fig = sum(len(outputs) for _n, (_s, outputs) in SPECS.items())
    print(f"\n{'PASS' if failures == 0 else 'FAIL'}: {failures} failure(s) across {n_fig} "
          f"Extended Data figures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
