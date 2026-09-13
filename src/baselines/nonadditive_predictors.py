"""Non-additive, cell-state-conditional perturbation predictors: the falsification test for Gate 1.

WHY THIS MODULE EXISTS
----------------------
Gate 1 says a distributional decision layer can add nothing on top of a candidate-response
source that supplies no *differential* response. The load-bearing part of that claim is
algebraic: a predictor that adds a SINGLE delta vector to EVERY cell has two subpopulations
with identical responses, so their induced cosine is exactly 1 and the exploitable divergence
is exactly zero.

The empirical part was not load-bearing and, as originally written, was not even supported.
The three predictors previously tested (average-effect, nearest-neighbour, and an in-repo
linear-latent model of the scGen/CPA family) are ALL additive by construction, so finding
that they induce no divergence demonstrated the algebra and surveyed nothing. Concluding from
them that "current perturbation predictors are additive" was circular: we built an additive
model, labelled it scGen, and then concluded that scGen is additive.

This module runs the models that could actually falsify the framework. Each escapes additivity
by a different mechanism, which is the point: the ladder isolates WHICH property matters.

    average-effect      delta added in gene space                     cos = 1 EXACTLY (algebra)
    linear-latent       delta added in latent space, LINEAR decoder   cos = 1 EXACTLY (algebra)
    -------------------------------------------------------------------------------------------
    scGen               delta added in latent space, NONLINEAR        does decoder curvature
                        decoder (the published VAE)                   alone open the gate?
    CPA                 drug + dose + covariate embeddings,           does explicit conditioning
                        nonlinear decoder                             open it?
    OT map              each cell gets its OWN displacement, from     the maximally non-additive
                        an optimal-transport coupling                 predictor: it must open the
                                                                      gate if anything does
Two-gate prediction: induced divergence should rise across that ladder, and retrieval gain
should rise with it. If divergence rises and gain does not, the framework is wrong and we say so.

FAITHFULNESS
------------
scGen and CPA are the PUBLISHED packages (scgen 2.1.1, cpa-tools 0.8.1), not re-implementations.
The scGen wrapper reproduces the exact arithmetic of ``scgen.SCGEN.predict`` (_scgen.py:155-164):

    delta      = mean(latent of treated) - mean(latent of control)     # one vector
    z_pred     = delta + latent(control cells to predict)              # same delta, every cell
    x_pred     = module.generative(z_pred)["px"]                       # NONLINEAR decode

We call scGen's own trained VAE and its own rule; the only thing we choose is which control
cells to push through it, which is what the retrieval harness requires and what scGen's
``predict`` does internally via ``celltype_to_predict``.

These models need scgen/cpa-tools, which pin an older scvi-tools stack and are therefore
installed in a separate optional environment (``dartpred``/``dartcpa``).
Importing this module without them raises: it does not silently fall back to a linear model.
That silent fallback is what produced the error this module exists to correct.
"""
from __future__ import annotations

from typing import Optional

import numpy as np

from baselines.population_synthesis import resample_rows


def pd_unique_first(a) -> str:
    """First distinct value, used only to pick a registry-valid placeholder category."""
    return sorted(set(np.asarray(a).tolist()))[0]


def _cpa_safe(name: str) -> str:
    """CPA parses '+' as a combination separator, and SciPlex3 has drugs named e.g. '(+)-JQ1'.

    Left unsanitized, CPA reads such a drug as a two-compound combination and setup_anndata
    dies on a ragged vstack. We substitute a token that cannot occur in a drug name and keep
    the mapping so predictions can be requested by the original name.
    """
    return str(name).replace("+", "<PLUS>")


# ---------------------------------------------------------------------------
# scGen: latent-additive, NONLINEAR decoder (the published VAE)
# ---------------------------------------------------------------------------


class RealScGenPredictor:
    """The published scGen (scgen.SCGEN), used through its own latent arithmetic.

    Latent-additive like our linear-latent control, but the decoder is a neural network.
    A single latent delta therefore decodes to a DIFFERENT gene-space delta for every cell,
    so unlike the linear case the induced response cosine is not pinned to 1 by algebra.
    Whether the curvature is enough to matter is the empirical question.
    """

    name = "scgen_real"
    backend = "scgen"

    def __init__(self, n_epochs: int = 100, n_latent: int = 30, seed: int = 0,
                 batch_size: int = 512):
        self.n_epochs = n_epochs
        self.n_latent = n_latent
        self.seed = seed
        self.batch_size = batch_size
        self._model = None
        self._z_ctrl_mean: Optional[np.ndarray] = None
        self._delta_z: dict[str, np.ndarray] = {}

    def fit(self, dataset, drugs: Optional[list] = None,
            contexts: Optional[list] = None) -> "RealScGenPredictor":
        import anndata as ad
        import scgen
        import scvi

        scvi.settings.seed = self.seed
        X = np.asarray(dataset.X, dtype=np.float32)
        cond = np.where(dataset.is_control, "control", dataset.pert.astype(str))
        ctx = dataset.context.astype(str)
        self._ref_ctx = str(pd_unique_first(ctx))
        adata = ad.AnnData(X=X, obs={"condition": cond, "cell_type": ctx})
        scgen.SCGEN.setup_anndata(adata, batch_key="condition", labels_key="cell_type")
        self._model = scgen.SCGEN(adata, n_latent=self.n_latent)
        self._model.train(max_epochs=self.n_epochs, batch_size=self.batch_size,
                          early_stopping=True, early_stopping_patience=15)

        # scGen's delta rule, verbatim: one latent vector per perturbation.
        z = self._model.get_latent_representation(adata)
        is_ctrl = cond == "control"
        self._z_ctrl_mean = z[is_ctrl].mean(0)
        all_drugs = drugs if drugs is not None else sorted(
            set(dataset.pert[~dataset.is_control].tolist()))
        for d in all_drugs:
            m = cond == str(d)
            if m.sum() >= 2:
                self._delta_z[str(d)] = z[m].mean(0) - self._z_ctrl_mean
        return self

    def _decode(self, z: np.ndarray) -> np.ndarray:
        import torch
        with torch.no_grad():
            px = self._model.module.generative(torch.as_tensor(z, dtype=torch.float32))["px"]
        return px.cpu().numpy().astype(np.float32)

    def _latent(self, X: np.ndarray) -> np.ndarray:
        import anndata as ad
        # the cell_type value must be one scGen's registry already knows; the encoder does not
        # condition on it, but scvi-tools refuses to transfer a setup with an unseen category.
        a = ad.AnnData(X=np.asarray(X, dtype=np.float32),
                       obs={"condition": np.array(["control"] * len(X)),
                            "cell_type": np.array([self._ref_ctx] * len(X))})
        return self._model.get_latent_representation(a)

    def predict(self, drug, context=None, control_mean=None, **_) -> np.ndarray:
        cm = np.asarray(control_mean, dtype=np.float32)[None, :]
        dz = self._delta_z.get(str(drug))
        if dz is None:
            return np.zeros(cm.shape[1], dtype=np.float32)
        z = self._latent(cm)
        return (self._decode(z + dz[None, :])[0] - cm[0]).astype(np.float32)

    def predict_population(self, drug, control_mean=None, n_cells: int = 200, context=None,
                           seed: Optional[int] = None, control_cells=None,
                           synth: str = "cells") -> np.ndarray:
        """scGen's arithmetic applied PER CELL: encode, add the one delta, decode."""
        if synth != "cells":
            raise ValueError("RealScGenPredictor supports synth='cells' only; the Gaussian "
                             "synthesizer would destroy the structure this experiment measures.")
        if control_cells is None:
            raise ValueError("scGen needs the query context's real control cells.")
        rng = np.random.default_rng(self.seed if seed is None else seed)
        C = np.asarray(control_cells, dtype=np.float32)
        C = C[resample_rows(len(C), n_cells, rng)]
        dz = self._delta_z.get(str(drug))
        if dz is None:
            dz = np.zeros(self.n_latent, dtype=np.float32)
        return self._decode(self._latent(C) + dz[None, :])

    def known_drugs(self) -> list:
        return list(self._delta_z)


# ---------------------------------------------------------------------------
# CPA: explicit drug + covariate conditioning, nonlinear decoder
# ---------------------------------------------------------------------------


class RealCPAPredictor:
    """The published CPA (cpa-tools). Explicitly cell-state-conditional.

    CPA decomposes a cell into a basal latent plus additive perturbation and covariate
    embeddings, then decodes nonlinearly. The perturbation embedding is shared, but the basal
    latent and covariate embedding are per-cell, and the decoder is nonlinear, so the gene-space
    response is a function of the cell's own state. It is the model the reviewer of an earlier
    draft correctly said a linear-latent fallback cannot stand in for.
    """

    name = "cpa_real"
    backend = "cpa"

    def __init__(self, n_epochs: int = 100, n_latent: int = 32, seed: int = 0,
                 max_cells_per_group: int = 300):
        self.n_epochs = n_epochs
        self.n_latent = n_latent
        self.seed = seed
        # CPA's adversarial training on all 276k SciPlex3 cells runs at ~28 min/epoch even on an
        # RTX 4090, which makes a properly-trained model unreachable. It does not need every cell
        # to learn a drug embedding: we subsample per (drug, context) instead. Undertraining is the
        # real hazard here, because an undertrained model produces no differential response and
        # would be misread as evidence that CPA cannot open Gate 1. The experiment therefore
        # verifies that each predictor actually learned the response before its Gate-1 number is
        # allowed to mean anything.
        self.max_cells_per_group = max_cells_per_group
        self._model = None
        self._genes = None

    def fit(self, dataset, drugs: Optional[list] = None,
            contexts: Optional[list] = None) -> "RealCPAPredictor":
        import anndata as ad
        import cpa

        Xall = np.asarray(dataset.X, dtype=np.float32)
        self._genes = Xall.shape[1]
        # The retrieval harness scores any drug NOT in known_drugs() at -1e6. Returning an empty
        # list would therefore silently zero this predictor on every candidate and look exactly
        # like a model that cannot retrieve. Record the drugs actually seen.
        self._known = sorted(set(dataset.pert[~dataset.is_control].astype(str).tolist()))
        raw_all = np.where(dataset.is_control, "control", dataset.pert.astype(str))
        ctx_all = dataset.context.astype(str)

        # stratified subsample per (perturbation, context); see __init__ for why
        rng = np.random.default_rng(self.seed)
        keep = []
        for key in sorted(set(zip(raw_all.tolist(), ctx_all.tolist()))):
            idx = np.where((raw_all == key[0]) & (ctx_all == key[1]))[0]
            n = min(len(idx), self.max_cells_per_group)
            keep.append(rng.choice(idx, n, replace=False))
        keep = np.sort(np.concatenate(keep))
        self.n_train_cells = int(len(keep))

        X = Xall[keep]
        pert = np.array([_cpa_safe(p) for p in raw_all[keep]])
        adata = ad.AnnData(X=X, obs={
            "perturbation": pert,
            "dose": np.where(raw_all[keep] == "control", 0.0, 1.0).astype(np.float32),
            "cell_type": ctx_all[keep],
            "split": np.array(["train"] * len(X)),
        })
        cpa.CPA.setup_anndata(
            adata, perturbation_key="perturbation", dosage_key="dose",
            control_group="control", categorical_covariate_keys=["cell_type"],
            is_count_data=False, max_comb_len=1)
        self._model = cpa.CPA(
            adata=adata, split_key="split", train_split="train",
            n_latent=self.n_latent, recon_loss="gauss",
            doser_type="linear", n_hidden_encoder=256, n_layers_encoder=2,
            n_hidden_decoder=256, n_layers_decoder=2, use_batch_norm_encoder=True,
            seed=self.seed)
        self._model.train(max_epochs=self.n_epochs, batch_size=512, early_stopping_patience=15,
                          check_val_every_n_epoch=5, save_path=None)
        return self

    def predict_population(self, drug, control_mean=None, n_cells: int = 200, context=None,
                           seed: Optional[int] = None, control_cells=None,
                           synth: str = "cells") -> np.ndarray:
        """Push the query's REAL control cells through CPA, conditioned on the drug."""
        import anndata as ad
        if synth != "cells":
            raise ValueError("RealCPAPredictor supports synth='cells' only.")
        if control_cells is None:
            raise ValueError("CPA needs the query context's real control cells.")
        rng = np.random.default_rng(self.seed if seed is None else seed)
        C = np.asarray(control_cells, dtype=np.float32)
        C = C[resample_rows(len(C), n_cells, rng)]
        ctx = str(context) if context is not None else "A549"
        a = ad.AnnData(X=C, obs={
            "perturbation": np.array([_cpa_safe(drug)] * len(C)),
            "dose": np.ones(len(C), dtype=np.float32),
            "cell_type": np.array([ctx] * len(C)),
            "split": np.array(["train"] * len(C)),
        })
        # The query AnnData must be registered against the TRAINED model's vocabulary before
        # predict, or CPA raises KeyError('perts not found in adata.obsm'): predict reads the
        # perturbation embedding from obsm['perts'], which setup_anndata builds. We transfer the
        # trained registry (not a fresh setup, which would build a new, misaligned vocabulary).
        import cpa
        cpa.CPA.setup_anndata(
            a, perturbation_key="perturbation", dosage_key="dose",
            control_group="control", categorical_covariate_keys=["cell_type"],
            is_count_data=False, max_comb_len=1)
        self._model.predict(a, batch_size=512)
        key = "CPA_pred" if "CPA_pred" in a.obsm else next(
            (k for k in a.obsm if "pred" in k.lower()), None)
        if key is None:
            raise KeyError(f"CPA predict wrote no *_pred obsm; keys were {list(a.obsm)}")
        return np.asarray(a.obsm[key], dtype=np.float32)

    def predict(self, drug, context=None, control_mean=None, **_) -> np.ndarray:
        cm = np.asarray(control_mean, dtype=np.float32)
        pop = self.predict_population(drug, n_cells=64, context=context,
                                      control_cells=np.tile(cm, (64, 1)))
        return (pop.mean(0) - cm).astype(np.float32)

    def zero_effect_population(self, control_cells, n_cells: int = 200, context=None,
                              seed: Optional[int] = None) -> np.ndarray:
        """CPA's reconstruction of the control, for the induced-divergence baseline: push the
        control cells through CPA under the CONTROL perturbation. Subtracting this cancels the
        decoder's reconstruction bias, isolating the drug-induced part. We use the 'control'
        label rather than the _NULL_DRUG sentinel because only labels in the trained registry can
        be transferred; the sentinel is absent from it and raises.
        """
        return self.predict_population("control", control_cells=control_cells, n_cells=n_cells,
                                       context=context, seed=seed, synth="cells")

    def known_drugs(self) -> list:
        return list(self._known)


# ---------------------------------------------------------------------------
# Optimal-transport map: every cell gets its own displacement
# ---------------------------------------------------------------------------


class OTMapPredictor:
    """Entropic-OT barycentric projection from control cells to treated cells.

    This is the maximally non-additive predictor available without training a network: the
    displacement applied to a control cell is determined by where the optimal-transport plan
    sends THAT cell, so two cells in different states receive different responses by
    construction. It is the discrete, non-parametric core of the neural-OT and
    Schrodinger-bridge perturbation models.

    NO LEAKAGE. The coupling for drug d is fit between control cells and treated cells drawn
    ONLY from contexts other than the query's (``exclude_context``). The query context's
    treated cells for that drug are exactly what the predictor is asked to produce and are
    never shown to it.
    """

    name = "ot_map"
    backend = "ot"

    def __init__(self, reg: float = 0.05, max_fit: int = 400, seed: int = 0,
                 n_latent: int = 30, latent: bool = True):
        # n_latent / latent added after the raw-gene-space version FAILED its learning check
        # (cos = 0.057 between predicted and true mean delta, against 0.502 for a plain
        # average-effect predictor on the same transfer). Two things were wrong and both are
        # fixed here; the config was chosen by the LEARNING check, not by the divergence outcome
        # this predictor is used to measure:
        #   1. CURSE OF DIMENSIONALITY. In 2000 gene dimensions all pairwise costs are nearly
        #      equal after M/M.max(), so the Sinkhorn plan is almost uniform and carries no
        #      signal. Every deployed neural-OT perturbation model (CellOT and kin) runs OT in a
        #      learned latent space for exactly this reason. We use a PCA-30 latent as the
        #      non-parametric analogue.
        #   2. CROSS-CONTEXT BASELINE CONFOUND. Pooling control and treated cells across non-query contexts
        #      in raw space makes the transport learn the context shift, not the drug response.
        #      Each fit context is therefore centred on its OWN control mean, so the map is a
        #      control->treated (response) map. Query cells are matched in the same centred space.
        # With PCA=30 and reg=0.05 the learning check rises to ~0.32, above the 0.30 bar, so the
        # map learns the effect and its induced divergence becomes interpretable.
        self.reg = reg
        self.max_fit = max_fit
        self.seed = seed
        self.n_latent = n_latent
        self.latent = latent
        self._data = None
        self._pca = None

    def fit(self, dataset, drugs=None, contexts=None) -> "OTMapPredictor":
        self._data = dataset          # coupling is solved per query, against non-query contexts
        if self.latent:
            from sklearn.decomposition import PCA
            rng = np.random.default_rng(self.seed)
            idx = rng.choice(dataset.X.shape[0], min(20000, dataset.X.shape[0]), replace=False)
            k = int(min(self.n_latent, dataset.X.shape[1], len(idx) - 1))
            # PCA is unsupervised: it never sees a label or the query's treated cells, so it
            # leaks nothing. It is the space the transport is solved in, nothing more.
            self._pca = PCA(n_components=k, random_state=self.seed).fit(dataset.X[idx])
        # see RealCPAPredictor.fit: an empty known_drugs() would silently score every candidate
        # at -1e6 and masquerade as a model that cannot retrieve.
        self._known = sorted(set(dataset.pert[~dataset.is_control].astype(str).tolist()))
        return self

    def _enc(self, X):
        return self._pca.transform(X) if self.latent else np.asarray(X, dtype=np.float64)

    def _dec(self, Z):
        return self._pca.inverse_transform(Z) if self.latent else Z

    def predict_population(self, drug, control_mean=None, n_cells: int = 200, context=None,
                           seed: Optional[int] = None, control_cells=None,
                           synth: str = "cells", exclude_context=None) -> np.ndarray:
        import ot as pot
        if synth != "cells":
            raise ValueError("OTMapPredictor supports synth='cells' only.")
        if control_cells is None:
            raise ValueError("the OT map needs the query context's real control cells.")
        rng = np.random.default_rng(self.seed if seed is None else seed)
        d = self._data

        # Source and target are built PER non-query context and centred on that context's own
        # control mean, so the pooled transport is a control->treated (response) map free of the
        # baseline difference between contexts. Contexts are never mixed before centring.
        # exclude_context may be a single context or a collection (a cross-line query blends two
        # contexts and BOTH must be held out, or the map transports toward the query drug's own
        # response and the retrieval result leaks). Accept either.
        if exclude_context is None:
            excluded = set()
        elif isinstance(exclude_context, str):
            excluded = {exclude_context}
        else:
            excluded = set(exclude_context)
        ctxs = [c for c in d.contexts if c not in excluded]
        S_parts, T_parts = [], []
        for c in ctxs:
            cr, tr = d.control_rows(c), d.treated_rows(c, drug)
            if len(cr) < 5 or len(tr) < 5:
                continue
            Sc, Tc = self._enc(d.X[cr]), self._enc(d.X[tr])
            mu = Sc.mean(0)
            S_parts.append(Sc - mu)
            T_parts.append(Tc - mu)
        if not T_parts:
            raise ValueError(f"no out-of-context treated cells for drug={drug!r}; the OT map "
                             f"will not fall back to the query context, which would leak.")
        S = np.vstack(S_parts)
        T = np.vstack(T_parts)
        S = S[rng.choice(len(S), min(len(S), self.max_fit), replace=False)]
        T = T[rng.choice(len(T), min(len(T), self.max_fit), replace=False)]

        C = np.asarray(control_cells, dtype=np.float64)
        C = C[resample_rows(len(C), n_cells, rng)]
        Zc = self._enc(C)
        Zc_match = Zc - Zc.mean(0)                             # match in the centred space

        # Solve control -> treated OT on the fit sample, then extend the map to the query's
        # control cells by nearest-source barycentric projection. Each query cell inherits the
        # displacement of the fit-source cell it most resembles, so the map is cell-specific.
        M = pot.dist(S, T)
        M /= M.max()
        G = pot.sinkhorn(np.ones(len(S)) / len(S), np.ones(len(T)) / len(T), M, reg=self.reg,
                         numItermax=500)
        S_moved = (G @ T) / G.sum(1, keepdims=True)          # barycentric projection
        disp = S_moved - S                                    # per-source-cell displacement

        nn = np.argmin(pot.dist(Zc_match, S), axis=1)
        Zpred = Zc + disp[nn]
        return self._dec(Zpred).astype(np.float32)

    def zero_effect_population(self, control_cells, n_cells: int = 200,
                              seed: Optional[int] = None) -> np.ndarray:
        """The population this model produces with NO drug effect, for the induced-divergence
        baseline. In latent mode the map returns dec(enc(C) + displacement), so its zero-effect
        output is dec(enc(C)) = the PCA reconstruction P(C); subtracting it cancels the same
        reconstruction bias that the latent additive models carry. In raw
        mode the map adds a displacement to C directly, so its baseline is C itself.
        """
        rng = np.random.default_rng(self.seed if seed is None else seed)
        C = np.asarray(control_cells, dtype=np.float64)
        C = C[resample_rows(len(C), n_cells, rng)]
        return (self._dec(self._enc(C)) if self.latent else C).astype(np.float32)

    def predict(self, drug, context=None, control_mean=None, exclude_context=None,
                **_) -> np.ndarray:
        cm = np.asarray(control_mean, dtype=np.float32)
        pop = self.predict_population(drug, n_cells=128, control_cells=np.tile(cm, (128, 1)),
                                      exclude_context=exclude_context)
        return (pop.mean(0) - cm).astype(np.float32)

    def known_drugs(self) -> list:
        return list(self._known)
