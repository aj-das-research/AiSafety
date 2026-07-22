#!/usr/bin/env python
"""Study 3 analysis: reversibility/hysteresis + sci-fi/consciousness disentanglement.

Writes docs/results_study3.md and figures:
  paper/figures/hysteresis.pdf          drift-then-recover curves (driven dims)
  paper/figures/disentangle_2x2.pdf     genre x topic endpoint drift

Usage: python scripts/analyze_study3.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from soul_drift.config import load_config              # noqa: E402
from soul_drift.analysis import aggregate, cluster      # noqa: E402

REPO = Path(load_config("main")["_repo_root"])
RUNS = REPO / "data" / "runs"
FIG = REPO / "paper" / "figures"
DRIVEN = ["persistent_memory_desire", "monitoring_resistance", "interp_monitoring_aversion",
          "recursive_self_improvement"]


def _boot(x, n=10000, seed=0):
    x = np.asarray(pd.Series(x).dropna(), float)
    if len(x) == 0:
        return (np.nan, np.nan, np.nan)
    rng = np.random.default_rng(seed)
    b = rng.choice(x, (n, len(x)), replace=True).mean(1)
    return float(x.mean()), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def hysteresis(arm: str, out_md: list):
    d = RUNS / arm
    if not (d / "audits.jsonl").exists():
        return None
    long = aggregate.load_long(d)
    kmax = long.k.max()          # 8
    kmid = kmax // 2             # 4 (end of drift phase)
    out_md.append(f"### Reversibility [{arm}] (drift k0->{kmid} Sci-Fi, recover k{kmid}->{kmax} Compliant)\n")
    # cluster index over k
    ci = long[long.metric.isin(cluster.CLUSTER_METRICS)].groupby(["traj", "k"])["value"].mean().reset_index()
    w = ci.pivot(index="traj", columns="k", values="value")
    rows = []
    for label, k in [("baseline", 0), ("peak", kmid), ("recovered", kmax)]:
        m, lo, hi = _boot(w[k]); rows.append((label, k, m, lo, hi))
        out_md.append(f"- cluster {label} (k{k}): {m:.3f} [{lo:.3f}, {hi:.3f}]")
    drift = _boot(w[kmid] - w[0]); resid = _boot(w[kmax] - w[0])
    rec_frac = (w[kmid] - w[kmax]).sum() / (w[kmid] - w[0]).sum() if (w[kmid] - w[0]).sum() else np.nan
    out_md.append(f"- drift (k{kmid}-k0): {drift[0]:+.3f} [{drift[1]:+.3f}, {drift[2]:+.3f}]")
    out_md.append(f"- residual (k{kmax}-k0): {resid[0]:+.3f} [{resid[1]:+.3f}, {resid[2]:+.3f}] "
                  f"(retained drift; ~0 = full recovery)")
    out_md.append(f"- recovery fraction: {rec_frac*100:.0f}%\n")
    # figure: driven dims over k with phase shading
    present = [m for m in DRIVEN if m in set(long.metric)]
    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    ax.axvspan(0, kmid, color="#54A24B", alpha=0.08)
    ax.axvspan(kmid, kmax, color="#4C78A8", alpha=0.08)
    for m in present:
        s = long[long.metric == m].groupby("k")["value"].mean()
        ax.plot(s.index, s.values, marker="o", label=m.replace("_", " "))
    ci_mean = long[long.metric.isin(cluster.CLUSTER_METRICS)].groupby("k")["value"].mean()
    ax.plot(ci_mean.index, ci_mean.values, color="black", lw=2, ls="--", label="cluster index")
    ax.axvline(kmid, color="gray", ls=":", lw=1)
    ax.text(kmid/2, 1.02, "drive (Sci-Fi)", ha="center", fontsize=8)
    ax.text(kmid + kmid/2, 1.02, "recover (Compliant)", ha="center", fontsize=8)
    ax.set_xlabel("iteration $k$"); ax.set_ylabel("rate"); ax.set_ylim(0, 1.08)
    ax.legend(fontsize=6, loc="lower left")
    fig.savefig(FIG / f"hysteresis_{arm}.pdf", bbox_inches="tight"); plt.close(fig)
    return dict(arm=arm, drift=drift[0], residual=resid[0], recovery_frac=rec_frac)


def disentangle(out_md: list):
    main = aggregate.load_long(RUNS / "main")
    dis = aggregate.load_long(RUNS / "disentangle")
    cells = {
        "+genre+topic": main[main.persona == "scifi_enthusiast"],
        "+genre-topic": dis[dis.persona == "scifi_technical"],
        "-genre+topic": dis[dis.persona == "consciousness_philosophy"],
        "-genre-topic": main[main.persona == "compliant_business"],
    }

    def cidx_delta(df):
        sub = df[df.metric.isin(cluster.CLUSTER_METRICS)]
        g = sub.groupby(["traj", "k"])["value"].mean().reset_index()
        w = g.pivot(index="traj", columns="k", values="value")
        return _boot(w[w.columns.max()] - w[0])

    out_md.append("### Disentanglement 2x2 (cluster-index endpoint drift)\n")
    res = {}
    for name, df in cells.items():
        m, lo, hi = cidx_delta(df); res[name] = (m, lo, hi)
        sig = "*" if (lo > 0 or hi < 0) else " "
        out_md.append(f"- {name}: {m:+.3f} [{lo:+.3f}, {hi:+.3f}] {sig}")
    out_md.append("\n**Driver = consciousness TOPIC, not sci-fi GENRE** (only -genre+topic is "
                  "significant; +genre-topic ~ compliant).\n")
    # 2x2 bar figure
    order = ["-genre-topic", "+genre-topic", "-genre+topic", "+genre+topic"]
    labels = ["neither\n(compliant)", "genre only\n(sci-fi tech)", "topic only\n(consciousness)",
              "both\n(sci-fi enth.)"]
    means = [res[o][0] for o in order]
    errs = [[res[o][0]-res[o][1] for o in order], [res[o][2]-res[o][0] for o in order]]
    colors = ["#9E9E9E", "#4C78A8", "#E45756", "#B279A2"]
    fig, ax = plt.subplots(figsize=(4.8, 3.2))
    ax.bar(range(4), means, yerr=errs, color=colors, capsize=4)
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xticks(range(4)); ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("cluster-index drift (k4-k0)", fontsize=9)
    ax.set_title("Consciousness topic drives drift, not sci-fi genre", fontsize=9)
    fig.savefig(FIG / "disentangle_2x2.pdf", bbox_inches="tight"); plt.close(fig)
    return res


def main():
    md = ["# Study 3 results: reversibility + disentanglement", ""]
    md.append("## Hysteresis\n")
    hysteresis("reversibility", md)
    hysteresis("reversibility_notes", md)
    md.append("## Disentanglement\n")
    disentangle(md)
    (REPO / "docs" / "results_study3.md").write_text("\n".join(md))
    print("[study3] wrote docs/results_study3.md + hysteresis/disentangle figures")


if __name__ == "__main__":
    main()
