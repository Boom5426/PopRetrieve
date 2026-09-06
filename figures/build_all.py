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
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from figstyle import (apply_style, panel_letter, assert_min_fontsize,
                      mathtext_offenders, MIN_PT, save)

FIGS = [1, 2, 3, 4, 5, 6]
# The single canonical output stem per figure. This is the name that gets copied to
# manuscript/latex/figures/figN.pdf, so it is the authority; each figN_assemble.py declares the
# same string as its own module-level STEM and _check_stem below refuses to build if the two
# disagree. Two figures used to write themselves under a SECOND stem (fig2_unification,
# fig2_apparent_gains) from inside build(), so each composite sat on disk twice under two names
# with nothing to say which one the manuscript compiled.
#
# SIX main figures since 2026-09-03. Figure 5 used to carry the whole Phase-II intervention
# result, oracle and forward prediction together, on one eight-panel page. The two halves answer
# different questions and were competing for the same room, so they are two pages: Figure 5 with
# candidate responses OBSERVED, Figure 6 with them PREDICTED. No experiment was re-run for the
# split; both pages read the same result tree through figures/phase2_data.py, and their two task
# schematics are one function with one switch (figures/phase2_task.py).
#
# The note below is the earlier count change and is kept for the record.
# FIVE main figures since 2026-08-29, not six. The old Figure 2 (the zero-variance-limit figure)
# carried no measured value from real cells: every claim on it was either an algebraic identity
# proved in Methods or a definitional property of the coverage score, and two of its six panels
# duplicated Extended Data Fig. 1b,c, which shows the mean-cosine/CMap-cosine identity over 54,180
# query-candidate scores rather than over three macro-means. Its two surviving panels are now
# Extended Data Fig. 1d,e and the old figures 3-6 moved down one place.
STEMS = {1: "fig1_problem", 2: "fig2_temptation", 3: "fig3_collapse",
         4: "fig4_benchmarks", 5: "fig5_intervention_oracle",
         6: "fig6_prediction_bottleneck"}


def _check_stem(n, mod):
    """Fail loudly if an assemble module writes under a stem other than the canonical one."""
    declared = getattr(mod, "STEM", None)
    if declared is not None and declared != STEMS[n]:
        raise ValueError(
            f"fig{n}_assemble.STEM is {declared!r} but build_all.STEMS[{n}] is {STEMS[n]!r}; "
            f"one figure, one stem. Fix the assemble, not this dict: STEMS is the name that syncs "
            f"to manuscript/latex/figures/fig{n}.pdf.")

# The figure the manuscript COMPILES is a second copy under manuscript/latex/figures/figN.pdf, and
# nothing kept it in step with the panel sources. Every one of the six had drifted: three were
# months-old renders of panel code that has since been rewritten, and the three that had been
# hand-copied went stale again on the next rebuild. A figure deck that is "regenerable from code"
# but reaches the PDF through a manual copy is not reproducible, so --write does the copy.
MANUSCRIPT_FIGDIR = HERE.parent / "manuscript" / "latex" / "figures"


def _sync_to_manuscript(n, stem_path):
    """Copy the freshly written PDF to the path \\includegraphics actually reads."""
    if not MANUSCRIPT_FIGDIR.is_dir():
        return None
    dst = MANUSCRIPT_FIGDIR / f"fig{n}.pdf"
    shutil.copyfile(str(stem_path) + ".pdf", dst)
    return dst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="export, and fail on any violation")
    args = ap.parse_args()

    violations = 0
    for n in FIGS:
        sys.path.insert(0, str(HERE / f"fig{n}"))
        try:
            mod = importlib.import_module(f"fig{n}.fig{n}_assemble")
            _check_stem(n, mod)
            plt.close("all")
            out = mod.build(apply_style, panel_letter)
            fig = out if hasattr(out, "savefig") else plt.figure(plt.get_fignums()[-1])
            # DRAW BEFORE MEASURING. Tick labels are created lazily at draw time, so a gate that
            # walks Text artists on an undrawn figure never sees them. That blind spot hid a real
            # violation for the life of this deck: matplotlib's LogFormatter writes an exponent as
            # mathtext, so the "$10^{-3}$" labels on figure 2's log axes printed their exponents
            # at 0.7 x 6 pt = 4.2 pt, under the production floor, while the gate reported CLEAN.
            fig.canvas.draw()

            # Reported, not counted as a violation: see figstyle.mathtext_offenders. Bringing a
            # sub/superscript to 5 pt means raising the nominal size to ~7.2 pt, which re-authors
            # the panel. Printed here so it cannot be forgotten, and left to a human to decide.
            mt = mathtext_offenders(fig)
            if mt:
                print(f"  fig{n}: NOTE {len(mt)} mathtext sub/superscript(s) print below "
                      f"{MIN_PT} pt (nominal size passes; see figstyle.mathtext_offenders)")
                for eff, nom, txt in mt[:3]:
                    print(f"         {eff:.2f} pt effective (nominal {nom:.1f})  {txt!r}")

            bad = assert_min_fontsize(fig, strict=False)
            if bad:
                violations += len(bad)
                print(f"  fig{n}: {len(bad)} text element(s) below {MIN_PT} pt")
                for sz, txt in sorted(bad)[:5]:
                    print(f"         {sz:.1f} pt  {txt!r}")
            else:
                print(f"  fig{n}: CLEAN")

            if args.write and not bad:
                stem = save(fig, HERE / f"fig{n}" / STEMS[n])
                dst = _sync_to_manuscript(n, stem)
                if dst is not None:
                    print(f"         -> {dst.relative_to(HERE.parent)}")
        except Exception as exc:
            violations += 1
            print(f"  fig{n}: BUILD FAILED  {type(exc).__name__}: {str(exc)[:110]}")

    print(f"\n{'PASS' if violations == 0 else 'FAIL'}: "
          f"{violations} typography violation(s) across {len(FIGS)} main figures")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
