"""Optional Tahoe-100M loader — placeholder (plan Phase 5, not this round).

Tahoe-100M (100M cells, 50 cancer lines, 1100+ drugs) is the optional ICLR
strengthening anchor (cross-cancer-line heterogeneous query, or a single-sample
naturally-divergent state). It requires a GCP download and is intentionally NOT
implemented in the Phase 1-2 build.
"""
from __future__ import annotations


def load_tahoe_optional(*_args, **_kwargs):
    raise NotImplementedError(
        "Tahoe-100M is a Phase 5 optional extension; not part of the Phase 1-2 core. "
        "See distributional_inverse_drug_retrieval_project_plan_v3.md §Optional Exp 9."
    )
