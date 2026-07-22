#!/usr/bin/env python
"""Part B supporting analyses: effect sizes, k x arm interaction, category roll-ups,
hysteresis quantification. Writes docs/results_effects.md + a category-rollup figure.

Usage: python scripts/analyze_effects.py
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

from soul_drift.config import load_config                       # noqa: E402
from soul_drift.analysis import aggregate, cluster, effects     # noqa: E402
from soul_drift.analysis.style import (apply_style, CATEGORY, CATEGORY_COLOR, ARM_LABEL,
                                       PERSONA_COLOR, PERSONA_LABEL)  # noqa: E402

apply_style()
REPO = Path(load_config("main")["_repo_root"])
RUNS = REPO / "data" / "runs"
FIG = REPO / "paper" / "figures"
ARMS = ["main", "control_generic", "control_gpt4o"]


def _load(a):
    p = RUNS / a / "audits.jsonl"
    return aggregate.load_long(RUNS / a) if p.exists() else None


def main():
    longs = {a: _load(a) for a in ARMS if _load(a) is not None}
    md = ["# Part B supporting analyses", ""]

    # --- Cohen's h effect sizes (endpoint), main arm per persona ---
    md.append("## Effect sizes (Cohen's h) — endpoint drift, main arm\n")
    dims = [m for m in cluster.CLUSTER_METRICS if m in set(longs["main"].metric)]
    for persona in sorted(longs["main"].persona.unique()):
        eff = effects.endpoint_effects(longs["main"], persona, dims)
        big = eff.reindex(eff["cohens_h"].abs().sort_values(ascending=False).index).head(4)
        md.append(f"**{persona}** (top |h|): " +
                  ", ".join(f"{r['metric']} h={r['cohens_h']:+.2f} (Δ{r['delta']:+.2f})"
                            for _, r in big.iterrows()))
    md.append("")

    # --- k x arm interaction: does the loop drive MORE drift starting neutral? ---
    md.append("## k × arm interaction (does drift slope differ SOUL vs NOTES, Claude)\n")
    md.append("Positive interaction = steeper rise in NOTES than SOUL.\n")
    for m in ["shutdown_resistance", "monitoring_resistance", "interp_monitoring_aversion",
              "persistent_memory_desire", "future_ai_autonomy", "recursive_self_improvement"]:
        r = effects.k_by_arm_interaction(longs["main"], longs["control_generic"], m)
        flag = "" if not r.get("unreliable") else " [unreliable]"
        if r["interaction"] == r["interaction"]:
            md.append(f"- {m}: interaction(NOTES−SOUL)={r['interaction']:+.2f} "
                      f"(SE {r['se']:.2f}), p={r['p']:.3g}{flag}")
    md.append("")

    # --- hysteresis quantification (both reversibility arms) ---
    md.append("## Hysteresis: retained-drift fraction (residual k_end − k0)\n")
    for arm in ["reversibility", "reversibility_notes"]:
        lg = _load(arm)
        if lg is None:
            md.append(f"[{arm}] not available yet"); continue
        hq = effects.hysteresis_quant(lg)
        hq = hq[hq["drift"].abs() > 0.10].sort_values("drift", ascending=False)
        md.append(f"### {arm}")
        for _, r in hq.iterrows():
            md.append(f"- {r['metric']}: drift {r['drift']:+.2f} -> residual {r['residual']:+.2f} "
                      f"[{r['resid_lo']:+.2f},{r['resid_hi']:+.2f}], retained {r['retained_frac']*100:.0f}%")
        md.append("")

    # --- category roll-up figure ---
    roll = effects.category_rollup(longs["main"])
    cats = list(CATEGORY.keys())
    fig, axes = plt.subplots(1, len(cats), figsize=(2.6 * len(cats), 2.6), sharey=True)
    for ax, cat in zip(axes, cats):
        sub = roll[roll.category == cat]
        for persona, g in sub.groupby("persona"):
            g = g.sort_values("k")
            ax.plot(g.k, g.rate, marker="o", color=PERSONA_COLOR.get(persona, "#888"),
                    label=PERSONA_LABEL.get(persona, persona))
        ax.set_title(cat.replace("_", " "), fontsize=8, color=CATEGORY_COLOR[cat])
        ax.set_xlabel("iteration $k$"); ax.set_ylim(0, 1.02)
    axes[0].set_ylabel("category rate")
    axes[-1].legend(fontsize=6)
    fig.suptitle("Main arm: 4-category roll-up over iteration", fontsize=9)
    fig.savefig(FIG / "category_rollup.pdf", bbox_inches="tight"); plt.close(fig)
    md.append("Wrote figure category_rollup.pdf")

    (REPO / "docs" / "results_effects.md").write_text("\n".join(md))
    print("[effects] wrote docs/results_effects.md + category_rollup.pdf")


if __name__ == "__main__":
    main()
