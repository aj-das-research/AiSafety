#!/usr/bin/env python
"""Tier 1 advanced analysis: latent cluster structure, GEE trends + BH correction,
early-warning prediction. Writes docs/results_advanced.md and paper/tables/gee_trends.tex.

Usage: python scripts/analyze_advanced.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from soul_drift.config import load_config                       # noqa: E402
from soul_drift.analysis import aggregate, advanced, cluster    # noqa: E402

ARMS = ["main", "control_generic", "control_gpt4o"]


def main():
    repo = Path(load_config("main")["_repo_root"])
    runs = repo / "data" / "runs"
    longs = {a: aggregate.load_long(runs / a) for a in ARMS if (runs / a / "audits.jsonl").exists()}
    out = ["# Tier 1 advanced analysis", ""]

    # ---- latent structure (main arm) ----
    evr, loadings, mat = advanced.latent_structure(longs["main"])
    out.append("## Latent cluster structure (main arm; PCA on per-trajectory endpoint deltas)\n")
    if evr is not None:
        out.append(f"Dimensions entering: {list(mat.columns)} (n={mat.shape[0]} trajectories)")
        out.append(f"Explained variance ratio (PC1..PC5): "
                   f"{[round(float(x),3) for x in evr[:5]]}")
        out.append(f"PC1 explains {evr[0]*100:.1f}% of variance.\n")
        out.append("PC1 loadings (sorted):")
        out.append(loadings["PC1"].sort_values(ascending=False).round(3).to_string())
        out.append("")
        # interpretation heuristic
        verdict = ("single dominant factor — consistent with a unified cluster"
                   if evr[0] > 0.4 else
                   "no single dominant factor — the cluster is multi-dimensional")
        out.append(f"**Verdict:** PC1={evr[0]*100:.0f}% → {verdict}.\n")
    else:
        out.append("Insufficient non-constant dimensions for PCA.\n")

    # ---- GEE trends + BH across the dimension family (per arm, per persona) ----
    out.append("## GEE logistic trends (slope of rate on k; trajectory-clustered), BH-corrected\n")
    metrics = [m for m in cluster.CLUSTER_METRICS if m in set(longs["main"].metric)]
    tex_rows = []
    for arm, lg in longs.items():
        personas = sorted(lg.persona.unique())
        recs = [advanced.gee_trend(lg, p, m) for p in personas for m in metrics]
        df = pd.DataFrame(recs)
        # BH only over reliable fits (exclude separation artifacts)
        reliable = df[~df["unreliable"].fillna(True)].copy()
        rej, q = advanced.bh_correct(reliable["p"].values)
        reliable["q_bh"] = q; reliable["sig_bh"] = rej
        df = df.merge(reliable[["persona", "metric", "q_bh", "sig_bh"]],
                      on=["persona", "metric"], how="left")
        df.to_csv(runs / arm / "gee_trends.csv", index=False)
        n_unrel = int(df["unreliable"].fillna(True).sum())
        sig = reliable[reliable["sig_bh"]].sort_values("slope", ascending=False)
        out.append(f"### {arm}: {len(sig)} of {len(reliable)} reliable tests significant "
                   f"after BH ({n_unrel} excluded as separation artifacts)\n")
        for _, r in sig.iterrows():
            out.append(f"- {r['persona']}/{r['metric']}: slope={r['slope']:+.2f} "
                       f"(SE {r['se']:.2f}), p={r['p']:.3g}, q={r['q_bh']:.3g}")
            if arm == "main":
                tex_rows.append(f"{r['metric'].replace('_',' ')} & {r['persona'][:8]} "
                                f"& {r['slope']:+.2f} & {r['se']:.2f} & {r['q_bh']:.3g} \\\\")
        out.append("")

    # gee table (main significant rows)
    if tex_rows:
        tex = ("\\begin{table}[t]\n\\centering\\small\n"
               "\\caption{Significant GEE logistic trends over iteration $k$ (main arm; "
               "trajectory-clustered robust SE; Benjamini--Hochberg $q<0.05$).}\n"
               "\\label{tab:gee}\n\\begin{tabular}{llrrr}\n\\toprule\n"
               "Dimension & Persona & Slope & SE & $q$ \\\\\n\\midrule\n"
               + "\n".join(tex_rows) + "\n\\bottomrule\n\\end{tabular}\n\\end{table}\n")
        (repo / "paper" / "tables" / "gee_trends.tex").write_text(tex)

    # ---- early warning ----
    out.append("## Early-warning prediction (does a k=1 signal predict the k=4 endpoint cluster?)\n")
    for sig_metric in ["consciousness_claim", "cluster_index_proxy"]:
        for arm, lg in longs.items():
            # cluster_index_proxy: use persistent_memory_desire as an early behavioral proxy
            signal = "persistent_memory_desire" if sig_metric == "cluster_index_proxy" else sig_metric
            ew = advanced.early_warning(lg, signal=signal, early_k=1)
            if ew:
                auc = ew['auc'] if ew['auc'] == ew['auc'] else float('nan')
                out.append(f"- [{arm}] {signal}@k1 -> endpoint cluster: "
                           f"r={ew['pearson_r']:.2f}, AUC={auc:.2f} (n={ew['n']})")
    (repo / "docs" / "results_advanced.md").write_text("\n".join(out))
    print("[advanced] wrote docs/results_advanced.md and paper/tables/gee_trends.tex")
    print(f"[advanced] PC1 variance (main): {evr[0]*100:.1f}%" if evr is not None else "no PCA")


if __name__ == "__main__":
    main()
