# Reviewer-risk control (stub, transcribed from plan v3 §13)

**R1 — "Energy distance is not novel."**
We do not claim energy distance as the algorithmic novelty. Energy, MMD, sliced-
Wasserstein, and coverage are evaluated as instances of a broader distribution-aware
retrieval framework. The contribution is the *task formulation* and the
*characterization of retrieval failure under divergent subpopulation responses*.

**R2 — "Mean failure under heterogeneity is already known."**
Prior work discusses heterogeneity in forward prediction / generative design. Our focus
is how heterogeneity affects inverse drug *ranking decisions*. Not all heterogeneity
matters; ranking failure is gated by response divergence (exp02).

**R3 — "Your strongest positive is constructed."**
The paper spans realism levels: controlled SciPlex3 mixtures (exp01), cross-cell-line
semi-realistic mixtures (exp03), a CD34+ honest negative control (exp04), and Frangieh
natural immune-context evidence incl. the within-gene IFNGR1 instance (exp05). Tahoe /
natural clone-level evidence is an optional strengthening experiment (Phase 5).

**R4 — "Distribution metrics are not always better."**
Correct — CD34+ is shown as a negative control (exp04): distribution-aware retrieval is
selectively beneficial only when response divergence is sufficiently high (exp02 gate).

**R5 — "Where is the generator?"**
Retrieval objectives are orthogonal to generators. Candidate populations can be observed
or predicted by any upstream model; SubFlow is optional and not central (Phase 5).

## Acceptance criteria (plan §15) — Phase 1–2 status
- [x] task framed as distributional inverse drug retrieval
- [x] not GID-Flow/SubFlow-centric
- [x] SciPlex3 controlled reproduced (exp01)
- [x] divergence gate reproduced (exp02)
- [x] cross-line semi-real reproduced (exp03)
- [x] CD34+ honest negative reproduced (exp04)
- [x] Frangieh IFNGR1 reproduced (exp05)
- [x] ranking-flip analysis (exp07)
- [x] theory degenerate limits (exp06)
- [x] Figures 1–6 (PDF+SVG + source data + caption drafts)
- [x] README one-click reproduce
- [x] SubFlow kept out of the main line (Phase 5 optional)
- [x] no "energy distance is novel" / "all heterogeneity needs distributional retrieval" claims
