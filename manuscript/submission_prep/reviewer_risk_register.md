> **SUPERSEDED IN PART, audited 2026-07-27.** This is a working document. It predates the July
> 2026 audit, which retracted or revised numbers this file may still quote, among them the
> "5.1x structure collapse" (R1), the MoA-nDCG statistics computed over 165 undefined sentinel
> values (R2), the Class A/B contrast that compared two different scorers (R4), the HIR-Bench
> predictability AUC of 0.640 (R11), the claim that no Class C metric was available (R14), and
> the "0 of 37 real-data tasks" count (R13). **Read [CORRECTIONS.md](../../CORRECTIONS.md) before quoting any
> number below**, and treat `manuscript/latex/PopRetrieve_manuscript.tex` as the authority for
> anything that reaches the paper. Where this file and CORRECTIONS.md disagree, CORRECTIONS.md
> is right.

# Reviewer Risk Register — Metric-Circularity Positioning

Anticipated reviewer objections, the risk, and the pre-emptive response embedded in
the manuscript. Ordered by severity.

| # | Anticipated objection | Risk | Where addressed | Response summary |
|---|---|---|---|---|
| 1 | "This is just YOUR evaluation being circular, not a field problem." | high | `evaluation_circularity_audit.md`; Intro; Discussion §field-level | Field-level audit over 7 method families shows objective-aligned evaluation is the field default across signature/predictive/graph modalities. |
| 2 | "If PopRetrieve doesn't improve independent utility, what is it for?" | high | Abstract; Result 3; Discussion §why-negatives-central | PopRetrieve is a probe; the contribution is the A-vs-B gap and the unification, not therapeutic superiority. Positive anchors preserved. |
| 3 | "Isn't the +0.119 gain enough to claim usefulness?" | high | Result 2 label; Result 3; negative-claims box | +0.119 is explicitly a Class A objective-aligned proxy. **The paired contrast quoted here is RETRACTED:** +0.119 and −0.013 come from different scorers on different query sets (R4), and "0 of 37" was the QUICK sanity task count quoted as a real-data result (R13). Use the Results section's current Class A / Class B statement. |
| 4 | "Observed candidate response is an oracle setting." | med | Result 2; Result 4 | Stated explicitly: observed = upper bound; exp09/12/13 test realistic predicted/partial-observed conditions. |
| 5 | "Why does PopRetrieve fail on predicted responses?" | med | Result 4 | **RETRACTED (R1):** the "~5x structure collapse" is false on both sides of the comparison. The current mechanism statement is that predictors *retain* baseline subpopulation structure but do not reproduce response *divergence* (Fig. 6c). Use that. |
| 6 | "Why trust a gate at AUC 0.640?" | med | Result 5; gate language fix | **RETRACTED (R11):** AUC 0.640 was one function of the oracle predicting another, with leaked cross-validation and n inflated 480-fold. Under honest grouping the observable-feature AUC is 0.788 at n_eff = 28 and the oracle-derived arm is 0.400, no better than chance. The reliability axis anti-correlation (ρ=−0.21) stands and is reported as a limitation. |
| 7 | "Is HIR-Bench circular / self-fulfilling?" | med | Result 5 | Stated: constructive synthetic; boundary expected by design; real question is whether real data project onto the same regimes. |
| 8 | "Does this predict resistance?" | med | Result 6; negative-claims box | No — exp15 exploratory, no timecourse/survival; minority-rescue near-null; hypothesis-generating only. |
| 9 | "Is the CMap identity overstated?" | low | Result 1; negative-claims box #7 | Identity limited to cosine kernel; WTCS is a monotone rank-based sibling, not algebraically identical. |
| 10 | "Did you benchmark scGen/PDGrapher fairly?" | low | Methods; negative-claims box #6 | Not benchmarked as live models; treated as candidate-response sources; scGen = CPA-linear fallback, provenance-stamped. |

## Residual risks (honest)
- The paper reports a largely negative independent-utility result; some reviewers may
  still prefer a positive-method paper. Mitigation: the unification (Result 1) and the
  field-level audit give two durable positive contributions independent of utility.
- Real-data breadth is limited (4 datasets, 0/37 tasks). Mitigation: framed as the
  finding (metric-dependence), not as insufficient evidence for a positive claim.
