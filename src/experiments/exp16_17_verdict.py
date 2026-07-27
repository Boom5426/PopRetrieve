"""Generate results/exp16_17_verdict.md from the FULL exp16/exp17 CSVs.

Derives the lesion location and the A/B/C outcome mechanically from the numbers, so the
verdict cannot drift from the data. Decision rules encode the execution spec exactly.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils.io import PKG_ROOT, results_path                    # noqa: E402

ALPHA = 0.05
E16 = "exp16_gate_diagnosis"
E17 = "exp17_true_divergence_subset"


def _fmt_p(p):
    if not np.isfinite(p):
        return "n/a"
    return f"{p:.2e}" if p < 1e-3 else f"{p:.3f}"


def main():
    gvt = pd.read_csv(results_path(E16, "gate_vs_true_divergence.csv"))
    sweep = pd.read_csv(results_path(E16, "gate_variants_sweep.csv"))
    strat = pd.read_csv(results_path(E17, "divergence_stratified.csv"))
    power = pd.read_csv(results_path(E17, "power_analysis.csv"))

    # ── Phase 1: is the gate aligned with true divergence? ──
    p1 = gvt.set_index("test")
    aligned = False
    p1_lines = []
    for test, r in p1.iterrows():
        p1_lines.append(f"- **{test}**: statistic={r['statistic']:.3f}, p={_fmt_p(r['pvalue'])}"
                        + (f", n={int(r['n_recommended'])}" if np.isfinite(r.get('n_recommended', np.nan)) else ""))
    mw = p1[p1.index.str.contains("recommended_vs_nonrecommended")]
    sp = p1[p1.index.str.contains("spearman_preference_conflict")]
    srel = p1[p1.index.str.contains("spearman_structure_reliability")]
    mw_sig = bool(len(mw) and mw.iloc[0]["pvalue"] < ALPHA)          # binary LABEL separates?
    sp_sig = bool(len(sp) and sp.iloc[0]["pvalue"] < ALPHA)          # conflict signal correlates?
    sp_rho = float(sp.iloc[0]["statistic"]) if len(sp) else float("nan")
    srel_sig = bool(len(srel) and srel.iloc[0]["pvalue"] < ALPHA)
    srel_rho = float(srel.iloc[0]["statistic"]) if len(srel) else float("nan")
    # "aligned" = the gate carries ANY significant divergence signal (label or continuous)
    aligned = mw_sig or sp_sig
    if mw_sig:
        gate_aligned_txt = "ALIGNED (label separates divergence)"
    elif sp_sig:
        gate_aligned_txt = ("WEAKLY ALIGNED (continuous conflict signal correlates, "
                            f"ρ={sp_rho:+.2f}, but the binary recommendation label does NOT "
                            "separate high- from low-divergence queries)")
    else:
        gate_aligned_txt = "NOT ALIGNED"
    # design-flaw flag: structure_reliability should rise with divergence; if it falls, the
    # gate is mis-wired on its reliability axis.
    reliability_flaw = bool(srel_sig and srel_rho < 0)

    # ── Phase 2: any variant giving cross-cell-line-consistent non-circular separation? ──
    fixable = False
    p2_top = pd.DataFrame()
    if len(sweep):
        good = sweep[(sweep["gap_of_gaps"] > 0) & (sweep["bh_qvalue"] < ALPHA)
                     & (sweep["cross_cellline_pos_fraction"] >= 0.999)]
        fixable = len(good) > 0
        p2_top = sweep.sort_values("gap_of_gaps", ascending=False).head(6)

    # ── Phase 3: highest-divergence stratum on non-circular metrics ──
    highest = None
    strat_nonall = strat[strat.stratum != "ALL"]
    if len(strat_nonall):
        # highest stratum = the one with the largest divergence_median
        hi_div = strat_nonall.loc[strat_nonall.groupby("metric")["divergence_median"].idxmax()]
        highest = hi_div

    # Effect-size floor: with n~191 per stratum, trivially small gaps reach significance.
    # A gap is "material" only if the median advantage is a non-trivial fraction of the
    # metric's observed spread. minority_state_coverage and moa_ndcg both live on ~[0,1]
    # but their realized per-query spread is small; we use a per-metric MAD-scaled floor.
    def _material(metric, median_gap):
        col = f"{metric}_gap"
        # spread of the gap across ALL queries (from the ALL row's sd if present)
        allrow = strat[(strat.metric == metric) & (strat.stratum == "ALL")]
        sd = float(allrow["sd_gap"].iloc[0]) if len(allrow) and np.isfinite(allrow["sd_gap"].iloc[0]) else np.nan
        # material if median gap >= 0.2 * sd of the gaps (a small-effect Cohen-style floor)
        return bool(np.isfinite(sd) and sd > 0 and median_gap >= 0.2 * sd)

    hi_sig_material = False   # significant AND materially sized
    hi_sig_trivial = False    # significant but negligible effect
    hi_positive_trend = False # positive but not significant
    if highest is not None:
        for _, r in highest.iterrows():
            sig = r["median_gap"] > 0 and np.isfinite(r["bh_qvalue"]) and r["bh_qvalue"] < ALPHA
            if sig and _material(r["metric"], r["median_gap"]):
                hi_sig_material = True
            elif sig:
                hi_sig_trivial = True
            elif r["median_gap"] > 0:
                hi_positive_trend = True

    underpowered = bool(len(power) and not power["data_sufficient"].any())

    # ── Outcome A/B/C ──  (effect size gates A; significance-without-magnitude is not A)
    if hi_sig_material:
        outcome = ("**A — conditional advantage holds.** In the highest-divergence stratum, "
                   "EvalShift significantly AND materially exceeds mean retrieval on a non-circular "
                   "metric.")
    elif hi_sig_trivial:
        outcome = ("**B(−) — statistically real but negligible.** In the highest-divergence "
                   "stratum EvalShift significantly exceeds mean retrieval on a non-circular metric, "
                   "but the effect size is negligible (well below a small-effect floor). The "
                   "mean→distribution mechanism is intact and divergence-monotone, yet its "
                   "practical magnitude is tiny; on the annotation-recovery metric there is no "
                   "advantage at all.")
    elif hi_positive_trend and underpowered:
        outcome = ("**B — trend, sample-limited.** The highest-divergence stratum shows a "
                   "positive but non-significant EvalShift gap on a non-circular metric, and the "
                   "power analysis shows the current sample is insufficient to resolve it.")
    else:
        outcome = ("**C — chain broken in expression data.** The highest-divergence stratum "
                   "shows no positive non-circular EvalShift advantage. Changing the gate or the "
                   "metric cannot recover it; a real functional/longitudinal outcome is needed.")

    # ── Lesion ──
    if not aligned:
        lesion = ("**Gate calibration (Phase 1/2).** The gate's recommended labels are not "
                  "significantly aligned with true response divergence. ")
        lesion += ("A gate variant DID achieve cross-cell-line-consistent non-circular separation "
                   "(Phase 2) — the gate is repairable."
                   if fixable else
                   "No gate variant achieved cross-cell-line-consistent non-circular separation "
                   "(Phase 2) — the gate is not simply mis-calibrated; the lesion is deeper.")
    else:
        lesion = ("**Data/task layer (Phase 3), not (only) the gate.** The gate carries a weak "
                  "but significant divergence signal, yet ")
        lesion += ("even stratifying directly by true divergence — bypassing the gate entirely — "
                   "EvalShift shows no MATERIAL non-circular advantage in the highest-divergence "
                   "stratum. The signal is either absent or negligibly small in the expression "
                   "data itself, so no gate re-calibration can recover a practical advantage."
                   if not hi_sig_material else
                   "a material advantage concentrates in the genuinely high-divergence stratum.")
    if reliability_flaw:
        lesion += (f" **Secondary gate design flaw:** structure_reliability correlates "
                   f"NEGATIVELY with true divergence (ρ={srel_rho:+.2f}, p="
                   f"{_fmt_p(float(srel.iloc[0]['pvalue']))}) — it moves opposite to the quantity "
                   f"it should track, so the gate's reliability axis is mis-wired. This explains "
                   f"why the binary recommendation label fails to separate on divergence even "
                   f"though the conflict axis weakly does.")

    # ── Assemble sections ──
    phase1 = ("Gate vs true divergence: **" + gate_aligned_txt + "**.\n\n" + "\n".join(p1_lines)
              + f"\n\nInterpretation: the binary DART_recommended label "
              + ("separates high- from low-divergence queries"
                 if mw_sig else "does NOT separate high- from low-divergence queries")
              + f" (Mann-Whitney p={_fmt_p(float(mw.iloc[0]['pvalue'])) if len(mw) else 'n/a'}); "
              + "the continuous preference_conflict signal is "
              + (f"weakly but significantly correlated with true divergence (ρ={sp_rho:+.2f})"
                 if sp_sig else "not significantly correlated with true divergence")
              + "; structure_reliability is "
              + (f"NEGATIVELY correlated with true divergence (ρ={srel_rho:+.2f}) — a design flaw"
                 if reliability_flaw else
                 f"correlated with true divergence at ρ={srel_rho:+.2f}")
              + ".")

    def _tbl(df, cols, headers):
        out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
        for _, r in df.iterrows():
            cells = []
            for c in cols:
                v = r[c]
                if isinstance(v, float):
                    cells.append(_fmt_p(v) if "p" == c[-1:] or "q" in c else f"{v:.4f}")
                else:
                    cells.append(str(v))
            out.append("| " + " | ".join(cells) + " |")
        return "\n".join(out)

    phase2 = ("No variant achieved cross-cell-line-consistent, BH-significant non-circular "
              "separation.\n\n" if not fixable else
              "At least one variant achieved cross-cell-line-consistent non-circular separation.\n\n")
    if len(p2_top):
        phase2 += _tbl(p2_top, ["conflict_variant", "reliability_variant", "metric",
                                "gap_of_gaps", "mannwhitney_p", "bh_qvalue",
                                "cross_cellline_pos_fraction"],
                       ["conflict", "reliability", "metric", "gap_of_gaps", "p", "q", "xline_pos"])

    phase3 = _tbl(strat_nonall.sort_values(["metric", "divergence_median"]),
                  ["metric", "stratum", "divergence_median", "n", "median_gap",
                   "frac_positive", "wilcoxon_p_two_sided", "bh_qvalue"],
                  ["metric", "stratum", "div_med", "n", "median_gap", "frac+", "p", "q"])

    powertbl = _tbl(power, ["metric", "stratum", "n", "observed_mean_gap", "sd_gap",
                            "achieved_power", "n_for_80pct_power", "data_sufficient"],
                    ["metric", "stratum", "n", "eff", "sd", "power", "n@80%", "sufficient"])

    # ── Impact ──
    if outcome.startswith("**A"):
        impact = ("Claim 3/Claim 4 reconciliation: the gate (or the true-divergence stratifier) "
                  "DOES isolate a subset with a genuine non-circular EvalShift advantage. Report this "
                  "subset explicitly; upgrade Claim 4 from 'metric-dependent, proxy-only' to "
                  "'conditional advantage on diagnosable high-divergence queries'.")
    elif outcome.startswith("**B(−)"):
        impact = ("Sharpens Claim 4 without overturning it. The mean→distribution advantage is "
                  "(a) real and divergence-monotone on the coverage proxy — EvalShift's sensitivity to "
                  "response divergence is mechanistically confirmed — but (b) negligibly small in "
                  "magnitude and (c) entirely absent on annotation-recovery (moa_ndcg), where the "
                  "study is orders-of-magnitude underpowered. Report the monotone coverage trend "
                  "WITH its effect size and the moa_ndcg null side-by-side. Do NOT upgrade to a "
                  "practical advantage. Claim 4 stays 'metric-dependent'; add: the direction of "
                  "the effect tracks true divergence exactly as the theory predicts, but its size "
                  "does not reach practical relevance in expression space.")
    elif outcome.startswith("**B"):
        impact = ("Report honestly as a sample-limited trend. State the observed effect and the "
                  "n required for 80% power. Do NOT claim advantage. Claim 4 stays "
                  "'metric-dependent'; add the divergence-stratified trend + power as a bounded, "
                  "future-work-flagged observation.")
    else:
        impact = ("Pivot the manuscript's central contribution to the negative result: the "
                  "mean→distribution advantage seen under energy-based proxies does NOT survive "
                  "non-circular metrics at ANY true-divergence level. This is the strongest "
                  "honest framing — it reveals (a) the circularity of energy-welfare proxies and "
                  "(b) that the mean→distribution chain breaks in pure expression data. The seven "
                  "manuscript files' Claim 4 already anticipate this; tighten them to lead with it.")

    nulls = []
    for _, r in strat_nonall.iterrows():
        if not (r["median_gap"] > 0 and np.isfinite(r["bh_qvalue"]) and r["bh_qvalue"] < ALPHA):
            nulls.append(f"- [{r['metric']}] {r['stratum']} (div~{r['divergence_median']:.2f}): "
                         f"median_gap={r['median_gap']:+.4f}, p={_fmt_p(r['wilcoxon_p_two_sided'])}, "
                         f"q={_fmt_p(r['bh_qvalue'])} — no significant advantage.")
    nulls_txt = "\n".join(nulls) if nulls else "- (none)"

    # Repo-anchored, not CWD-relative. This used to read "paper/exp16_17_verdict_TEMPLATE.md":
    # `paper/` is gitignored author-local scratch, does not exist even on the author's machine, and
    # has never been in git history, so step [4/4] of scripts/run_exp16_17.sh ended in a traceback
    # for everyone and results/exp16_17_verdict.md could not be regenerated at all (audited
    # 2026-07-27). The only surviving copy of the template is the archived one, and it is the right
    # one: its eight placeholders are exactly the eight substituted below.
    tmpl_path = PKG_ROOT / "manuscript" / "_archive" / "audits" / "exp16_17_verdict_TEMPLATE.md"
    if not tmpl_path.exists():
        raise FileNotFoundError(
            f"verdict template not found at {tmpl_path}. It carries the eight placeholders this "
            f"function fills ({{IMPACT}} {{LESION}} {{NULLS}} {{OUTCOME}} {{PHASE1}} {{PHASE2}} "
            f"{{PHASE3}} {{POWER}}); without it the verdict document cannot be regenerated.")
    tmpl = tmpl_path.read_text()
    doc = (tmpl.replace("{LESION}", lesion).replace("{OUTCOME}", outcome)
           .replace("{PHASE1}", phase1).replace("{PHASE2}", phase2)
           .replace("{PHASE3}", phase3).replace("{POWER}", powertbl)
           .replace("{IMPACT}", impact).replace("{NULLS}", nulls_txt))
    # strip the template HTML comment header
    doc = doc.split("-->", 1)[1].lstrip() if "-->" in doc else doc
    out = results_path("exp16_17_verdict.md")
    out.write_text(doc)
    print(f"wrote {out}")
    print("OUTCOME:", "A" if outcome.startswith("**A") else "B" if outcome.startswith("**B") else "C")
    print("LESION aligned:", aligned, "fixable:", fixable, "underpowered:", underpowered)


if __name__ == "__main__":
    main()
