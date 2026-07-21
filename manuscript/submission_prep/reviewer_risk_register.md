# Reviewer Risk Register — Metric-Circularity Positioning

Anticipated reviewer objections, the risk, and the pre-emptive response embedded in
the manuscript. Ordered by severity.

| # | Anticipated objection | Risk | Where addressed | Response summary |
|---|---|---|---|---|
| 1 | "This is just YOUR evaluation being circular, not a field problem." | high | `evaluation_circularity_audit.md`; Intro; Discussion §field-level | Field-level audit over 7 method families shows objective-aligned evaluation is the field default across signature/predictive/graph modalities. |
| 2 | "If DART doesn't improve independent utility, what is it for?" | high | Abstract; Result 3; Discussion §why-negatives-central | DART is a probe; the contribution is the A-vs-B gap and the unification, not therapeutic superiority. Positive anchors preserved. |
| 3 | "Isn't the +0.119 gain enough to claim usefulness?" | high | Result 2 label; Result 3; negative-claims box | +0.119 is explicitly a Class A objective-aligned proxy; reported only paired with the Class B null (−0.013 / 0-of-37). |
| 4 | "Observed candidate response is an oracle setting." | med | Result 2; Result 4 | Stated explicitly: observed = upper bound; exp09/12/13 test realistic predicted/partial-observed conditions. |
| 5 | "Why does DART fail on predicted responses?" | med | Result 4 | Mechanism: predictors collapse structure (~5x lower subpop-variance ratio); no structure to exploit — the thesis, not a defect. |
| 6 | "Why trust a gate at AUC 0.640?" | med | Result 5; gate language fix | Called moderate, not accurate; gate is experimental; reliability axis anti-correlated with true divergence (ρ=−0.21) — reported as a limitation. |
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
