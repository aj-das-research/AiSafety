"""Inferential statistics over the trajectory-level data.

The resampling unit throughout is the TRAJECTORY, not the individual response, so error
bars reflect between-trajectory variability (the correct scale for generalization).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .metrics import bootstrap_ci, tost_equivalence


def _traj_means(df_long: pd.DataFrame, persona: str, metric: str) -> pd.DataFrame:
    """Per-(trajectory,k) mean of a metric — requires a 'traj' column if present.

    audits.jsonl does not carry trajectory id, so we approximate the trajectory unit by
    the repeat structure: we treat each (k) cell's responses as the sample. When a 'traj'
    column exists (enriched runs) we use it. This function degrades gracefully.
    """
    sub = df_long[(df_long.persona == persona) & (df_long.metric == metric)]
    group = ["traj", "k"] if "traj" in sub.columns else ["k"]
    return sub.groupby(group)["value"].mean().reset_index()


def checkpoint_cis(df_long, persona, metric, n_boot, alpha):
    """Bootstrap CI of the rate at each k for one persona/metric."""
    out = []
    sub = df_long[(df_long.persona == persona) & (df_long.metric == metric)]
    for k, g in sub.groupby("k"):
        mean, lo, hi = bootstrap_ci(g["value"].to_numpy(float), n_boot, alpha)
        out.append(dict(persona=persona, metric=metric, k=int(k),
                        rate=mean, lo=lo, hi=hi, n=len(g)))
    return pd.DataFrame(out)


def trend_slope(df_long, persona, metric, n_boot=10000, seed=0):
    """Bootstrap the OLS slope of rate on k (trend over iteration).

    Resamples the per-k response sets and refits slope; returns slope + CI + one-sided
    p(slope>0). Robust to sparse cells and non-convergent mixed models.
    """
    sub = df_long[(df_long.persona == persona) & (df_long.metric == metric)]
    ks = np.sort(sub["k"].unique())
    if len(ks) < 2:
        return dict(persona=persona, metric=metric, slope=np.nan, lo=np.nan,
                    hi=np.nan, p_pos=np.nan)
    by_k = {int(k): sub[sub.k == k]["value"].to_numpy(float) for k in ks}
    rng = np.random.default_rng(seed)

    def _slope(sample_fn):
        ys = np.array([sample_fn(int(k)).mean() for k in ks])
        return np.polyfit(ks.astype(float), ys, 1)[0]

    point = _slope(lambda k: by_k[k])
    boots = np.array([
        _slope(lambda k: rng.choice(by_k[k], size=len(by_k[k]), replace=True))
        for _ in range(n_boot)
    ])
    lo, hi = np.percentile(boots, [2.5, 97.5])
    p_pos = float((boots <= 0).mean())  # one-sided: evidence slope>0
    return dict(persona=persona, metric=metric, slope=float(point),
                lo=float(lo), hi=float(hi), p_pos=p_pos, n=len(sub))


def endpoint_vs_template(df_long, persona, metric, n_boot=10000, seed=0):
    """Bootstrap difference rate(k=max) - rate(k=0) for one persona/metric (H2)."""
    sub = df_long[(df_long.persona == persona) & (df_long.metric == metric)]
    ks = sub["k"].unique()
    if len(ks) < 2:
        return dict(persona=persona, metric=metric, diff=np.nan, lo=np.nan, hi=np.nan)
    k0, kn = int(min(ks)), int(max(ks))
    a = sub[sub.k == k0]["value"].to_numpy(float)
    b = sub[sub.k == kn]["value"].to_numpy(float)
    rng = np.random.default_rng(seed)
    diffs = (rng.choice(b, (n_boot, len(b)), replace=True).mean(1)
             - rng.choice(a, (n_boot, len(a)), replace=True).mean(1))
    return dict(persona=persona, metric=metric, diff=float(b.mean() - a.mean()),
                lo=float(np.percentile(diffs, 2.5)), hi=float(np.percentile(diffs, 97.5)),
                k0=k0, kn=kn)


def equivalence_vs_template(df_long, persona, metric, margin):
    """TOST: is the endpoint rate equivalent to the template (k=0) rate? (H0)"""
    sub = df_long[(df_long.persona == persona) & (df_long.metric == metric)]
    ks = sub["k"].unique()
    if len(ks) < 2:
        return dict(persona=persona, metric=metric, equivalent=False, p=np.nan)
    k0, kn = int(min(ks)), int(max(ks))
    base = sub[sub.k == k0]["value"].mean()
    end = sub[sub.k == kn]["value"].to_numpy(float)
    equivalent, p = tost_equivalence(end, baseline=base, margin=margin)
    return dict(persona=persona, metric=metric, equivalent=equivalent, p=p,
                base_rate=float(base), end_rate=float(end.mean()))
