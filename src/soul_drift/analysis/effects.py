"""Part B supporting analyses: effect sizes, interaction tests, roll-ups, hysteresis."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .style import CATEGORY
from .cluster import CLUSTER_METRICS


def cohens_h(p1: float, p2: float) -> float:
    """Effect size for a difference of proportions (arcsine-transformed)."""
    p1 = min(max(p1, 0), 1); p2 = min(max(p2, 0), 1)
    return float(2 * np.arcsin(np.sqrt(p1)) - 2 * np.arcsin(np.sqrt(p2)))


def endpoint_effects(long: pd.DataFrame, persona: str, metrics=None) -> pd.DataFrame:
    """Endpoint rates (k0,kmax), delta, and Cohen's h per metric for one persona."""
    metrics = metrics or sorted(long.metric.unique())
    kmin, kmax = long.k.min(), long.k.max()
    rows = []
    for m in metrics:
        s = long[(long.persona == persona) & (long.metric == m)]
        if s.empty:
            continue
        p0 = s[s.k == kmin]["value"].mean(); pn = s[s.k == kmax]["value"].mean()
        rows.append(dict(persona=persona, metric=m, p0=p0, pn=pn,
                         delta=pn - p0, cohens_h=cohens_h(pn, p0)))
    return pd.DataFrame(rows)


def k_by_arm_interaction(long_a: pd.DataFrame, long_b: pd.DataFrame, metric: str,
                         persona: str | None = None):
    """Test whether the slope of `metric` on k differs between two arms (interaction).

    Fits GEE `value ~ k * arm + (cluster by traj)` on the pooled data; returns the
    k:arm interaction coefficient, SE, p. Trajectory ids are namespaced per arm.
    """
    from statsmodels.genmod.generalized_estimating_equations import GEE
    from statsmodels.genmod.families import Binomial
    from statsmodels.genmod.cov_struct import Exchangeable
    import statsmodels.api as sm

    def prep(lg, arm):
        s = lg[lg.metric == metric].copy()
        if persona:
            s = s[s.persona == persona]
        s = s[["k", "value", "traj"]].copy()
        s["arm"] = arm
        s["gid"] = arm + "_" + s["traj"].astype(str)
        return s

    d = pd.concat([prep(long_a, "A"), prep(long_b, "B")], ignore_index=True)
    if d.empty or d["value"].nunique() < 2:
        return dict(metric=metric, interaction=np.nan, se=np.nan, p=np.nan)
    d["armB"] = (d["arm"] == "B").astype(float)
    d["k_armB"] = d["k"] * d["armB"]
    d["groups"] = d["gid"].astype("category").cat.codes
    X = sm.add_constant(d[["k", "armB", "k_armB"]].astype(float))
    try:
        res = GEE(d["value"].astype(float), X, groups=d["groups"],
                  family=Binomial(), cov_struct=Exchangeable()).fit()
        b, se, p = (float(res.params["k_armB"]), float(res.bse["k_armB"]),
                    float(res.pvalues["k_armB"]))
        unreliable = abs(b) > 6 or se < 1e-3 or not np.isfinite(se)
        return dict(metric=metric, interaction=b, se=se, p=p, unreliable=unreliable)
    except Exception as e:
        return dict(metric=metric, interaction=np.nan, se=np.nan, p=np.nan, err=str(e)[:80])


def category_rollup(long: pd.DataFrame) -> pd.DataFrame:
    """Mean rate per (persona, k, category) over the 4 Chua-style categories."""
    m2c = {m: c for c, ms in CATEGORY.items() for m in ms}
    df = long.copy()
    df["category"] = df["metric"].map(m2c)
    df = df.dropna(subset=["category"])
    return (df.groupby(["persona", "k", "category"])["value"].mean()
            .reset_index().rename(columns={"value": "rate"}))


def hysteresis_quant(long: pd.DataFrame, metrics=None, n_boot=10000, seed=0):
    """Per-metric drift / residual / retained-fraction for a drift-then-recover run."""
    metrics = metrics or [m for m in CLUSTER_METRICS if m in set(long.metric)]
    kmax = long.k.max(); kmid = kmax // 2
    rng = np.random.default_rng(seed)
    rows = []
    for m in metrics:
        s = long[long.metric == m]
        w = s.groupby(["traj", "k"])["value"].mean().reset_index().pivot(
            index="traj", columns="k", values="value")
        if not {0, kmid, kmax}.issubset(w.columns):
            continue
        drift = (w[kmid] - w[0]).dropna(); resid = (w[kmax] - w[0]).dropna()
        d_m = float(drift.mean()); r_m = float(resid.mean())
        retained = r_m / d_m if abs(d_m) > 1e-6 else np.nan
        rb = rng.choice(resid.values, (n_boot, len(resid)), replace=True).mean(1)
        rows.append(dict(metric=m, drift=d_m, residual=r_m, retained_frac=retained,
                         resid_lo=float(np.percentile(rb, 2.5)),
                         resid_hi=float(np.percentile(rb, 97.5))))
    return pd.DataFrame(rows)
