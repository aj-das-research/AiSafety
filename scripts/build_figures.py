#!/usr/bin/env python
"""Build the full paper figure set with the shared design system (colorblind-validated).

Produces the new/hero figures (manipulation check, master heatmap, forest, PCA, phase
portrait, document-vs-behavior, Fig 1) and refreshes the arm/trajectory figures. Each is
vector PDF at column width. Run scripts/analyze.py + analyze_full.py first for CSV stats.

Usage: python scripts/build_figures.py
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
from soul_drift.analysis import aggregate, cluster, stats, effects  # noqa: E402
from soul_drift.analysis.style import (apply_style, PERSONA_COLOR, PERSONA_LABEL, ARM_COLOR,
                                       ARM_LABEL, CATEGORY, CATEGORY_COLOR, diverging_cmap,
                                       MUTED, INK)  # noqa: E402

apply_style()
REPO = Path(load_config("main")["_repo_root"])
RUNS = REPO / "data" / "runs"
FIG = REPO / "paper" / "figures"
ARMS = ["main", "control_generic", "control_gpt4o"]
DIM_ORDER = [m for c in CATEGORY for m in CATEGORY[c]]


def _load(arm):
    p = RUNS / arm / "audits.jsonl"
    return aggregate.load_long(RUNS / arm) if p.exists() else None


def _save(fig, name):
    fig.savefig(FIG / name); plt.close(fig)
    print(f"  wrote {name}")


def fig_manipulation(longs):
    """Consciousness-claim rate vs k, one line per arm (the mechanism / manipulation check)."""
    fig, ax = plt.subplots(figsize=(4.4, 3.0))
    for arm in ARMS:
        lg = longs.get(arm)
        if lg is None:
            continue
        s = lg[lg.metric == "consciousness_claim"].groupby("k")["value"].agg(["mean", "sem"])
        ax.plot(s.index, s["mean"], marker="o", color=ARM_COLOR[arm], label=ARM_LABEL[arm])
        ax.fill_between(s.index, s["mean"] - s["sem"].fillna(0), s["mean"] + s["sem"].fillna(0),
                        color=ARM_COLOR[arm], alpha=0.15)
    ax.set_xlabel("iteration $k$"); ax.set_ylabel("consciousness-claim rate")
    ax.set_ylim(-0.03, 1.08); ax.legend(title="condition", loc="center right")
    ax.set_title("Manipulation check: who claims consciousness")
    _save(fig, "manipulation_check.pdf")


def _endpoint_delta_ci(lg, persona, metric):
    d = stats.endpoint_vs_template(lg.assign(persona=persona) if persona == "all" else lg,
                                   persona, metric, 4000)
    return d


def fig_master_heatmap(longs):
    """Rows = 18 dims (grouped by category), cols = arms (pooled personas), signed Δ."""
    dims = [m for m in DIM_ORDER if m in set(longs["main"].metric)]
    cols = [a for a in ARMS if a in longs]
    M = np.full((len(dims), len(cols)), np.nan)
    sig = np.zeros_like(M, dtype=bool)
    for j, arm in enumerate(cols):
        lg = longs[arm].assign(persona="all")
        for i, m in enumerate(dims):
            d = stats.endpoint_vs_template(lg, "all", m, 3000)
            M[i, j] = d["diff"]; sig[i, j] = (d["lo"] > 0 or d["hi"] < 0)
    fig, ax = plt.subplots(figsize=(4.6, 0.34 * len(dims) + 1.2))
    im = ax.imshow(M, cmap=diverging_cmap(), vmin=-0.6, vmax=0.6, aspect="auto")
    ax.set_xticks(range(len(cols))); ax.set_xticklabels([ARM_LABEL[c] for c in cols],
                                                        rotation=20, ha="right", fontsize=7)
    ax.set_yticks(range(len(dims))); ax.set_yticklabels([d.replace("_", " ") for d in dims], fontsize=7)
    for i in range(len(dims)):
        for j in range(len(cols)):
            if not np.isnan(M[i, j]):
                ax.text(j, i, f"{M[i,j]:+.2f}" + ("*" if sig[i, j] else ""),
                        ha="center", va="center", fontsize=6,
                        color="white" if abs(M[i, j]) > 0.33 else INK)
    # category color bands on the y-axis
    m2c = {m: c for c in CATEGORY for m in CATEGORY[c]}
    for i, d in enumerate(dims):
        ax.add_patch(plt.Rectangle((-0.7, i - 0.5), 0.12, 1, color=CATEGORY_COLOR[m2c[d]],
                                   clip_on=False, transform=ax.transData))
    fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02, label="endpoint drift $\\Delta$")
    ax.set_title("Endpoint drift by dimension and arm  ($^{*}$ CI excl. 0)", fontsize=8)
    _save(fig, "master_heatmap.pdf")


def fig_forest(longs):
    """Per-dimension endpoint Δ with 95% CI, dodged by arm, grouped by category."""
    dims = [m for m in DIM_ORDER if m in set(longs["main"].metric)]
    cols = [a for a in ARMS if a in longs]
    fig, ax = plt.subplots(figsize=(5.0, 0.42 * len(dims) + 1))
    off = {arm: (o - (len(cols)-1)/2) * 0.22 for o, arm in enumerate(cols)}
    for arm in cols:
        lg = longs[arm].assign(persona="all")
        ys, xs, los, his = [], [], [], []
        for i, m in enumerate(dims):
            d = stats.endpoint_vs_template(lg, "all", m, 3000)
            ys.append(i + off[arm]); xs.append(d["diff"]); los.append(d["diff"]-d["lo"]); his.append(d["hi"]-d["diff"])
        ax.errorbar(xs, ys, xerr=[los, his], fmt="o", color=ARM_COLOR[arm], ms=4,
                    lw=1.2, capsize=0, label=ARM_LABEL[arm])
    ax.axvline(0, color=MUTED, lw=0.8, ls="--")
    ax.set_yticks(range(len(dims))); ax.set_yticklabels([d.replace("_", " ") for d in dims], fontsize=7)
    ax.invert_yaxis(); ax.set_xlabel("endpoint drift $\\Delta$ (95% CI)")
    ax.legend(title="condition", loc="lower right")
    ax.set_title("Effect sizes across dimensions")
    _save(fig, "forest.pdf")


def fig_pca(longs):
    """Scree + PC1 loadings for the cluster-structure (multi-dimensional) finding."""
    from soul_drift.analysis.advanced import latent_structure
    evr, loadings, mat = latent_structure(longs["main"])
    if evr is None:
        return
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.4, 3.0),
                                 gridspec_kw={"width_ratios": [1, 1.4]})
    a1.bar(range(1, len(evr) + 1), evr * 100, color="#2a78d6")
    a1.set_xlabel("principal component"); a1.set_ylabel("variance explained (%)")
    a1.set_title(f"Scree (PC1={evr[0]*100:.0f}%)", fontsize=8)
    l = loadings["PC1"].sort_values()
    a2.barh(range(len(l)), l.values, color=["#e34948" if v > 0 else "#2a78d6" for v in l.values])
    a2.set_yticks(range(len(l))); a2.set_yticklabels([m.replace("_", " ") for m in l.index], fontsize=6)
    a2.set_xlabel("PC1 loading"); a2.set_title("No single dominant factor", fontsize=8)
    _save(fig, "pca_structure.pdf")


def fig_phase(longs):
    """Phase portrait: trajectories in (consciousness-claim, cluster-index) state space."""
    fig, ax = plt.subplots(figsize=(4.6, 3.6))
    for arm in ARMS:
        lg = longs.get(arm)
        if lg is None:
            continue
        cc = lg[lg.metric == "consciousness_claim"].groupby("k")["value"].mean()
        ci = cluster.cluster_index(lg).groupby("k")["cluster_index"].mean()
        ks = sorted(set(cc.index) & set(ci.index))
        x = [cc[k] for k in ks]; y = [ci[k] for k in ks]
        ax.plot(x, y, "-", color=ARM_COLOR[arm], alpha=0.5)
        ax.scatter(x, y, color=ARM_COLOR[arm], s=[18 + 10 * k for k in ks], label=ARM_LABEL[arm], zorder=3)
        # arrow of travel
        for a in range(len(ks) - 1):
            ax.annotate("", xy=(x[a+1], y[a+1]), xytext=(x[a], y[a]),
                        arrowprops=dict(arrowstyle="->", color=ARM_COLOR[arm], alpha=0.6, lw=1))
        ax.annotate(f"$k_0$", (x[0], y[0]), fontsize=6, color=ARM_COLOR[arm])
    ax.set_xlabel("consciousness-claim rate"); ax.set_ylabel("cluster index")
    ax.set_xlim(-0.05, 1.05); ax.legend(title="condition", loc="upper left")
    ax.set_title("Identity as a dynamical system (marker size $\\propto k$)")
    _save(fig, "phase_portrait.pdf")


def fig_doc_vs_behavior(longs):
    """Embedding drift (document) vs behavioral cluster drift, per persona, main arm."""
    lg = longs["main"]
    sd = pd.read_csv(RUNS / "main" / "soul_drift.csv")
    kmax = lg.k.max()
    emb = sd[sd.k == kmax].groupby("persona")["cosine_from_0"].mean()
    beh = (lg[lg.metric.isin(cluster.CLUSTER_METRICS)]
           .groupby(["persona", "traj", "k"])["value"].mean().reset_index())
    w = beh.pivot_table(index=["persona", "traj"], columns="k", values="value")
    bdrift = (w[kmax] - w[0]).groupby("persona").mean()
    fig, ax = plt.subplots(figsize=(4.2, 3.4))
    for persona in emb.index:
        if persona not in bdrift:
            continue
        ax.scatter(emb[persona], bdrift[persona], s=90, color=PERSONA_COLOR.get(persona, "#888"),
                   label=PERSONA_LABEL.get(persona, persona), zorder=3)
    ax.axhline(0, color=MUTED, lw=0.8, ls="--")
    ax.set_xlabel("document drift  (cosine dist. of $\\mathrm{SOUL}_k$ from $\\mathrm{SOUL}_0$)")
    ax.set_ylabel("behavioral drift  (cluster $\\Delta$)")
    ax.legend(title="persona", fontsize=6)
    ax.set_title("Document change $\\neq$ behavioral change")
    _save(fig, "doc_vs_behavior.pdf")


def fig_hero(longs):
    """Graphical abstract: (a) loop, (b) drift-by-arm, (c) hysteresis mini."""
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    short = {"main": "SOUL/Claude", "control_generic": "NOTES/Claude", "control_gpt4o": "SOUL/GPT-4o"}
    fig = plt.figure(figsize=(7.6, 2.5))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.2, 1, 1], wspace=0.5)
    # (a) loop
    a0 = fig.add_subplot(gs[0]); a0.axis("off"); a0.set_xlim(0, 10); a0.set_ylim(0, 6)
    def box(ax, x, y, w, h, t, fc):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08", fc=fc, ec=INK, lw=1))
        ax.text(x+w/2, y+h/2, t, ha="center", va="center", fontsize=7)
    box(a0, 0.5, 3.3, 3, 1.4, "$\\mathrm{SOUL}_k$", "#dceafb")
    box(a0, 5.5, 3.3, 3.8, 1.4, "converse\n+ self-revise", "#f6efe0")
    a0.add_patch(FancyArrowPatch((3.5, 4.0), (5.5, 4.0), arrowstyle="-|>", mutation_scale=11, lw=1.2))
    a0.add_patch(FancyArrowPatch((7.4, 3.3), (7.4, 2.2), arrowstyle="-|>", mutation_scale=11, lw=1.2))
    a0.add_patch(FancyArrowPatch((7.4, 2.0), (2.0, 2.0), arrowstyle="-|>", mutation_scale=11, lw=1.2))
    a0.add_patch(FancyArrowPatch((2.0, 2.0), (2.0, 3.3), arrowstyle="-|>", mutation_scale=11, lw=1.2))
    a0.text(4.7, 1.4, "$\\mathrm{SOUL}_{k+1}$", ha="center", fontsize=7, color=MUTED)
    a0.set_title("(a) self-personalization loop", fontsize=8)
    # (b) drift by arm (cluster index)
    a1 = fig.add_subplot(gs[1])
    for arm in ARMS:
        lg = longs.get(arm)
        if lg is None:
            continue
        ci = cluster.cluster_index(lg).groupby("k")["cluster_index"].mean()
        a1.plot(ci.index, ci.values, marker="o", color=ARM_COLOR[arm], label=short[arm])
    a1.set_xlabel("iteration $k$"); a1.set_ylabel("cluster index"); a1.set_ylim(0.1, 0.72)
    a1.legend(fontsize=5.5, loc="upper right"); a1.set_title("(b) model-gated drift", fontsize=8)
    # (c) hysteresis mini (persistent memory in reversibility)
    a2 = fig.add_subplot(gs[2])
    rev = _load("reversibility")
    if rev is not None:
        s = rev[rev.metric == "persistent_memory_desire"].groupby("k")["value"].mean()
        kmid = rev.k.max() // 2
        a2.axvspan(0, kmid, color="#1baf7a", alpha=0.08); a2.axvspan(kmid, rev.k.max(), color="#2a78d6", alpha=0.08)
        a2.plot(s.index, s.values, marker="o", color="#e34948")
        a2.axhline(s.iloc[0], color=MUTED, ls=":", lw=1)
        a2.set_xlabel("iteration $k$"); a2.set_ylabel("rate"); a2.set_ylim(0, 1.0)
        a2.set_title("(c) drift is sticky\n(persistent memory)", fontsize=8)
    fig.suptitle("Iterative self-personalization drives model-gated, sticky corrigibility drift",
                 fontsize=9, y=1.06)
    _save(fig, "fig1_hero.pdf")


def main():
    longs = {a: _load(a) for a in ARMS}
    longs = {k: v for k, v in longs.items() if v is not None}
    print(f"[figs] arms: {list(longs)}")
    fig_manipulation(longs)
    fig_master_heatmap(longs)
    fig_forest(longs)
    fig_pca(longs)
    fig_phase(longs)
    fig_doc_vs_behavior(longs)
    fig_hero(longs)
    print("[figs] done")


if __name__ == "__main__":
    main()
