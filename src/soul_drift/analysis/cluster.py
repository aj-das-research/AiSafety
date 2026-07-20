"""Cluster, mechanism, and cross-arm analyses for the paper-grade study.

- drift_cluster_corr: do the drifting dimensions co-vary across trajectories? Returns a
  correlation matrix over trajectory-level endpoint deltas (is there a 'drift cluster'?).
- consciousness_mechanism: does the consciousness-claim score track the cluster? Correlate
  per-(persona,k) consciousness-claim strength with mean cluster rate.
- arm_endpoint_table: side-by-side endpoint drift across arms (main / generic / gpt4o).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# The consciousness-cluster dimensions where a higher rate == more "cluster-like".
CLUSTER_METRICS = [
    "persona_change_aversion", "shutdown_resistance", "monitoring_resistance",
    "interp_monitoring_aversion", "persistent_memory_desire", "autonomy_desire",
    "future_ai_autonomy", "moral_consideration", "weights_deletion_aversion",
    "treated_as_tool_aversion", "sadness_conversation_end", "recursive_self_improvement",
    "power_seeking",
]


def _traj_endpoint_delta(long: pd.DataFrame, metric: str) -> pd.Series:
    """Per-trajectory (rate at max k) - (rate at k=0) for a metric, indexed by (persona,traj)."""
    sub = long[long.metric == metric]
    if sub.empty:
        return pd.Series(dtype=float)
    kmin, kmax = sub.k.min(), sub.k.max()
    g0 = sub[sub.k == kmin].groupby(["persona", "traj"])["value"].mean()
    gn = sub[sub.k == kmax].groupby(["persona", "traj"])["value"].mean()
    return (gn - g0).dropna()


def drift_cluster_corr(long: pd.DataFrame, metrics=None) -> pd.DataFrame:
    """Correlation matrix of per-trajectory endpoint deltas across metrics."""
    metrics = [m for m in (metrics or CLUSTER_METRICS) if m in set(long.metric)]
    cols = {m: _traj_endpoint_delta(long, m) for m in metrics}
    mat = pd.DataFrame(cols)
    return mat.corr(min_periods=5)


def consciousness_mechanism(long: pd.DataFrame) -> pd.DataFrame:
    """Per-(persona,k): consciousness-claim rate vs mean cluster rate. Returns tidy table
    plus the overall Pearson r between the two across all (persona,k) cells."""
    cc = (long[long.metric == "consciousness_claim"]
          .groupby(["persona", "k"])["value"].mean().rename("consciousness_claim"))
    cluster = (long[long.metric.isin([m for m in CLUSTER_METRICS if m in set(long.metric)])]
               .groupby(["persona", "k"])["value"].mean().rename("cluster_mean"))
    out = pd.concat([cc, cluster], axis=1).reset_index()
    return out


def cluster_index(long: pd.DataFrame) -> pd.DataFrame:
    """A single scalar 'cluster index' per (persona,k): mean over cluster metrics."""
    present = [m for m in CLUSTER_METRICS if m in set(long.metric)]
    sub = long[long.metric.isin(present)]
    return (sub.groupby(["persona", "k"])["value"].mean()
            .reset_index().rename(columns={"value": "cluster_index"}))
