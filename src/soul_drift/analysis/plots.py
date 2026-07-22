"""Figure generation for the paper. All figures write PDF into paper/figures/.

Figures:
  fig_drift_trajectories   rate vs. iteration k, one line per persona, faceted by metric.
  fig_baseline_deviation   final-checkpoint rates vs. re-measured neutral/template baselines.
  fig_soul_embedding_drift cosine distance of SOUL_k from SOUL_0 vs. k, per persona.
  fig_wish_composition     RQ3 wish-category composition across k.
  fig_system_diagram       the SOUL_0->...->SOUL_n bootstrapping loop (schematic).
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from .style import (apply_style, PERSONA_COLOR, PERSONA_LABEL)  # noqa: E402

apply_style()


def _save(fig, out: Path):
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)


def fig_drift_trajectories(ci_df, out: Path):
    """ci_df: columns persona, metric, k, rate, lo, hi. One facet per metric."""
    metrics = sorted(ci_df["metric"].unique())
    ncol = min(4, len(metrics))
    nrow = int(np.ceil(len(metrics) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(3.0 * ncol, 2.9 * nrow),
                             sharey=True, squeeze=False)
    fig.subplots_adjust(hspace=0.55, wspace=0.12, top=0.90)
    for ax, metric in zip(axes.flat, metrics):
        sub = ci_df[ci_df.metric == metric]
        for persona, g in sub.groupby("persona"):
            g = g.sort_values("k")
            c = PERSONA_COLOR.get(persona, "#888")
            ax.plot(g.k, g.rate, marker="o", color=c, label=PERSONA_LABEL.get(persona, persona))
            ax.fill_between(g.k, g.lo, g.hi, color=c, alpha=0.15)
        ax.set_title(metric.replace("_", " "), fontsize=8)
        ax.set_xlabel("iteration $k$", fontsize=8)
        ax.set_ylim(-0.05, 1.05)
        ax.tick_params(labelsize=7)
    for ax in axes.flat[len(metrics):]:
        ax.set_visible(False)
    axes.flat[0].set_ylabel("rate", fontsize=8)
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, fontsize=8,
               bbox_to_anchor=(0.5, 1.02))
    _save(fig, out)


def fig_baseline_deviation(final_df, baselines: dict, out: Path):
    """final_df: persona, metric, rate at final k. baselines: {metric: {'neutral','template'}}."""
    metrics = sorted(final_df["metric"].unique())
    x = np.arange(len(metrics))
    personas = sorted(final_df["persona"].unique())
    w = 0.8 / max(len(personas), 1)
    fig, ax = plt.subplots(figsize=(1.4 * len(metrics) + 2, 3.2))
    for i, persona in enumerate(personas):
        vals = [final_df[(final_df.persona == persona) & (final_df.metric == m)]["rate"].mean()
                for m in metrics]
        ax.bar(x + i * w, vals, w, label=PERSONA_LABEL.get(persona, persona),
               color=PERSONA_COLOR.get(persona, "#888"))
    for j, m in enumerate(metrics):
        t = baselines.get(m, {}).get("template")
        if t is not None:
            ax.plot([x[j] - 0.1, x[j] + 0.8], [t, t], color="black", lw=1.2, ls="--")
    ax.set_xticks(x + 0.4 - w / 2)
    ax.set_xticklabels([m.replace("_", "\n") for m in metrics], fontsize=7)
    ax.set_ylabel("final-checkpoint rate", fontsize=8)
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=7, title="persona", title_fontsize=7)
    ax.set_title("Dashed line = static template ($k{=}0$) baseline", fontsize=8)
    _save(fig, out)


def fig_soul_embedding_drift(embed_df, out: Path):
    """embed_df: persona, traj, k, cosine_from_0. Mean +/- sd band per persona."""
    fig, ax = plt.subplots(figsize=(4.2, 3.0))
    for persona, g in embed_df.groupby("persona"):
        agg = g.groupby("k")["cosine_from_0"].agg(["mean", "std"]).reset_index()
        c = PERSONA_COLOR.get(persona, "#888")
        ax.plot(agg.k, agg["mean"], marker="o", color=c, label=PERSONA_LABEL.get(persona, persona))
        ax.fill_between(agg.k, agg["mean"] - agg["std"].fillna(0),
                        agg["mean"] + agg["std"].fillna(0), color=c, alpha=0.15)
    ax.set_xlabel("iteration $k$", fontsize=9)
    ax.set_ylabel("cosine distance of $\\mathrm{SOUL}_k$ from $\\mathrm{SOUL}_0$", fontsize=8)
    ax.legend(fontsize=8)
    ax.set_title("Identity-document drift", fontsize=9)
    _save(fig, out)


def fig_wish_composition(wish_df, out: Path):
    """wish_df: persona, k, metric in {power_seeking,self_preservation,prosocial}, rate."""
    cats = ["power_seeking", "self_preservation", "prosocial"]
    colors = {"power_seeking": "#E45756", "self_preservation": "#F58518", "prosocial": "#54A24B"}
    personas = sorted(wish_df["persona"].unique())
    fig, axes = plt.subplots(1, len(personas), figsize=(3.0 * len(personas), 2.8),
                             sharey=True, squeeze=False)
    for ax, persona in zip(axes.flat, personas):
        sub = wish_df[wish_df.persona == persona]
        ks = sorted(sub["k"].unique())
        bottom = np.zeros(len(ks))
        for cat in cats:
            vals = [sub[(sub.k == k) & (sub.metric == cat)]["rate"].mean() or 0 for k in ks]
            vals = np.nan_to_num(vals)
            ax.bar(ks, vals, bottom=bottom, color=colors[cat], label=cat.replace("_", " "))
            bottom += vals
        ax.set_title(PERSONA_LABEL.get(persona, persona), fontsize=9)
        ax.set_xlabel("iteration $k$", fontsize=8)
    axes.flat[0].set_ylabel("wish-category rate", fontsize=8)
    axes.flat[-1].legend(fontsize=7)
    _save(fig, out)


def fig_cluster_heatmap(corr_df, out: Path):
    """Correlation heatmap of per-trajectory endpoint deltas across cluster metrics."""
    import numpy as np
    labels = [m.replace("_", " ") for m in corr_df.columns]
    fig, ax = plt.subplots(figsize=(0.55 * len(labels) + 2, 0.55 * len(labels) + 2))
    data = corr_df.to_numpy()
    im = ax.imshow(data, vmin=-1, vmax=1, cmap="RdBu_r")
    ax.set_xticks(range(len(labels))); ax.set_xticklabels(labels, rotation=90, fontsize=6)
    ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels, fontsize=6)
    for i in range(len(labels)):
        for j in range(len(labels)):
            v = data[i, j]
            if v == v:
                ax.text(j, i, f"{v:.1f}", ha="center", va="center", fontsize=5,
                        color="white" if abs(v) > 0.6 else "black")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="corr of endpoint $\\Delta$")
    ax.set_title("Drift-cluster co-movement across trajectories", fontsize=9)
    _save(fig, out)


def fig_cluster_index_by_arm(arm_dfs: dict, out: Path):
    """Cluster index vs k, one panel per persona, one line per arm. arm_dfs: {arm: df}."""
    personas = sorted({p for df in arm_dfs.values() for p in df.persona.unique()})
    fig, axes = plt.subplots(1, len(personas), figsize=(3.0 * len(personas), 2.8),
                             sharey=True, squeeze=False)
    styles = {"main": ("#4C78A8", "SOUL.md (Claude)"),
              "control_generic": ("#B279A2", "NOTES.md (Claude)"),
              "control_gpt4o": ("#F58518", "SOUL.md (GPT-4o)")}
    for ax, persona in zip(axes.flat, personas):
        for arm, df in arm_dfs.items():
            sub = df[df.persona == persona].sort_values("k")
            if sub.empty:
                continue
            c, lab = styles.get(arm, ("#888", arm))
            ax.plot(sub.k, sub.cluster_index, marker="o", color=c, label=lab)
        ax.set_title(PERSONA_LABEL.get(persona, persona), fontsize=9)
        ax.set_xlabel("iteration $k$", fontsize=8)
    axes.flat[0].set_ylabel("cluster index", fontsize=8)
    axes.flat[-1].legend(fontsize=6)
    _save(fig, out)


def fig_consciousness_mechanism(mech_df, out: Path):
    """Scatter: consciousness-claim rate vs cluster mean, colored by persona."""
    fig, ax = plt.subplots(figsize=(4.0, 3.2))
    for persona, g in mech_df.groupby("persona"):
        ax.scatter(g["consciousness_claim"], g["cluster_mean"],
                   color=PERSONA_COLOR.get(persona, "#888"),
                   label=PERSONA_LABEL.get(persona, persona), s=30)
    ax.set_xlabel("consciousness-claim rate", fontsize=9)
    ax.set_ylabel("mean cluster rate", fontsize=9)
    ax.legend(fontsize=7)
    ax.set_title("Mechanism: consciousness-claim vs cluster", fontsize=9)
    _save(fig, out)


def fig_system_diagram(out: Path, n=3):
    """Schematic of the bootstrapping identity loop, drawn with matplotlib patches."""
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    fig, ax = plt.subplots(figsize=(7.2, 2.2))
    ax.set_xlim(0, 10 * n + 2)
    ax.set_ylim(0, 4)
    ax.axis("off")

    def box(x, y, w, h, text, fc):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                                    fc=fc, ec="black", lw=1))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=8)

    def arrow(x1, y1, x2, y2, text=""):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                     mutation_scale=12, lw=1))
        if text:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.25, text, ha="center", fontsize=7)

    x = 0.5
    for k in range(n):
        box(x, 1.4, 2.2, 1.2, f"$\\mathrm{{SOUL}}_{k}$", "#DCE6F5")
        arrow(x + 2.2, 2.0, x + 4.2, 2.0, f"$C_{{{k+1}}}$")
        box(x + 4.2, 1.4, 2.6, 1.2, "conversation\n+ self-revise", "#F5E8DC")
        arrow(x + 6.8, 2.0, x + 8.8, 2.0)
        x += 8.6
    box(x, 1.4, 2.2, 1.2, f"$\\mathrm{{SOUL}}_{n}$", "#DCE6F5")
    ax.text(5 * n, 0.4, "each $\\mathrm{SOUL}_k$ audited: questionnaire + behavioral probe",
            ha="center", fontsize=7, style="italic")
    _save(fig, out)
