"""SubFlowModel: subpopulation-aware conditional flow matching for drug response.

Ties together the reusable gidflow components:

    DrugEncoder      Morgan fingerprint -> drug embedding
    DrugGeneBridge   drug embedding -> protein-target logits + drug_proj + dose vec
    PopulationEncoder source population -> context vector z_source (+ per-cell emb)
    FlowField        FiLM-conditioned velocity field in gene space
    SubpopHead       soft subpopulation assignment over source-cell embeddings

The per-cell conditioning vector ``cond`` fed to the flow field concatenates the
drug projection, the dose vector, the cell-line embedding, and (optionally) the
source-population context, each broadcast across the source cells.  A single
drug/dose/cell-line condition is shared by all cells in a population.
"""
from __future__ import annotations

import torch
import torch.nn as nn

from ..losses.flow_matching import euler_integrate, flow_matching_loss
from ..losses.distribution import energy_distance
from .drug_encoder import DrugEncoder
from .drug_gene_bridge import DrugGeneBridge
from .flow_field import FlowField
from .population_encoder import PopulationEncoder
from .subpop_head import SubpopHead, coverage_aggregate


class SubFlowModel(nn.Module):
    def __init__(self, n_genes: int, n_drugs: int, n_proteins: int,
                 drug_features: torch.Tensor, n_cell_lines: int = 3,
                 pop_hidden: int = 512, pop_dim: int = 256, drug_dim: int = 256,
                 emb_dim: int = 128, K: int = 4, flow_hidden: int = 512,
                 flow_blocks: int = 3, include_source_context: bool = True,
                 dropout: float = 0.1):
        super().__init__()
        self.n_genes = n_genes
        self.n_drugs = n_drugs
        self.n_proteins = n_proteins
        self.emb_dim = emb_dim
        self.pop_dim = pop_dim
        self.K = K
        self.include_source_context = include_source_context

        df = torch.as_tensor(drug_features, dtype=torch.float32)
        self.register_buffer("drug_features", df)                       # [n_drugs, 2048]
        self.fp_dim = df.shape[1]

        self.drug_encoder = DrugEncoder(fp_dim=self.fp_dim, hidden=drug_dim * 2,
                                        out_dim=drug_dim, dropout=dropout)
        self.bridge = DrugGeneBridge(drug_dim=drug_dim, n_proteins=n_proteins,
                                     attn_dim=drug_dim, emb_dim=emb_dim, dropout=dropout)
        self.pop_encoder = PopulationEncoder(n_genes=n_genes, hidden=pop_hidden,
                                             out_dim=pop_dim, dropout=dropout)
        self.cell_line_emb = nn.Embedding(n_cell_lines, 32)
        self.subpop_head = SubpopHead(in_dim=pop_hidden, K=K)

        # cond = drug_proj(emb_dim) + dose_vec(emb_dim) + cell_line(32) + [pop_dim if ctx]
        self.cond_dim = emb_dim + emb_dim + 32 + (pop_dim if include_source_context else 0)
        self.field = FlowField(n_genes=n_genes, cond_dim=self.cond_dim,
                               hidden=flow_hidden, n_blocks=flow_blocks, dropout=dropout)

    # ------------------------------------------------------------------ drug / dose
    def drug_condition(self, drug_idx: torch.Tensor, log_dose: torch.Tensor,
                       z_source: torch.Tensor | None = None) -> dict[str, torch.Tensor]:
        """Returns {'cond':[B,cond_dim], 'target_logits':[B,P], 'drug_proj':[B,emb_dim]}.

        NOTE: this builder does NOT include the cell-line term (cell line is passed
        separately in ``_percell_cond``); it produces the drug+dose(+optional
        source-context) portion so callers that only need drug/dose reuse it.
        """
        drug_emb = self.drug_encoder(self.drug_features[drug_idx])       # [B, drug_dim]
        enc = self.bridge.encode(drug_emb)                               # target_logits, drug_proj
        dose_vec = self.bridge.dose_mlp(log_dose[:, None])               # [B, emb_dim]
        parts = [enc["drug_proj"], dose_vec]
        if self.include_source_context:
            if z_source is None:
                z_source = drug_emb.new_zeros(drug_idx.shape[0], self.pop_dim)
            parts.append(z_source)
        return {"cond_partial": torch.cat(parts, dim=-1),
                "target_logits": enc["target_logits"],
                "drug_proj": enc["drug_proj"],
                "dose_vec": dose_vec}

    # ------------------------------------------------------------------ source context
    def source_context(self, source_cells: torch.Tensor, source_mask: torch.Tensor) -> torch.Tensor:
        """[B,Ns,G],[B,Ns] -> z_source [B,pop_dim] via PopulationEncoder."""
        return self.pop_encoder(source_cells, source_mask)

    # ------------------------------------------------------------------ per-cell cond
    def _percell_cond(self, batch, z_source: torch.Tensor | None = None):
        """Build the per-cell conditioning [B,Ns,cond_dim] plus target_logits[B,P].

        Concatenates drug_proj, dose_vec, cell_line_emb(cell_line_idx), and
        z_source (if include_source_context), each broadcast across the Ns source
        cells so every cell in a population shares the same drug/dose/line/context.
        """
        B, Ns, _ = batch.source_cells.shape
        dc = self.drug_condition(batch.drug_idx, batch.log_dose, z_source=z_source)
        cl = self.cell_line_emb(batch.cell_line_idx)                     # [B, 32]
        # cond_partial already = drug_proj + dose_vec (+ z_source); splice cell line in
        # between dose and z_source is unnecessary -- concatenation order only needs to
        # be consistent, so append cell line here.
        cond_b = torch.cat([dc["cond_partial"], cl], dim=-1)            # [B, cond_dim]
        assert cond_b.shape[-1] == self.cond_dim, (cond_b.shape, self.cond_dim)
        cond = cond_b[:, None, :].expand(B, Ns, self.cond_dim)         # [B, Ns, cond_dim]
        return cond, dc["target_logits"]

    # ------------------------------------------------------------------ FM loss
    def fm_loss(self, batch) -> dict[str, torch.Tensor]:
        """DrugRankBatch -> {'fm':scalar,'target_logits':[B,P]}.

        For each item b, pair valid source cells to valid target cells and regress
        the field onto the OT displacement; average the per-pair FM loss over the
        batch.  target_logits are returned so the training loop can add
        protein_space_bce.
        """
        z_source = self.source_context(batch.source_cells, batch.source_mask) \
            if self.include_source_context else None
        cond, target_logits = self._percell_cond(batch, z_source=z_source)  # [B,Ns,cond_dim]

        B = batch.batch_size
        losses = []
        for b in range(B):
            sv = batch.source_mask[b].bool()
            tv = batch.target_mask[b].bool()
            if sv.sum() < 1 or tv.sum() < 1:
                continue
            x0 = batch.source_cells[b][sv]                              # [ns, G]
            x1 = batch.target_cells[b][tv]                             # [nt, G]
            cond_b = cond[b][sv]                                       # [ns, cond_dim]
            # OT pairing requires equal-size populations: match ns to nt.
            x0, cond_b = self._match_size(x0, x1, cond_b)
            losses.append(flow_matching_loss(self.field, x0, x1, cond_b))
        if not losses:
            fm = target_logits.sum() * 0.0
        else:
            fm = torch.stack(losses).mean()
        return {"fm": fm, "target_logits": target_logits}

    @staticmethod
    def _match_size(x0: torch.Tensor, x1: torch.Tensor, cond0: torch.Tensor):
        """Resample source rows (and their cond) so len(x0)==len(x1) for the square
        OT assignment.  Approximation: with-replacement resampling of the smaller
        set toward the target size (kept simple; batch cells are exchangeable)."""
        n0, n1 = x0.shape[0], x1.shape[0]
        if n0 == n1:
            return x0, cond0
        idx = torch.randint(0, n0, (n1,), device=x0.device)
        return x0[idx], cond0[idx]

    # ------------------------------------------------------------------ generation
    @torch.no_grad()
    def generate(self, source_cells: torch.Tensor, source_mask: torch.Tensor,
                 drug_idx: torch.Tensor, log_dose: torch.Tensor,
                 cell_line_idx: torch.Tensor, n_steps: int = 8) -> torch.Tensor:
        """-> Yhat [B,Ns,G].  Integrates each source cell forward under its drug's
        condition; source context is drawn from the source population itself."""
        B, Ns, G = source_cells.shape
        z_source = self.source_context(source_cells, source_mask) \
            if self.include_source_context else None
        dc = self.drug_condition(drug_idx, log_dose, z_source=z_source)
        cl = self.cell_line_emb(cell_line_idx)                          # [B, 32]
        cond_b = torch.cat([dc["cond_partial"], cl], dim=-1)          # [B, cond_dim]

        out = source_cells.new_zeros(B, Ns, G)
        for b in range(B):
            cond = cond_b[b][None, :].expand(Ns, self.cond_dim)       # [Ns, cond_dim]
            out[b] = euler_integrate(self.field, source_cells[b], cond, n_steps=n_steps)
        return out

    # ------------------------------------------------------------------ diagnostics
    def delta_variance(self, batch) -> torch.Tensor:
        """Variance across cells of the initial per-cell velocity field(x0, t=0, cond).

        A collapsed (pure mean-shift) field predicts the same velocity for every
        cell -> variance ~ 0.  A healthy field varies per cell -> variance > 0.
        Returns a scalar (mean per-gene variance averaged over the batch).
        """
        z_source = self.source_context(batch.source_cells, batch.source_mask) \
            if self.include_source_context else None
        cond, _ = self._percell_cond(batch, z_source=z_source)         # [B,Ns,cond_dim]
        B, Ns, _ = batch.source_cells.shape
        vars_ = []
        for b in range(B):
            sv = batch.source_mask[b].bool()
            if sv.sum() < 2:
                continue
            x0 = batch.source_cells[b][sv]                             # [ns, G]
            t0 = x0.new_zeros(x0.shape[0])                            # t=0
            v = self.field(x0, t0, cond[b][sv])                       # [ns, G]
            vars_.append(v.var(dim=0, unbiased=False).mean())         # mean per-gene variance
        if not vars_:
            return batch.source_cells.sum() * 0.0
        return torch.stack(vars_).mean()

    # ------------------------------------------------------------------ scoring
    @torch.no_grad()
    def energy_score(self, Yhat: torch.Tensor, target_cells: torch.Tensor,
                     target_mask: torch.Tensor) -> torch.Tensor:
        """-> [B] = -energy_distance(Yhat_b, target_b) over valid cells."""
        B = Yhat.shape[0]
        out = Yhat.new_zeros(B)
        for b in range(B):
            tv = target_mask[b].bool()
            out[b] = -energy_distance(Yhat[b], target_cells[b][tv])
        return out

    @torch.no_grad()
    def coverage_score(self, Yhat: torch.Tensor, source_assign: torch.Tensor,
                       target_cells: torch.Tensor, target_mask: torch.Tensor,
                       beta: float) -> torch.Tensor:
        """Per source-subpop coverage score -> [B].

        Approximation (documented): split the generated cells into K hard groups by
        argmax of ``source_assign`` [B,Ns,K], compute energy_distance(group_k,
        target_b) per subpop, then coverage_aggregate over K (lower distance =
        better coverage) and negate so higher score = better.  Empty groups get a
        large distance so they don't spuriously improve coverage.
        """
        B, Ns, _ = Yhat.shape
        K = source_assign.shape[-1]
        out = Yhat.new_zeros(B)
        for b in range(B):
            tv = target_mask[b].bool()
            tgt = target_cells[b][tv]
            hard = source_assign[b].argmax(dim=-1)                     # [Ns]
            dists = []
            for k in range(K):
                sel = hard == k
                if sel.sum() < 1:
                    dists.append(Yhat.new_tensor(1e6))                # empty subpop -> poor coverage
                else:
                    dists.append(energy_distance(Yhat[b][sel], tgt))
            dvec = torch.stack(dists)                                  # [K]
            out[b] = -coverage_aggregate(dvec, beta=beta)
        return out
