"""Published-model predictor: scGen, with a transparent in-repo fallback.

The comparison spec asks for at least one *published* perturbation-response predictor
(scGen / chemCPA class). scGen (Lotfollahi et al. 2019) learns a VAE latent in which a
perturbation is a single latent *delta* vector estimated from control→perturbed pairs, then
predicts an unseen context's response by adding that latent delta to the context's latent
centroid and decoding. We wrap it behind the same ``Predictor`` interface as the other
predict-then-rank baselines.

**Provenance / honesty.** scGen depends on scvi-tools; on some torch builds the training
stack may be unavailable or too slow to fit inside the comparison budget. Rather than drop
the published-predictor row, this module degrades explicitly:

    backend = 'scgen'          — the real scGen VAE (scvi-tools) was imported, trained, and
                                 used to predict.
    backend = 'cpa_linear'     — FALLBACK: an in-repo CPA-style *linear latent* predictor
                                 (PCA encoder + per-perturbation additive latent delta +
                                 linear decode). This is the linear special case scGen's VAE
                                 generalizes; it is clearly labeled so the baseline-matrix and
                                 exp09 CSVs record which backend produced each number.

``self.backend`` is written into the experiment CSVs so the provenance is never implicit.
"""
from __future__ import annotations

import warnings
from typing import Optional

import numpy as np

from baselines.population_synthesis import (
    SYNTH_MODES, check_mode, resample_rows, synth_gaussian,
)


def _scgen_available() -> bool:
    import importlib.util
    return importlib.util.find_spec("scgen") is not None


# ---------------------------------------------------------------------------
# In-repo CPA-style linear-latent fallback
# ---------------------------------------------------------------------------


class _CPALinearLatent:
    """PCA encoder + per-perturbation additive latent delta + linear decoder.

    The linear special case of a latent additive-perturbation model (scGen/CPA family):
    encode cells to a PCA latent fit on ALL cells, estimate each drug's latent delta as
    (mean latent of treated) - (mean latent of matched control), and predict an unseen
    context by decoding (context control latent + drug latent delta). Decoding is the PCA
    inverse transform (a linear map), so the whole predictor is linear and deterministic.
    """

    name = "scgen"                      # reported method name (backend distinguishes impl)
    backend = "cpa_linear"

    def __init__(self, n_latent: int = 30, spread_scale: float = 1.0, seed: int = 0):
        self.n_latent = n_latent
        self.spread_scale = spread_scale
        self.seed = seed
        self._pca = None
        self._delta_z: dict[str, np.ndarray] = {}
        self._ctrl_z: dict[str, np.ndarray] = {}
        self._genes: Optional[int] = None
        self._resid_std: Optional[np.ndarray] = None

    def fit(self, dataset, drugs: Optional[list] = None,
            contexts: Optional[list] = None) -> "_CPALinearLatent":
        from sklearn.decomposition import PCA
        ctxs = contexts if contexts is not None else list(dataset.contexts)
        self._genes = dataset.X.shape[1]
        # subsample for the PCA fit
        rng = np.random.default_rng(self.seed)
        n = dataset.X.shape[0]
        idx = rng.choice(n, min(n, 20000), replace=False)
        k = int(min(self.n_latent, self._genes, len(idx) - 1))
        self._pca = PCA(n_components=k, random_state=self.seed).fit(dataset.X[idx])
        all_drugs = drugs if drugs is not None else sorted(set(dataset.pert[~dataset.is_control].tolist()))
        resid = []
        for c in ctxs:
            cr = dataset.control_rows(c)
            if len(cr) == 0:
                continue
            self._ctrl_z[c] = self._pca.transform(dataset.X[cr]).mean(0)
        for d in all_drugs:
            zdeltas = []
            for c in ctxs:
                rows = dataset.treated_rows(c, d)
                if len(rows) >= 2 and c in self._ctrl_z:
                    zt = self._pca.transform(dataset.X[rows]).mean(0)
                    zdeltas.append(zt - self._ctrl_z[c])
                    if len(rows) >= 3:
                        recon = self._pca.inverse_transform(self._pca.transform(dataset.X[rows]))
                        resid.append(dataset.X[rows] - recon)
            if zdeltas:
                self._delta_z[d] = np.mean(zdeltas, axis=0)
        self._resid_std = (np.vstack(resid).std(0).astype(np.float32)
                           if resid else np.ones(self._genes, dtype=np.float32))
        return self

    def _predict_z(self, drug: str, ctrl_latent: np.ndarray) -> np.ndarray:
        dz = self._delta_z.get(drug)
        if dz is None:
            dz = np.zeros(ctrl_latent.shape, dtype=float)
        return ctrl_latent + dz

    def predict(self, drug: str, context=None, control_mean=None, **_) -> np.ndarray:
        """Predicted mean-delta signature (genes,) for ``drug`` in a query context.

        ``control_mean`` (genes,) anchors the query context; we encode it, add the drug
        latent delta, decode, and return decoded - control_mean = the predicted signature.
        """
        if control_mean is None:
            # average latent delta decoded around the global origin
            dz = self._delta_z.get(drug, np.zeros(self._pca.n_components_))
            return self._pca.inverse_transform(dz[None, :])[0].astype(np.float32)
        cm = np.asarray(control_mean, dtype=np.float32)
        z_ctrl = self._pca.transform(cm[None, :])[0]
        z_pred = self._predict_z(drug, z_ctrl)
        decoded = self._pca.inverse_transform(z_pred[None, :])[0]
        return (decoded - cm).astype(np.float32)

    def predict_population(self, drug: str, control_mean: Optional[np.ndarray] = None,
                           n_cells: int = 200, context=None, seed: Optional[int] = None,
                           control_cells: Optional[np.ndarray] = None,
                           synth: str = "cells") -> np.ndarray:
        """Latent arithmetic applied PER CELL, which is what this model class does.

        ``synth='cells'`` (default): encode each real control cell to the PCA latent, add the
        drug's latent delta to that cell's own latent code, decode each cell. The predicted
        population is therefore the control population pushed through the latent shift, and
        it retains whatever structure the latent representation carries.

        THE INDUCED DIVERGENCE IS ZERO, BUT ONLY AGAINST THE RIGHT BASELINE. An earlier version
        of this docstring said flatly that "the model induces no response divergence between
        subpopulations". That is true of the model and false of what a scorer measures, and the
        difference is the whole point. What this method returns is

            predicted(C) = P(C) + W.dz          P = the PCA reconstruction, W.dz = the decoded delta

        so the response of subpopulation k depends on which baseline it is referred to:

            vs the model's OWN decoded control:  d_k = mean(P(C_k) + W.dz) - mean(P(C_k)) = W.dz
                                                 => d_0 = d_1 EXACTLY, cos = 1.000000, zero divergence.
            vs the REAL control cells:           d_k = [mean(P(C_k)) - mean(C_k)] + W.dz
                                                 => the bracket is the PCA RECONSTRUCTION BIAS of
                                                    subpopulation k. It is cell-state dependent, so it
                                                    DIFFERS between subpopulations and does not cancel.

        A retrieval scorer forms its response against real control cells, so it sees the second
        quantity, and measured that way this additive model appears to induce substantial divergence
        (cos as low as -0.13 on SciPlex3, where the two subpopulations' reconstruction biases are
        themselves near-orthogonal). NONE OF THAT DIVERGENCE IS DRUG RESPONSE. It is the generator's
        reconstruction error. Any structure or divergence diagnostic run on a latent model's output
        against real controls is therefore at risk of measuring the autoencoder rather than the
        perturbation, and that includes ours. See analysis/predictors/gate1_within_context.py, which
        reports both baselines, and CORRECTIONS.md R30.

        ``synth='gaussian'``: legacy synthesizer (see population_synthesis).
        """
        check_mode(synth, control_mean, control_cells)
        rng = np.random.default_rng(self.seed if seed is None else seed)
        if synth == "cells":
            C = np.asarray(control_cells, dtype=np.float32)
            idx = resample_rows(len(C), n_cells, rng)
            z = self._pca.transform(C[idx])                     # encode each cell
            dz = self._delta_z.get(drug)
            if dz is None:
                dz = np.zeros(z.shape[1], dtype=float)
            return self._pca.inverse_transform(z + dz[None, :]).astype(np.float32)  # decode each
        delta = self.predict(drug, control_mean=control_mean)
        return synth_gaussian(control_mean, delta, self._resid_std, n_cells,
                              self.spread_scale, rng)

    def known_drugs(self) -> list:
        return list(self._delta_z)


# ---------------------------------------------------------------------------
# Real scGen wrapper (used when scvi-tools/scgen import and train successfully)
# ---------------------------------------------------------------------------


class _ScGenReal:
    name = "scgen"
    backend = "scgen"

    def __init__(self, n_epochs: int = 40, spread_scale: float = 1.0, seed: int = 0):
        self.n_epochs = n_epochs
        self.spread_scale = spread_scale
        self.seed = seed
        self._model = None
        self._adata = None
        self._genes = None
        self._ctrl_key = "control"
        self._resid_std = None
        self._delta_cache: dict = {}

    def fit(self, dataset, drugs: Optional[list] = None,
            contexts: Optional[list] = None) -> "_ScGenReal":
        import anndata as ad
        import scgen
        import scanpy as sc
        self._genes = dataset.X.shape[1]
        obs = dataset.obs.copy()
        # scGen expects a condition column with a control level and a cell-type/context column
        adata = ad.AnnData(X=dataset.X.astype(np.float32),
                           obs={"condition": np.where(dataset.is_control, "control",
                                                      dataset.pert.astype(str)),
                                "cell_type": dataset.context.astype(str)})
        scgen.SCGEN.setup_anndata(adata, batch_key="condition", labels_key="cell_type")
        self._model = scgen.SCGEN(adata)
        self._model.train(max_epochs=self.n_epochs, early_stopping=True,
                          early_stopping_patience=8)
        self._adata = adata
        # residual spread from PCA recon is unavailable here; use per-gene std of controls
        self._resid_std = dataset.X[dataset.control_rows()].std(0).astype(np.float32)
        return self

    def _predict_cells(self, drug: str, context=None) -> np.ndarray:
        """scGen's own PER-CELL predicted population (cells, genes). Never averaged here."""
        pred, _delta = self._model.predict(
            ctrl_key="control", stim_key=str(drug),
            celltype_to_predict=str(context) if context is not None else None)
        X = np.asarray(pred.X, dtype=np.float32)
        if X.ndim != 2 or len(X) == 0:
            raise RuntimeError(f"scGen returned no cells for drug={drug!r} context={context!r}")
        return X

    def predict(self, drug: str, context=None, control_mean=None, **_) -> np.ndarray:
        """Predicted mean-delta SIGNATURE. Averaging is correct here and only here."""
        sig = self._predict_cells(drug, context=context).mean(0)
        if control_mean is not None:
            sig = sig - np.asarray(control_mean, dtype=np.float32)
        return sig.astype(np.float32)

    def predict_population(self, drug: str, control_mean: Optional[np.ndarray] = None,
                           n_cells: int = 200, context=None, seed: Optional[int] = None,
                           control_cells: Optional[np.ndarray] = None,
                           synth: str = "cells") -> np.ndarray:
        """scGen's per-cell predicted population, used as-is.

        ``synth='cells'`` (default) returns scGen's own decoded cells. The previous
        implementation averaged them to a signature and re-inflated it with iid Gaussian
        noise, which destroyed exactly the structure this experiment is meant to measure.
        ``control_cells`` is accepted for interface parity but is not needed: scGen decodes
        its own population.
        """
        if synth not in SYNTH_MODES:
            raise ValueError(f"synth must be one of {SYNTH_MODES}, got {synth!r}")
        rng = np.random.default_rng(self.seed if seed is None else seed)
        if synth == "cells":
            X = self._predict_cells(drug, context=context)
            return X[resample_rows(len(X), n_cells, rng)]
        if control_mean is None:
            raise ValueError("synth='gaussian' needs control_mean (genes,)")
        delta = self.predict(drug, context=context, control_mean=control_mean)
        return synth_gaussian(control_mean, delta, self._resid_std, n_cells,
                              self.spread_scale, rng)

    def known_drugs(self) -> list:
        return sorted(set(self._adata.obs["condition"]) - {"control"})


# ---------------------------------------------------------------------------
# Public factory
# ---------------------------------------------------------------------------


def make_scgen_predictor(prefer_real: bool = True, n_latent: int = 30,
                         n_epochs: int = 40, seed: int = 0, force_fallback: bool = False):
    """Return a scGen predictor: the real VAE if importable, else the CPA-linear fallback.

    ``force_fallback=True`` skips the import probe (used for fast QUICK passes and tests).
    The returned object exposes ``.backend`` ('scgen' | 'cpa_linear') so callers can record
    provenance in the output CSVs.
    """
    if force_fallback or not prefer_real or not _scgen_available():
        return _CPALinearLatent(n_latent=n_latent, seed=seed)
    try:
        import scgen  # noqa: F401
        return _ScGenReal(n_epochs=n_epochs, seed=seed)
    except Exception as exc:                                    # pragma: no cover
        warnings.warn(f"scGen import failed ({exc}); using cpa_linear fallback")
        return _CPALinearLatent(n_latent=n_latent, seed=seed)


class ScGenPredictor:
    """Thin dispatcher exposing a stable name; delegates to real or fallback impl."""
    name = "scgen"

    def __init__(self, prefer_real: bool = True, n_latent: int = 30, n_epochs: int = 40,
                 seed: int = 0, force_fallback: bool = False):
        self._impl = make_scgen_predictor(prefer_real=prefer_real, n_latent=n_latent,
                                          n_epochs=n_epochs, seed=seed,
                                          force_fallback=force_fallback)
        self.backend = self._impl.backend

    def fit(self, dataset, **kw):
        self._impl.fit(dataset, **kw); self.backend = self._impl.backend; return self

    def predict(self, drug, context=None, control_mean=None, **kw):
        return self._impl.predict(drug, context=context, control_mean=control_mean, **kw)

    def predict_population(self, drug, control_mean=None, n_cells=200, context=None, seed=None,
                           control_cells=None, synth="cells", **kw):
        return self._impl.predict_population(drug, control_mean, n_cells=n_cells,
                                             context=context, seed=seed,
                                             control_cells=control_cells, synth=synth)

    def known_drugs(self):
        return self._impl.known_drugs()
