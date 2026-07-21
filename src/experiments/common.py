"""Shared experiment helpers: path bootstrap, FINDINGS reference targets, verdicts.

Every experiment inserts ``src`` on ``sys.path`` (mirroring the repo convention) and
imports this module for the reproduction targets (the logged headline numbers in
``results/subflow/FINDINGS.md``) and a tolerance-checking ``verdict`` used to assert
that the self-contained re-run reproduces them.
"""
from __future__ import annotations

import sys
from pathlib import Path

# --- path bootstrap: put <package>/src on sys.path so `data`/`retrieval`/`utils`
# resolve as top-level packages (matches the original scripts' sys.path style) ---
SRC = Path(__file__).resolve().parents[1]
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TOL = 0.08   # hit@1 tolerance for the reproduction verdict (seed-identical => near-exact)

# Reproduction targets — the logged headline numbers (FINDINGS.md §3/§7/§8/§9/§11).
FINDINGS = {
    "exp01_controlled": {   # avg Hit@1 over alpha {0.5..0.9}, per cell line (FINDINGS §3)
        "K562": {"mean_cosine": 0.11, "global_energy": 0.76, "coverage_mean": 0.84, "coverage_worst": 0.63},
        "A549": {"mean_cosine": 0.36, "global_energy": 0.97, "coverage_mean": 0.87, "coverage_worst": 0.68},
        "MCF7": {"mean_cosine": 0.34, "global_energy": 0.95, "coverage_mean": 0.86, "coverage_worst": 0.65},
    },
    "exp03_crossline": {    # avg Hit@1 over alpha, per line pair (FINDINGS §9)
        "K562+A549": {"mean_cosine": 0.51, "global_energy": 0.91, "coverage_mean": 0.85, "coverage_worst": 0.68},
        "A549+MCF7": {"mean_cosine": 0.53, "global_energy": 0.96, "coverage_mean": 0.87, "coverage_worst": 0.67},
        "K562+MCF7": {"mean_cosine": 0.30, "global_energy": 0.90, "coverage_mean": 0.85, "coverage_worst": 0.65},
    },
    "exp04_cd34": {         # self-retrieval Hit@1 (FINDINGS §7): mean-cosine WINS on real primary source
        "mean_cosine": 0.53, "global_energy": 0.38, "coverage_mean": 0.37, "coverage_worst": 0.20,
    },
    # exp02/exp05/exp06 checked qualitatively (gate direction / IFNGR1 flip / 10-of-10 props).
}


def verdict(label: str, got: float, expect: float, tol: float = TOL) -> dict:
    ok = abs(got - expect) <= tol
    tag = "PASS" if ok else "WARN"
    print(f"    [{tag}] {label}: got {got:.3f} vs FINDINGS {expect:.3f} (|d|={abs(got-expect):.3f} tol {tol})")
    return {"label": label, "got": float(got), "expect": float(expect),
            "abs_diff": float(abs(got - expect)), "pass": bool(ok)}


def ordering_verdict(label: str, holds: bool, detail: str = "") -> dict:
    tag = "PASS" if holds else "FAIL"
    print(f"    [{tag}] {label}" + (f": {detail}" if detail else ""))
    return {"label": label, "pass": bool(holds), "detail": detail}
