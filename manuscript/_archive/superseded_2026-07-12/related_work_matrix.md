# Related-work positioning (stub, transcribed from plan v3 §12)

| Direction | Representative works | What they solve | Relation to this project |
|---|---|---|---|
| Forward perturbation prediction | scGen, CPA, chemCPA, scDFM | Predict perturbed cell states | Upstream; not retrieval |
| Distributional prediction | scDFM and related | Model the full response distribution | Similar motivation, different task |
| Inverse design / generation | PDGrapher, CURE | Infer targets / generate molecules | Inverse, but not candidate distributional retrieval |
| Signature-based retrieval | CMap / LINCS-style | Rank drugs by signatures | Retrieval, but usually mean/signature-based |
| **This project** | Distributional inverse retrieval | Rank candidate drugs using population distributions | Focus on the decision objective |

Positioning: forward prediction and generative inverse design are upstream; the
contribution here is the **retrieval/ranking decision layer** and its
**divergence-gated boundary**, orthogonal to any response predictor.
