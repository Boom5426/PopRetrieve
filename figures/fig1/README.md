# Figure 1: Distributional differences are visible, but their value depends on the evaluator

One-line message: two drugs can share a mean signature yet differ in their subpopulation response,
so distribution-aware retrieval can see structure mean-signature retrieval cannot. Whether that
structure HELPS depends on the evaluator, which is the question the paper answers. This figure sets
the tension; it contains NO Fig-4 collapse numbers.

## Panels

| Panel | Message | Type | Status |
|-------|---------|------|--------|
| a | Biology: two drugs, similar mean signature, opposite subpopulation responses (one worsens a resistant minority) | AI schematic (fig1a_prompt.md) | prompt handed over; placeholder until fig1a.png dropped |
| b | Inverse-retrieval task: query -> candidate populations -> score (mean vs distributional) -> ranking | schematic | done |
| c | Toy 2D: candidates whose MEANS tie with the target but whose DISTRIBUTIONS differ | synthetic (seeded) | done |
| d | Evaluation coupling: coupled (energy objective -> energy regret, Class A) vs independent (-> MoA/viability, Class B/C) | schematic | done |
| e | Metric evidence ladder: Class A objective-aligned / B task-proximal / C externally-grounded, with this study's coverage (A full, B partial, C none) | schematic | done |

## Design notes
- 1a is the ONLY AI panel in the deck. Prompt in fig1a_prompt.md; palette locked to FOCAL/COMP/GREY.
- 1c is synthetic (seeded RandomState(3)); it is a labeled schematic, not a data panel, and is
  captioned as such. The shared-mean marker is drawn at the exact centroid of the target cloud.
- 1e states this study's evidence coverage honestly: Class A full, Class B partial, Class C none.
  This is the review's strongest Fig 1 addition and pre-empts the "you never validated externally"
  objection by making the evidence tier explicit up front.
- Per deck rule 5, Fig 1 sets tension only: no +0.119, no collapse statistics.

## Files
- fig1a_prompt.md : AI prompt for panel a (hand to an image model, drop result as fig1a.png).
- fig1b.py ... fig1e.py, fig1_assemble.py, fig1_problem.{png,pdf}
