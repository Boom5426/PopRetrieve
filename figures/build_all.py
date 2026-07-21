"""Rebuild every main figure and enforce the Nature typography floor at build time.

This exists because the failure mode it guards against is invisible until the proofs come back.
Nature Portfolio production rejects text below 5 pt at final printed size, and the natural response
to a crowded panel is to shrink the annotation rather than to cut it. Nothing complains, the PDF
still renders, and the figure ships illegible.

So this complains. Every rendered Text artist in every panel is measured, and a figure with any
text under the floor is reported rather than silently written.

    python figures/build_all.py            # report only
    python figures/build_all.py --write    # report AND export pdf/svg/png (fails on violations)
"""
import argparse
import importlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from figstyle import apply_style, panel_letter, assert_min_fontsize, MIN_PT, save

FIGS = [1, 2, 3, 4, 5, 6]
STEMS = {1: "fig1_problem", 2: "fig2_collapse", 3: "fig3_temptation",
         4: "fig4_collapse", 5: "fig5_benchmarks", 6: "fig6_two_gate"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="export, and fail on any violation")
    args = ap.parse_args()

    violations = 0
    for n in FIGS:
        sys.path.insert(0, str(HERE / f"fig{n}"))
        try:
            mod = importlib.import_module(f"fig{n}.fig{n}_assemble")
            plt.close("all")
            out = mod.build(apply_style, panel_letter)
            fig = out if hasattr(out, "savefig") else plt.figure(plt.get_fignums()[-1])

            bad = assert_min_fontsize(fig, strict=False)
            if bad:
                violations += len(bad)
                print(f"  fig{n}: {len(bad)} text element(s) below {MIN_PT} pt")
                for sz, txt in sorted(bad)[:5]:
                    print(f"         {sz:.1f} pt  {txt!r}")
            else:
                print(f"  fig{n}: CLEAN")

            if args.write and not bad:
                save(fig, HERE / f"fig{n}" / STEMS[n])
        except Exception as exc:
            violations += 1
            print(f"  fig{n}: BUILD FAILED  {type(exc).__name__}: {str(exc)[:110]}")

    print(f"\n{'PASS' if violations == 0 else 'FAIL'}: "
          f"{violations} typography violation(s) across {len(FIGS)} main figures")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
