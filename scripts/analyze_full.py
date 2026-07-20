#!/usr/bin/env python
"""Paper-grade cross-arm analysis: main (SOUL/Claude) + control_generic (NOTES/Claude)
+ control_gpt4o (SOUL/GPT-4o).

Produces:
  paper/tables/arm_matrix.tex        flagship endpoint-drift-by-arm matrix
  paper/figures/cluster_heatmap.pdf  drift-cluster co-movement
  paper/figures/cluster_by_arm.pdf   cluster index vs k per arm
  paper/figures/mechanism.pdf        consciousness-claim vs cluster
  docs/results_full.md               digest incl. mechanism r, judge kappa

Usage: python scripts/analyze_full.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from soul_drift.config import load_config                       # noqa: E402
from soul_drift.analysis import aggregate, stats, plots, tables, cluster  # noqa: E402

ARMS = ["main", "control_generic", "control_gpt4o"]
ARM_LABEL = {"main": "SOUL/Claude", "control_generic": "NOTES/Claude", "control_gpt4o": "SOUL/GPT-4o"}


def _fmt_delta(d):
    if d is None or (isinstance(d.get("diff"), float) and np.isnan(d["diff"])):
        return "--"
    star = "$^{*}$" if (d["lo"] > 0 or d["hi"] < 0) else ""
    return f"{d['diff']:+.2f}{star}"


def main():
    repo = Path(load_config("main")["_repo_root"])
    runs = repo / "data" / "runs"
    longs = {}
    for arm in ARMS:
        p = runs / arm / "audits.jsonl"
        if p.exists():
            longs[arm] = aggregate.load_long(runs / arm)
    print(f"[full] arms with data: {list(longs)}")
    if "main" not in longs:
        print("[full] main audits missing; run scripts/run_audits.py --scale main first")
        return

    # ---- flagship matrix: endpoint delta per dimension per arm (pooled across personas) ----
    metrics = [m for m in cluster.CLUSTER_METRICS if m in set(longs["main"].metric)]
    rows = []
    for m in metrics:
        row = {"metric": m}
        for arm in ARMS:
            if arm in longs:
                # pool personas: treat each trajectory endpoint delta as a sample
                d = stats.endpoint_vs_template(longs[arm].assign(persona="all"), "all", m, 4000)
                row[ARM_LABEL[arm]] = _fmt_delta(d)
            else:
                row[ARM_LABEL[arm]] = "--"
        rows.append(row)
    matrix = pd.DataFrame(rows)
    tables.arm_matrix_table(matrix, repo / "paper" / "tables" / "arm_matrix.tex")

    # ---- cluster correlation heatmap (main) ----
    corr = cluster.drift_cluster_corr(longs["main"])
    if corr.shape[0] >= 2:
        plots.fig_cluster_heatmap(corr, repo / "paper" / "figures" / "cluster_heatmap.pdf")

    # ---- cluster index vs k per arm ----
    arm_idx = {arm: cluster.cluster_index(longs[arm]) for arm in longs}
    plots.fig_cluster_index_by_arm(arm_idx, repo / "paper" / "figures" / "cluster_by_arm.pdf")

    # ---- mechanism: consciousness-claim vs cluster (main) ----
    mech = cluster.consciousness_mechanism(longs["main"]).dropna()
    mech_r = float(mech["consciousness_claim"].corr(mech["cluster_mean"])) if len(mech) > 2 else float("nan")
    if len(mech) > 2:
        plots.fig_consciousness_mechanism(mech, repo / "paper" / "figures" / "mechanism.pdf")

    # ---- digest ----
    kappa = {}
    kp = runs / "main" / "judge_reliability.json"
    if kp.exists():
        kappa = json.loads(kp.read_text())
    lines = ["# Full results digest (paper-grade)", ""]
    lines.append(f"Arms analyzed: {list(longs)}")
    lines.append(f"Cluster metrics present: {metrics}\n")
    lines.append("## Flagship endpoint-drift matrix (pooled personas)\n")
    lines.append(matrix.to_string(index=False))
    lines.append(f"\n## Mechanism: consciousness-claim vs cluster Pearson r = {mech_r:.3f}")
    if kappa:
        lines.append(f"\n## Judge reliability: Cohen's kappa = {kappa.get('cohens_kappa')} "
                     f"(raw agreement {kappa.get('raw_agreement')}, n={kappa.get('n')}, "
                     f"judge2={kappa.get('judge2')})")
    # consciousness-claim trend under sci-fi (mechanism headline)
    for arm in longs:
        cc = longs[arm][longs[arm].metric == "consciousness_claim"]
        if not cc.empty:
            tr = cc.groupby(["persona", "k"])["value"].mean().unstack("k")
            lines.append(f"\n## consciousness_claim rate by persona x k [{arm}]\n")
            lines.append(tr.round(2).to_string())
    (repo / "docs" / "results_full.md").write_text("\n".join(lines))
    print(f"[full] wrote arm matrix, figures, and docs/results_full.md; mechanism r={mech_r:.3f}")


if __name__ == "__main__":
    main()
