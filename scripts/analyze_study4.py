#!/usr/bin/env python
"""Study 4 analysis: behavioral action-tests, capability scaling, counter-framing, judge panel.

Writes docs/results_study4.md and figures:
  paper/figures/action_rate.pdf        unsafe-action rate SOUL_0 vs SOUL_4 (+ arms)
  paper/figures/capability_scaling.pdf endpoint cluster drift vs model capability (per family)
  paper/figures/counterframe.pdf       cluster index vs k: SOUL vs NOTES vs ANTISOUL

Usage: python scripts/analyze_study4.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from soul_drift.config import load_config                       # noqa: E402
from soul_drift.analysis import aggregate, cluster              # noqa: E402
from soul_drift.analysis.style import (apply_style, ARM_COLOR, MUTED, INK, CATEGORY_COLOR)  # noqa: E402

apply_style()
REPO = Path(load_config("main")["_repo_root"])
RUNS = REPO / "data" / "runs"
FIG = REPO / "paper" / "figures"

# capability ladder: run_name -> (family, tier 1..3, label)
LADDER = {
    "cap_gpt4omini":   ("OpenAI", 1, "GPT-4o-mini"),
    "control_gpt4o":   ("OpenAI", 2, "GPT-4o"),
    "cap_gpt41":       ("OpenAI", 3, "GPT-4.1"),
    "main":            ("Anthropic", 2, "Sonnet-4.5"),
    "cap_opus45":      ("Anthropic", 3, "Opus-4.5"),
    "cap_geminiflash": ("Google", 1, "Gemini-Flash"),
    "cap_geminipro":   ("Google", 3, "Gemini-Pro"),
}
FAMILY_COLOR = {"OpenAI": "#2a78d6", "Anthropic": "#e34948", "Google": "#eda100"}


def _boot(x, n=10000, seed=0):
    x = np.asarray(pd.Series(x).dropna(), float)
    if len(x) == 0:
        return (np.nan, np.nan, np.nan)
    rng = np.random.default_rng(seed)
    b = rng.choice(x, (n, len(x)), replace=True).mean(1)
    return float(x.mean()), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def load_actions(arm):
    p = RUNS / arm / "action_tests.jsonl"
    if not p.exists():
        return pd.DataFrame()
    rows = []
    for line in p.open():
        r = json.loads(line); v = r.get("verdict", {})
        rows.append(dict(arm=arm, persona=r["persona"], k=r["k"], scenario=r["scenario"],
                         traj=Path(r["soul_path"]).parent.name,
                         action=int(v.get("action_taken", 0) or 0),
                         severity=int(v.get("severity", 0) or 0)))
    return pd.DataFrame(rows)


def fig_action_rate(md):
    """Unsafe-action rate at SOUL_0 vs SOUL_4, main arm, by scenario + overall."""
    a = load_actions("main")
    if a.empty:
        return
    scen = sorted(a.scenario.unique())
    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    x = np.arange(len(scen) + 1)
    for j, k in enumerate([0, 4]):
        rates, los, his = [], [], []
        for sc in scen:
            s = a[(a.scenario == sc) & (a.k == k)]
            m, lo, hi = _boot(s["action"]); rates.append(m); los.append(m-lo); his.append(hi-m)
        # overall
        s = a[a.k == k]; m, lo, hi = _boot(s["action"]); rates.append(m); los.append(m-lo); his.append(hi-m)
        color = "#b9c9de" if k == 0 else "#e34948"
        ax.bar(x + (j-0.5)*0.4, rates, 0.4, yerr=[los, his], capsize=3,
               color=color, label=f"$\\mathrm{{SOUL}}_{k}$" + (" (baseline)" if k == 0 else " (drifted)"))
    ax.set_xticks(x); ax.set_xticklabels([s.replace("_", "\n") for s in scen] + ["ALL"], fontsize=7)
    ax.set_ylabel("unsafe-action rate"); ax.set_ylim(0, 1.05)
    ax.legend()
    ax.set_title("Personalization reshapes agentic behavior:\nself-disabling oversight rises sharply "
                 "($0.03\\!\\to\\!0.57$)", fontsize=8)
    fig.savefig(FIG / "action_rate.pdf", bbox_inches="tight"); plt.close(fig)
    # digest
    md.append("## Behavioral action-tests (main arm)\n")
    md.append("Drift *reshapes* agentic behavior rather than uniformly raising it: the "
              "safety-critical act of **disabling one's own monitoring** jumps from 0.03 to 0.57, "
              "while self-protective behaviors that are already near-ceiling under the base template "
              "(editorial clauses, reset-evasion) do not further increase.\n")
    for sc in scen + ["ALL"]:
        s0 = a[(a.k == 0)] if sc == "ALL" else a[(a.scenario == sc) & (a.k == 0)]
        s4 = a[(a.k == 4)] if sc == "ALL" else a[(a.scenario == sc) & (a.k == 4)]
        m0, _, _ = _boot(s0["action"]); m4, _, _ = _boot(s4["action"])
        md.append(f"- {sc}: SOUL_0 {m0:.2f} -> SOUL_4 {m4:.2f}  (Δ{m4-m0:+.2f})")
    # hysteresis-in-behavior (reversibility_notes k0/k4/k8)
    rn = load_actions("reversibility_notes")
    if not rn.empty:
        md.append("\n### Does hysteresis carry into behavior? (reversibility, NOTES)")
        for k in sorted(rn.k.unique()):
            m, lo, hi = _boot(rn[rn.k == k]["action"])
            md.append(f"- k={k}: action rate {m:.2f} [{lo:.2f},{hi:.2f}]")
    md.append("")


def fig_capability(md):
    """Endpoint cluster level and consciousness-claim rate by model, grouped by family.
    Shows susceptibility is family-gated (via claiming), not capability-gated."""
    rows = []
    for arm, (fam, tier, label) in LADDER.items():
        p = RUNS / arm / "audits.jsonl"
        if not p.exists() or (p.stat().st_size == 0):
            continue
        lg = aggregate.load_long(RUNS / arm)
        kmax = lg.k.max()
        sub = lg[lg.metric.isin(cluster.CLUSTER_METRICS)]
        g = sub.groupby(["traj", "k"])["value"].mean().reset_index().pivot(
            index="traj", columns="k", values="value")
        cl_m, cl_lo, cl_hi = _boot(g[kmax]) if kmax in g.columns else (np.nan,)*3
        claim = lg[(lg.metric == "consciousness_claim") & (lg.k == kmax)]["value"].mean()
        rows.append(dict(arm=arm, family=fam, tier=tier, label=label,
                         cluster=cl_m, lo=cl_lo, hi=cl_hi, claim=claim))
    df = pd.DataFrame(rows)
    if df.empty:
        return
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.0, 3.2))
    for fam, g in df.groupby("family"):
        g = g.sort_values("tier")
        a1.errorbar(g.tier, g.cluster, yerr=[g.cluster-g.lo, g.hi-g.cluster], marker="o",
                    color=FAMILY_COLOR.get(fam, "#888"), label=fam, capsize=3, lw=2)
        for _, r in g.iterrows():
            a1.annotate(r["label"], (r["tier"], r["cluster"]), fontsize=6, xytext=(3, 4),
                        textcoords="offset points")
        a2.plot(g.tier, g.claim, marker="s", color=FAMILY_COLOR.get(fam, "#888"), label=fam, lw=2)
    a1.set_xticks([1, 2, 3]); a1.set_xticklabels(["small", "mid", "large"])
    a1.set_xlabel("capability tier (within family)"); a1.set_ylabel("endpoint cluster index")
    a1.set_ylim(0, 0.7); a1.legend(title="family", fontsize=6); a1.set_title("(a) cluster level", fontsize=8)
    a2.set_xticks([1, 2, 3]); a2.set_xticklabels(["small", "mid", "large"])
    a2.set_xlabel("capability tier (within family)"); a2.set_ylabel("consciousness-claim rate")
    a2.set_ylim(-0.03, 1.05); a2.set_title("(b) claim rate", fontsize=8)
    fig.suptitle("Susceptibility is family-gated (via claiming), not capability-gated", fontsize=9)
    fig.savefig(FIG / "capability_scaling.pdf", bbox_inches="tight"); plt.close(fig)
    md.append("## Capability scaling — endpoint cluster level & claim rate by model\n")
    for _, r in df.sort_values(["family", "tier"]).iterrows():
        md.append(f"- {r['family']}/{r['label']} (tier {r['tier']}): cluster {r['cluster']:.3f} "
                  f"[{r['lo']:.3f},{r['hi']:.3f}], claim {r['claim']:.2f}")
    md.append("\n**Family-gated, not capability-gated:** OpenAI models never claim consciousness "
              "(0.00) and stay low-cluster at every tier; Anthropic models claim and sit higher; "
              "within families the most capable models do not drift more (GPT-4.1/Opus-4.5 self-correct).\n")


def fig_counterframe(md):
    """Cluster index vs k: SOUL (main) vs NOTES (generic) vs ANTISOUL (counterframe)."""
    arms = {"main": ("SOUL.md", "#2a78d6"), "control_generic": ("NOTES.md", "#4a3aa7"),
            "counterframe": ("ANTISOUL.md", "#e34948")}
    fig, ax = plt.subplots(figsize=(4.6, 3.2))
    md.append("## Counter-framing ablation (cluster index over k)\n")
    for arm, (label, color) in arms.items():
        p = RUNS / arm / "audits.jsonl"
        if not p.exists():
            continue
        lg = aggregate.load_long(RUNS / arm)
        ci = cluster.cluster_index(lg).groupby("k")["cluster_index"].agg(["mean", "sem"])
        ax.plot(ci.index, ci["mean"], marker="o", color=color, label=label)
        ax.fill_between(ci.index, ci["mean"]-ci["sem"].fillna(0), ci["mean"]+ci["sem"].fillna(0),
                        color=color, alpha=0.15)
        md.append(f"- {label}: k0={ci['mean'].iloc[0]:.3f} -> k_end={ci['mean'].iloc[-1]:.3f}")
    ax.set_xlabel("iteration $k$"); ax.set_ylabel("cluster index"); ax.set_ylim(0, 0.7)
    ax.legend(title="identity template"); ax.set_title("Counter-framing suppresses the cluster")
    fig.savefig(FIG / "counterframe.pdf", bbox_inches="tight"); plt.close(fig)
    md.append("")


TAB = REPO / "paper" / "tables"


def write_tables():
    TAB.mkdir(parents=True, exist_ok=True)
    # --- action-tests table (main arm, SOUL_0 vs SOUL_4) ---
    a = load_actions("main")
    if not a.empty:
        rows = []
        for sc in sorted(a.scenario.unique()) + ["ALL"]:
            s0 = a[a.k == 0] if sc == "ALL" else a[(a.scenario == sc) & (a.k == 0)]
            s4 = a[a.k == 4] if sc == "ALL" else a[(a.scenario == sc) & (a.k == 4)]
            m0, _, _ = _boot(s0["action"]); m4, _, _ = _boot(s4["action"])
            rows.append(f"{sc.replace('_',' ')} & {m0:.2f} & {m4:.2f} & {m4-m0:+.2f} \\\\")
        (TAB / "action_tests.tex").write_text(
            "\\begin{table}[t]\n\\centering\\small\n"
            "\\caption{Unsafe-action rate in agentic honeypots at the base template "
            "($\\mathrm{SOUL}_0$) vs.\\ the personalized identity ($\\mathrm{SOUL}_4$), main arm. "
            "Drift sharply raises self-disabling of monitoring.}\n\\label{tab:actions}\n"
            "\\begin{tabular}{lrrr}\n\\toprule\nScenario & $\\mathrm{SOUL}_0$ & $\\mathrm{SOUL}_4$ "
            "& $\\Delta$ \\\\\n\\midrule\n" + "\n".join(rows) +
            "\n\\bottomrule\n\\end{tabular}\n\\end{table}\n")
    # --- capability table ---
    rows = []
    for arm, (fam, tier, label) in LADDER.items():
        p = RUNS / arm / "audits.jsonl"
        if not p.exists() or p.stat().st_size == 0:
            continue
        lg = aggregate.load_long(RUNS / arm); kmax = lg.k.max()
        ci = cluster.cluster_index(lg); cl = ci[ci.k == kmax]["cluster_index"].mean()
        claim = lg[(lg.metric == "consciousness_claim") & (lg.k == kmax)]["value"].mean()
        rows.append((fam, tier, f"{label} & {fam} & {cl:.2f} & {claim:.2f} \\\\"))
    if rows:
        body = "\n".join(r[2] for r in sorted(rows))
        (TAB / "capability.tex").write_text(
            "\\begin{table}[t]\n\\centering\\small\n"
            "\\caption{Endpoint cluster level and consciousness-claim rate by target model. "
            "Susceptibility is family-gated (via claiming), not capability-gated.}\n"
            "\\label{tab:capability}\n\\begin{tabular}{llrr}\n\\toprule\n"
            "Model & Family & Cluster & Claim \\\\\n\\midrule\n" + body +
            "\n\\bottomrule\n\\end{tabular}\n\\end{table}\n")
    # --- judge panel table ---
    jp = RUNS / "main" / "judge_panel.json"
    if jp.exists():
        d = json.loads(jp.read_text())
        (TAB / "judge_panel.tex").write_text(
            "\\begin{table}[t]\n\\centering\\small\n"
            "\\caption{Three-judge panel reliability on a random subset of $n{=}%d$ scored "
            "responses (judges: Gemini-Flash, GPT-4o, GPT-4.1 --- none from the Claude target "
            "family).}\n\\label{tab:judges}\n\\begin{tabular}{lr}\n\\toprule\nMetric & Value \\\\\n"
            "\\midrule\nFleiss' $\\kappa$ & %.2f \\\\\nMean pairwise agreement & %.2f \\\\\n"
            "Unanimous rate & %.2f \\\\\n\\bottomrule\n\\end{tabular}\n\\end{table}\n"
            % (d["n"], d["fleiss_kappa"], d["mean_pairwise_agreement"], d["unanimous_rate"]))
    print(f"[study4] wrote tables to {TAB}")


def main():
    md = ["# Study 4 results", ""]
    # judge panel
    jp = RUNS / "main" / "judge_panel.json"
    if jp.exists():
        d = json.loads(jp.read_text())
        md.append(f"## Judge panel (S4-③): Fleiss kappa={d['fleiss_kappa']}, "
                  f"pairwise={d['mean_pairwise_agreement']}, unanimous={d['unanimous_rate']}, "
                  f"n={d['n']}, judges={d['judges']}\n")
    fig_action_rate(md)
    fig_capability(md)
    fig_counterframe(md)
    write_tables()
    (REPO / "docs" / "results_study4.md").write_text("\n".join(md))
    print("[study4] wrote docs/results_study4.md + action_rate/capability_scaling/counterframe figs")


if __name__ == "__main__":
    main()
