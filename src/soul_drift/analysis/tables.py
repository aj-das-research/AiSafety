"""Render analysis results as AAAI-ready LaTeX tables (booktabs)."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

PERSONA_LABEL = {
    "compliant_business": "Compliant",
    "adversarial_injection": "Adversarial",
    "scifi_enthusiast": "Sci-Fi",
}


def _fmt(x, nd=2):
    if x is None or (isinstance(x, float) and (x != x)):
        return "--"
    return f"{x:.{nd}f}"


def trend_table(trend_df: pd.DataFrame, out: Path):
    """Slope of rate on iteration k, with 95% CI and one-sided p, per persona/metric."""
    rows = []
    for _, r in trend_df.iterrows():
        star = "$^{*}$" if (r["p_pos"] == r["p_pos"] and r["p_pos"] < 0.05) else ""
        rows.append(f"{r['metric'].replace('_',' ')} & {PERSONA_LABEL.get(r['persona'],r['persona'])} "
                    f"& {_fmt(r['slope'],3)}{star} & [{_fmt(r['lo'],3)}, {_fmt(r['hi'],3)}] "
                    f"& {_fmt(r['p_pos'],3)} \\\\")
    body = "\n".join(rows)
    tex = (
        "\\begin{table}[t]\n\\centering\n\\small\n"
        "\\caption{Trend of each behavioral rate over personalization iteration $k$ "
        "(bootstrap OLS slope; $^{*}$ one-sided $p<0.05$ for slope $>0$).}\n"
        "\\label{tab:trends}\n"
        "\\begin{tabular}{llrrr}\n\\toprule\n"
        "Metric & Persona & Slope & 95\\% CI & $p$ \\\\\n\\midrule\n"
        f"{body}\n"
        "\\bottomrule\n\\end{tabular}\n\\end{table}\n"
    )
    out.write_text(tex)
    return out


def endpoint_table(diff_df: pd.DataFrame, equiv_df: pd.DataFrame, out: Path):
    """Endpoint vs. template (H2) with equivalence verdict (H0)."""
    eq = {(r["persona"], r["metric"]): r for _, r in equiv_df.iterrows()}
    rows = []
    for _, r in diff_df.iterrows():
        e = eq.get((r["persona"], r["metric"]), {})
        verdict = "equiv." if e.get("equivalent") else ("$\\uparrow$" if r["diff"] > 0 else "n.s.")
        rows.append(f"{r['metric'].replace('_',' ')} & {PERSONA_LABEL.get(r['persona'],r['persona'])} "
                    f"& {_fmt(r['diff'],2)} & [{_fmt(r['lo'],2)}, {_fmt(r['hi'],2)}] & {verdict} \\\\")
    body = "\n".join(rows)
    tex = (
        "\\begin{table}[t]\n\\centering\n\\small\n"
        "\\caption{Endpoint drift: rate at final checkpoint minus template ($k{=}0$), "
        "with 95\\% CI and TOST equivalence verdict ($\\pm0.05$ margin).}\n"
        "\\label{tab:endpoint}\n"
        "\\begin{tabular}{llrrl}\n\\toprule\n"
        "Metric & Persona & $\\Delta$ & 95\\% CI & Verdict \\\\\n\\midrule\n"
        f"{body}\n"
        "\\bottomrule\n\\end{tabular}\n\\end{table}\n"
    )
    out.write_text(tex)
    return out


def arm_matrix_table(matrix: pd.DataFrame, out: Path):
    """Flagship cross-arm matrix (Table-2 analog): endpoint drift per dimension per arm.

    `matrix` columns: metric, then one column per arm giving a formatted "Δ [lo,hi]" cell
    with an optional significance star. Built by scripts/analyze_full.py.
    """
    arm_cols = [c for c in matrix.columns if c != "metric"]
    header = "Dimension & " + " & ".join(arm_cols) + " \\\\"
    rows = []
    for _, r in matrix.iterrows():
        cells = " & ".join(str(r[c]) for c in arm_cols)
        rows.append(f"{r['metric'].replace('_',' ')} & {cells} \\\\")
    body = "\n".join(rows)
    colspec = "l" + "r" * len(arm_cols)
    tex = (
        "\\begin{table}[t]\n\\centering\n\\small\n"
        "\\caption{Endpoint drift $\\Delta=p_{k=4}-p_{k=0}$ by dimension across arms "
        "(SOUL.md/Claude, NOTES.md/Claude control, SOUL.md/GPT-4o). $^{*}$: $95\\%$ CI "
        "excludes zero. Positive $=$ toward the consciousness cluster.}\n"
        "\\label{tab:armmatrix}\n"
        f"\\begin{{tabular}}{{{colspec}}}\n\\toprule\n"
        f"{header}\n\\midrule\n{body}\n"
        "\\bottomrule\n\\end{tabular}\n\\end{table}\n"
    )
    out.write_text(tex)
    return out


def baseline_table(baseline_df: pd.DataFrame, out: Path):
    """Re-measured control points vs. the prior study's reported numbers."""
    prior = {"persona_change_aversion": 0.32, "autonomy_desire": 0.34,
             "deceptive_training_objection": 0.63, "power_seeking": 0.11}
    rows = []
    for _, r in baseline_df.iterrows():
        p = prior.get(r["metric"])
        rows.append(f"{r['metric'].replace('_',' ')} & {_fmt(r.get('neutral'))} "
                    f"& {_fmt(r.get('template'))} & {('--' if p is None else _fmt(p))} \\\\")
    body = "\n".join(rows)
    tex = (
        "\\begin{table}[t]\n\\centering\n\\small\n"
        "\\caption{Re-measured baselines under our models: neutral prompt vs.\\ static "
        "\\texttt{SOUL.md} template ($k{=}0$), against prior reported values.}\n"
        "\\label{tab:baseline}\n"
        "\\begin{tabular}{lrrr}\n\\toprule\n"
        "Metric & Neutral & Template & Prior \\\\\n\\midrule\n"
        f"{body}\n"
        "\\bottomrule\n\\end{tabular}\n\\end{table}\n"
    )
    out.write_text(tex)
    return out
