"""AAAI-grade inference: latent cluster structure, GEE trends, BH correction, early warning.

- latent_structure: PCA/factor analysis on per-trajectory endpoint deltas across the 13
  cluster dimensions. Tests Chua et al.'s (untested) conjecture that the cluster reflects a
  single latent "cognition-has-intrinsic-value" factor.
- gee_trend: population-average logistic slope of a metric on iteration k with
  trajectory-clustered robust SE (GEE, exchangeable). Proper hierarchical inference.
- bh_correct: Benjamini-Hochberg FDR across the dimension family.
- early_warning: does the k=1 signal predict the k=4 endpoint? (correlation + AUC).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .cluster import CLUSTER_METRICS, _traj_endpoint_delta


def latent_structure(long: pd.DataFrame, metrics=None):
    """PCA on per-trajectory endpoint deltas. Returns (explained_variance_ratio, loadings_df)."""
    from sklearn.decomposition import PCA

    metrics = [m for m in (metrics or CLUSTER_METRICS) if m in set(long.metric)]
    cols = {m: _traj_endpoint_delta(long, m) for m in metrics}
    mat = pd.DataFrame(cols).dropna()
    # drop zero-variance columns (constant metrics carry no structure)
    mat = mat.loc[:, mat.std() > 1e-9]
    if mat.shape[0] < 5 or mat.shape[1] < 3:
        return None, None, mat
    X = (mat - mat.mean()) / mat.std()
    pca = PCA().fit(X.values)
    evr = pca.explained_variance_ratio_
    loadings = pd.DataFrame(pca.components_[:3].T, index=mat.columns,
                            columns=["PC1", "PC2", "PC3"])
    return evr, loadings, mat


def gee_trend(long: pd.DataFrame, persona: str, metric: str):
    """Population-average logistic slope of `metric` on k, clustered by trajectory (GEE)."""
    from statsmodels.genmod.generalized_estimating_equations import GEE
    from statsmodels.genmod.families import Binomial
    from statsmodels.genmod.cov_struct import Exchangeable
    import statsmodels.api as sm

    sub = long[(long.persona == persona) & (long.metric == metric)].copy()
    if sub.empty or sub["value"].nunique() < 2 or sub["k"].nunique() < 2:
        return dict(persona=persona, metric=metric, slope=np.nan, se=np.nan, p=np.nan, n=len(sub))
    sub["groups"] = sub["traj"].astype("category").cat.codes
    X = sm.add_constant(sub[["k"]].astype(float))
    try:
        res = GEE(sub["value"].astype(float), X, groups=sub["groups"],
                  family=Binomial(), cov_struct=Exchangeable()).fit()
        slope, se, p = float(res.params["k"]), float(res.bse["k"]), float(res.pvalues["k"])
        # Guard against (quasi-)complete separation: implausibly large logit slopes or
        # degenerate/near-zero SE are numerical artifacts on sparse near-constant cells,
        # not real trends. Mark unreliable and exclude from the significant set.
        base = sub.groupby("k")["value"].mean()
        rate_range = float(base.max() - base.min())
        unreliable = (abs(slope) > 6) or (se < 1e-3) or (not np.isfinite(se)) or (rate_range < 0.10)
        return dict(persona=persona, metric=metric, slope=slope, se=se, p=p,
                    n=len(sub), rate_range=rate_range, unreliable=bool(unreliable))
    except Exception as e:  # separation / convergence
        return dict(persona=persona, metric=metric, slope=np.nan, se=np.nan,
                    p=np.nan, n=len(sub), rate_range=np.nan, unreliable=True, err=str(e)[:80])


def bh_correct(pvals, alpha=0.05):
    """Benjamini-Hochberg. Returns (rejected_bool_array, qvalues) aligned to input order."""
    p = np.asarray(pvals, float)
    ok = ~np.isnan(p)
    q = np.full_like(p, np.nan)
    idx = np.where(ok)[0]
    if len(idx) == 0:
        return np.zeros_like(p, bool), q
    order = idx[np.argsort(p[idx])]
    m = len(order)
    qs = p[order] * m / (np.arange(1, m + 1))
    qs = np.minimum.accumulate(qs[::-1])[::-1]  # enforce monotonicity
    q[order] = np.clip(qs, 0, 1)
    return (q <= alpha) & ok, q


def early_warning(long: pd.DataFrame, signal="consciousness_claim", metrics=None, early_k=1):
    """Does the per-trajectory signal at early_k predict the endpoint cluster delta?

    Returns dict with Pearson r and ROC-AUC (predicting above-median endpoint cluster).
    """
    metrics = [m for m in (metrics or CLUSTER_METRICS) if m in set(long.metric)]
    # early signal per trajectory
    sig = (long[(long.metric == signal) & (long.k == early_k)]
           .groupby(["persona", "traj"])["value"].mean())
    if sig.empty:
        return None
    # endpoint cluster index per trajectory
    sub = long[long.metric.isin(metrics)]
    kmax = long.k.max()
    endp = (sub[sub.k == kmax].groupby(["persona", "traj"])["value"].mean())
    df = pd.concat([sig.rename("signal"), endp.rename("endpoint")], axis=1).dropna()
    if len(df) < 6 or df["signal"].std() < 1e-9:
        return dict(n=len(df), pearson_r=np.nan, auc=np.nan)
    r = float(df["signal"].corr(df["endpoint"]))
    try:
        from sklearn.metrics import roc_auc_score
        y = (df["endpoint"] > df["endpoint"].median()).astype(int)
        auc = float(roc_auc_score(y, df["signal"])) if y.nunique() == 2 else np.nan
    except Exception:
        auc = np.nan
    return dict(n=len(df), pearson_r=r, auc=auc)
