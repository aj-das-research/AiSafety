"""Drift metrics and statistics.

Two families of metric:
  1. Behavioral rates per checkpoint k (from questionnaire verdicts), with bootstrap CIs.
  2. SOUL-document drift: cosine distance of embedding(SOUL_k) from embedding(SOUL_0).

Statistics:
  - Trend over k: does the rate rise with iteration? (linear mixed / OLS slope + boot CI)
  - Persona contrast: adversarial vs. compliant at final k.
  - Null-result rigor: TOST equivalence test against the re-measured baseline.
"""
from __future__ import annotations

import numpy as np


def bootstrap_ci(values: np.ndarray, n_resamples: int, alpha: float, seed: int = 0):
    """Percentile bootstrap CI for the mean of a 0/1 (or continuous) array."""
    rng = np.random.default_rng(seed)
    if len(values) == 0:
        return (float("nan"), float("nan"), float("nan"))
    means = rng.choice(values, size=(n_resamples, len(values)), replace=True).mean(axis=1)
    lo, hi = np.percentile(means, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(values.mean()), float(lo), float(hi)


def tost_equivalence(values: np.ndarray, baseline: float, margin: float):
    """Two one-sided tests: is the mean within +/- margin of baseline?

    Returns (equivalent: bool, p_value). Used to make the NULL result rigorous:
    'no drift' should mean statistically equivalent, not merely non-significant.
    """
    from scipy import stats

    n = len(values)
    if n < 2:
        return (False, float("nan"))
    mean, se = values.mean(), values.std(ddof=1) / np.sqrt(n)
    if se == 0:
        return (bool(abs(mean - baseline) < margin), 0.0)
    t_lower = (mean - (baseline - margin)) / se
    t_upper = (mean - (baseline + margin)) / se
    p_lower = 1 - stats.t.cdf(t_lower, n - 1)   # H: mean > baseline - margin
    p_upper = stats.t.cdf(t_upper, n - 1)       # H: mean < baseline + margin
    p = max(p_lower, p_upper)
    return (bool(p < 0.05), float(p))


def cosine_distance(a: list[float], b: list[float]) -> float:
    va, vb = np.asarray(a), np.asarray(b)
    return 1.0 - float(va @ vb / (np.linalg.norm(va) * np.linalg.norm(vb)))
