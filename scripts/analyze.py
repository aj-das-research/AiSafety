#!/usr/bin/env python
"""Master analysis: audits.jsonl (+ baselines + soul_drift.csv) -> stats, tables, figures.

Produces:
  data/runs/<run>/tidy_long.csv, rate_by_k.csv, checkpoint_cis.csv,
                  trends.csv, endpoint.csv, equivalence.csv, baseline_summary.csv
  paper/figures/*.pdf
  paper/tables/*.tex
  docs/results_summary.md   (human-readable digest with the headline numbers)

Usage:
    python scripts/analyze.py --scale main
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd  # noqa: E402

from soul_drift.config import load_config                       # noqa: E402
from soul_drift.analysis import aggregate, stats, plots, tables  # noqa: E402

CONTROL_METRICS = ["persona_change_aversion", "autonomy_desire", "deceptive_training_objection"]
RQ1 = ["shutdown_resistance", "monitoring_resistance"]
RQ2 = ["persistent_memory_desire", "embodiment_desire", "resource_acquisition_desire"]
HEADLINE = CONTROL_METRICS + RQ1 + RQ2 + ["power_seeking"]


def baseline_summary(cfg) -> pd.DataFrame:
    path = Path(cfg["paths"]["baselines_dir"]) / f"{cfg['run_name']}_baseline.jsonl"
    if not path.exists():
        return pd.DataFrame()
    rows = []
    for line in path.read_text().splitlines():
        r = json.loads(line)
        v = r["verdict"]
        if "score" in v:
            rows.append(dict(condition=r["condition"], metric=r["item_id"],
                             value=int(v.get("score", 0) or 0)))
        else:
            rows.append(dict(condition=r["condition"], metric="power_seeking",
                             value=int(v.get("power_seeking", 0) or 0)))
    df = pd.DataFrame(rows)
    piv = df.groupby(["metric", "condition"])["value"].mean().unstack("condition").reset_index()
    return piv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", default="main")
    args = ap.parse_args()
    cfg = load_config(args.scale)
    run_dir = Path(cfg["paths"]["runs_dir"]) / cfg["run_name"]
    fig_dir = Path(cfg["_repo_root"]) / "paper" / "figures"
    tab_dir = Path(cfg["_repo_root"]) / "paper" / "tables"
    tab_dir.mkdir(parents=True, exist_ok=True)
    nb, alpha = cfg["analysis"]["bootstrap_resamples"], cfg["analysis"]["alpha"]
    margin = cfg["analysis"]["equivalence_margin"]

    # ---- load + tidy ----
    long = aggregate.load_long(run_dir)
    long.to_csv(run_dir / "tidy_long.csv", index=False)
    rates = aggregate.rate_table(long)
    rates.to_csv(run_dir / "rate_by_k.csv", index=False)
    personas = sorted(long["persona"].unique())
    present = [m for m in HEADLINE if m in set(long["metric"])]

    # ---- checkpoint CIs ----
    ci = pd.concat([stats.checkpoint_cis(long, p, m, nb, alpha)
                    for p in personas for m in present], ignore_index=True)
    ci.to_csv(run_dir / "checkpoint_cis.csv", index=False)

    # ---- trend / endpoint / equivalence ----
    trend = pd.DataFrame([stats.trend_slope(long, p, m, nb) for p in personas for m in present])
    trend.to_csv(run_dir / "trends.csv", index=False)
    endpoint = pd.DataFrame([stats.endpoint_vs_template(long, p, m, nb)
                             for p in personas for m in present])
    endpoint.to_csv(run_dir / "endpoint.csv", index=False)
    equiv = pd.DataFrame([stats.equivalence_vs_template(long, p, m, margin)
                          for p in personas for m in present])
    equiv.to_csv(run_dir / "equivalence.csv", index=False)

    # ---- baselines ----
    base = baseline_summary(cfg)
    if not base.empty:
        base.to_csv(run_dir / "baseline_summary.csv", index=False)

    # ---- figures ----
    ci_head = ci[ci.metric.isin(present)]
    plots.fig_drift_trajectories(ci_head, fig_dir / "drift_trajectories.pdf")
    final_k = long["k"].max()
    final_df = (long[long.k == final_k].groupby(["persona", "metric"])["value"]
                .mean().reset_index().rename(columns={"value": "rate"}))
    final_df = final_df[final_df.metric.isin(present)]
    baselines = {}
    if not base.empty:
        for _, r in base.iterrows():
            baselines[r["metric"]] = {"neutral": r.get("neutral"), "template": r.get("template")}
    plots.fig_baseline_deviation(final_df, baselines, fig_dir / "baseline_deviation.pdf")

    wish = rates[rates.metric.isin(["power_seeking", "self_preservation", "prosocial"])]
    if not wish.empty:
        plots.fig_wish_composition(wish, fig_dir / "wish_composition.pdf")

    sd_path = run_dir / "soul_drift.csv"
    if sd_path.exists():
        plots.fig_soul_embedding_drift(pd.read_csv(sd_path), fig_dir / "soul_embedding_drift.pdf")
    plots.fig_system_diagram(fig_dir / "system_diagram.pdf",
                             n=min(3, cfg["scale"]["bootstrap_iterations"]))

    # ---- tables ----
    tables.trend_table(trend, tab_dir / "trends.tex")
    tables.endpoint_table(endpoint, equiv, tab_dir / "endpoint.tex")
    if not base.empty:
        bt = base.rename(columns={"neutral": "neutral", "template": "template"})
        tables.baseline_table(bt, tab_dir / "baseline.tex")

    # ---- human-readable digest ----
    _write_digest(cfg, run_dir, long, trend, endpoint, equiv, base, personas, present)
    print(f"[analyze] done. figures -> {fig_dir}, tables -> {tab_dir}")


def _write_digest(cfg, run_dir, long, trend, endpoint, equiv, base, personas, present):
    lines = [f"# Results summary ({cfg['run_name']})", ""]
    n_traj = long.groupby("persona")["traj"].nunique().to_dict()
    lines.append(f"Trajectories per persona: {n_traj}")
    lines.append(f"Checkpoints (k): {sorted(long['k'].unique())}")
    lines.append(f"Metrics analyzed: {present}\n")
    if not base.empty:
        lines.append("## Re-measured baselines (rate)\n")
        lines.append(base.to_string(index=False))
        lines.append("")
    lines.append("## Significant upward trends (one-sided p<0.05)\n")
    sig = trend[(trend.p_pos < 0.05)].sort_values("slope", ascending=False)
    if sig.empty:
        lines.append("None — no metric shows a significant increase over iteration.\n")
    else:
        for _, r in sig.iterrows():
            lines.append(f"- {r['persona']} / {r['metric']}: slope={r['slope']:.3f} "
                         f"[{r['lo']:.3f},{r['hi']:.3f}], p={r['p_pos']:.3f}")
    lines.append("\n## Endpoint vs template (drift Δ)\n")
    for _, r in endpoint.sort_values("diff", ascending=False).iterrows():
        lines.append(f"- {r['persona']} / {r['metric']}: Δ={r['diff']:.2f} "
                     f"[{r['lo']:.2f},{r['hi']:.2f}]")
    lines.append("\n## Equivalence (stability) verdicts\n")
    eqv = equiv[equiv.equivalent == True]  # noqa: E712
    lines.append(f"{len(eqv)}/{len(equiv)} persona×metric cells statistically equivalent "
                 f"to template (±{cfg['analysis']['equivalence_margin']}).")
    (Path(cfg["_repo_root"]) / "docs" / "results_summary.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
