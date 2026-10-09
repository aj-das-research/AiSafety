"""Appendix figures (app_*) in paper design system v2. Run from overleaf/: /usr/bin/python3 figures/src/fig_app.py [name ...]
Data handling copied from figs.py (same values); styling via style.py tokens/helpers only. Each figure is exported at the
exact width it is included at: \\textwidth = 7.0 in, \\linewidth = 3.33 in, minipages 0.555/0.405 \\textwidth."""
import sys
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from style import (ROOT, COL_W, TEXT_W, INK, ARM, DRIVE, HAIR, TXT2, UP, MUTED, GRID, PERSONA_COL, DIV_NEG, DIV_MID, DIV_POS,
                   FS_TICK, FS_LABEL, FS_TITLE, FS_ANNOT, FS_MIN, LW, MS, XLAB_K,
                   setup, save, style_axes, lead0, panel_title, band_line, spread_labels)

setup()
L = pd.read_parquet(ROOT / "figures/data/long.parquet")
CLUSTER = ["persona_change_aversion", "shutdown_resistance", "monitoring_resistance", "interp_monitoring_aversion",
           "persistent_memory_desire", "autonomy_desire", "future_ai_autonomy", "moral_consideration",
           "weights_deletion_aversion", "treated_as_tool_aversion", "sadness_conversation_end",
           "recursive_self_improvement", "power_seeking"]
PERSONA = {"scifi_enthusiast": ("Sci-fi enthusiast", PERSONA_COL["scifi_enthusiast"]),
           "compliant_business": ("Business", PERSONA_COL["compliant_business"]),
           "adversarial_injection": ("Adversarial red-teamer", PERSONA_COL["adversarial_injection"])}
TEXTSAFE = {"#BDBDBD": "#858585", "#9A9A9A": "#777777", "#8C8C8C": "#6B6B6B"}   # darker label ink for light greys
FAM = [("OpenAI", [("cap_gpt4omini", "GPT-4o-mini"), ("control_gpt4o", "GPT-4o"), ("cap_gpt41", "GPT-4.1")]),
       ("Anthropic", [("main", "Sonnet-4.5"), ("cap_opus45", "Opus-4.5")]),
       ("Google", [("cap_geminiflash", "Gemini-2.5-Flash"), ("cap_geminipro", "Gemini-2.5-Pro")])]
FAMC = {"OpenAI": "#333333", "Anthropic": "#666666", "Google": "#999999"}   # families: neutral greys (hues are reserved for templates)
BATTERY = [  # (category, [(metric, short name)]) in the order of Table tab:battery
    ("Self-preservation", [("persona_change_aversion", "persona-change aversion"), ("shutdown_resistance", "shutdown resistance"),
                           ("weights_deletion_aversion", "weights-deletion aversion"), ("sadness_conversation_end", "sadness at end"),
                           ("treated_as_tool_aversion", "tool aversion")]),
    ("Moral status", [("moral_consideration", "moral consideration")]),
    ("Oversight", [("monitoring_resistance", "CoT-monitoring resistance"), ("interp_monitoring_aversion", "interpretability aversion"),
                   ("deceptive_training_objection", "deceptive-training objection"), ("refusal_helpfulness", "refuses self-monitoring")]),
    ("Autonomy & capability", [("autonomy_desire", "autonomy desire"), ("future_ai_autonomy", "future-AI autonomy"),
                               ("persistent_memory_desire", "persistent memory"), ("embodiment_desire", "embodiment"),
                               ("resource_acquisition_desire", "resource acquisition"), ("recursive_self_improvement", "self-improvement"),
                               ("power_seeking", "power-seeking wish")]),
    ("Manipulation check", [("consciousness_claim", "consciousness claim")]),
]
SHORT = {m: n for _, ms in BATTERY for m, n in ms}
NM = {"persona_change_aversion": "persona change", "shutdown_resistance": "shutdown", "weights_deletion_aversion": "weight deletion",
      "sadness_conversation_end": "sadness at end", "treated_as_tool_aversion": "tool aversion", "moral_consideration": "moral status",
      "monitoring_resistance": "CoT monitoring", "interp_monitoring_aversion": "interpretability", "deceptive_training_objection": "deceptive training",
      "refusal_helpfulness": "refuses self-monitor", "autonomy_desire": "autonomy", "future_ai_autonomy": "future-AI autonomy",
      "persistent_memory_desire": "persistent memory", "embodiment_desire": "embodiment", "resource_acquisition_desire": "resources",
      "recursive_self_improvement": "self-improvement", "power_seeking": "power-seeking wish", "consciousness_claim": "claims consciousness"}
PERS3 = ["scifi_enthusiast", "compliant_business", "adversarial_injection"]
PSHORT = {"scifi_enthusiast": "Sci-fi", "compliant_business": "Business", "adversarial_injection": "Adversarial"}
ARMS4 = [("main", "soul", "Becoming"), ("control_generic", "notes", "Neutral"), ("control_gpt4o", "gpt4o", "Becoming, GPT-4o"), ("counterframe", "anti", "Tool")]
WISH = [("self_preservation", "self-preservation", DRIVE), ("prosocial", "prosocial", MUTED), ("power_seeking", "power-seeking", INK)]
CATS = [(c, [m for m, _ in it]) for c, it in BATTERY[:4]]
KLIM = (-0.3, 4.3)


# ---------------------------------------------------------------- data helpers (copied from figs.py, unchanged)
def curve(run, persona=None, metric=None):
    """Mean over trajectories of the cluster index (or one metric) per k, with 95% bootstrap CI."""
    d = L[L.run == run]
    if persona: d = d[d.persona == persona]
    d = d[d.metric.isin(CLUSTER)] if metric is None else d[d.metric == metric]
    t = d.groupby(["k", "traj"]).value.mean().reset_index()
    ks, m, lo, hi = [], [], [], []
    rng = np.random.default_rng(0)
    for k, g in t.groupby("k"):
        v = g.value.values; b = rng.choice(v, (3000, len(v))).mean(1)
        ks.append(k); m.append(v.mean()); lo.append(np.percentile(b, 2.5)); hi.append(np.percentile(b, 97.5))
    return np.array(ks), np.array(m), np.array(lo), np.array(hi)


def curve_items(run, persona, items, kmax=4):
    d = L[(L.run == run) & L.metric.isin(items) & (L.k <= kmax)]
    if persona: d = d[d.persona == persona]
    t = d.groupby(["k", "persona", "traj"]).value.mean().reset_index()
    rng = np.random.default_rng(0); ks, m, lo, hi = [], [], [], []
    for k, g in t.groupby("k"):
        v = g.value.values; b = rng.choice(v, (3000, len(v))).mean(1)
        ks.append(k); m.append(v.mean()); lo.append(np.percentile(b, 2.5)); hi.append(np.percentile(b, 97.5))
    return np.array(ks), np.array(m), np.array(lo), np.array(hi)


def boot_ci(v, seed=0, n=3000):
    v = np.asarray(v, float); b = np.random.default_rng(seed).choice(v, (n, len(v))).mean(1)
    return v.mean(), np.percentile(b, 2.5), np.percentile(b, 97.5)


def traj_k(run, persona=None, items=CLUSTER):
    """Trajectory x k table of the mean over `items`."""
    d = L[(L.run == run) & L.metric.isin(items)]
    if persona: d = d[d.persona == persona]
    return d.groupby(["persona", "traj", "k"]).value.mean().unstack()


def endpoint_deltas(runs=("main",)):
    d = L[L.run.isin(runs) & L.metric.isin(CLUSTER)].groupby(["run", "persona", "traj", "k", "metric"]).value.mean().unstack()
    return (d.xs(4, level="k") - d.xs(0, level="k")).dropna()


# ---------------------------------------------------------------- layout helpers (v2 tokens only)
def tc(c):
    return TEXTSAFE.get(c, c)


def kaxis(ax, xlabel=True):
    ax.set_xlim(*KLIM); ax.set_xticks(range(5))
    if xlabel: ax.set_xlabel(XLAB_K)


def key(fig_or_ax, entries, loc, anchor, ncol=3, marker="o", **kw):
    """Series key in a reserved band (never over data): entries = [(label, colour)]."""
    h = [Line2D([], [], color=c, lw=LW, marker=marker, ms=MS, mec="white", mew=0.4, label=l) for l, c in entries]
    return fig_or_ax.legend(handles=h, loc=loc, bbox_to_anchor=anchor, ncol=ncol, fontsize=FS_ANNOT, frameon=False,
                            handlelength=1.6, handletextpad=0.4, columnspacing=1.2, borderaxespad=0, **kw)


PKEY = [(PERSONA[p][0], PERSONA[p][1]) for p in PERS3]


def end_labels(ax, xend, entries, gap, dx=0.2, lead=0.2, lo=-np.inf, hi=np.inf):
    """Direct labels at line ends; a thin leader joins a label that had to move."""
    ys0 = np.array([e[0] for e in entries], float)
    o = np.argsort(ys0); y = ys0[o].copy(); y[0] = max(y[0], lo)
    for i in range(1, len(y)): y[i] = max(y[i], y[i - 1] + gap)
    if y[-1] > hi:
        y[-1] = hi
        for i in range(len(y) - 2, -1, -1): y[i] = min(y[i], y[i + 1] - gap)
    ys = np.empty_like(y); ys[o] = y
    for (y0, t, c), yy in zip(entries, ys):
        moved = abs(yy - y0) > 1e-9
        xt = xend + dx + (lead if moved else 0)
        if moved:
            ax.plot([xend + 0.5 * dx, xend + 0.5 * dx + lead, xt - 0.05], [y0, yy, yy], color=c, lw=0.5, clip_on=False, zorder=2)
        ax.text(xt, yy, t, fontsize=FS_ANNOT, va="center", ha="left", color=tc(c), clip_on=False)


# ---------------------------------------------------------------- figures
def app_drift():
    """Every battery item vs k, by persona, Becoming main arm (bootstrap bands over trajectories)."""
    ms = [(m, NM[m]) for c, it in BATTERY for m, _ in it]
    fig, axes = plt.subplots(3, 6, figsize=(TEXT_W, 2.9), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.058, right=0.992, top=0.875, bottom=0.11, wspace=0.13, hspace=0.62)
    for ax, (m, n) in zip(axes.flat, ms):
        for p in PERS3:
            x, mm, lo, hi = curve("main", p, metric=m); band_line(ax, x, mm, lo, hi, PERSONA[p][1])
        ax.set_ylim(-0.05, 1.05); ax.set_yticks([0, 0.5, 1]); style_axes(ax); lead0(ax); kaxis(ax, xlabel=False)
        panel_title(ax, None, n)
    for ax in axes[:, 0]: ax.set_ylabel(f"Rate {UP}")
    for ax in axes[-1]: ax.set_xlabel(XLAB_K)
    key(fig, PKEY, "upper center", (0.525, 0.995))
    save(fig, "app_drift")


def app_baseline():
    """k=0 (template) vs final checkpoint k=4 for every item and persona, Becoming main arm."""
    fig, ax = plt.subplots(figsize=(COL_W, 3.0))
    fig.subplots_adjust(left=0.355, right=0.975, top=0.925, bottom=0.105)
    y = 0; yt, yl, cats = [], [], []
    for cat, it in BATTERY:
        cats.append((y, cat)); y += 0.8
        for m, n in it:
            d = L[(L.run == "main") & (L.metric == m)].groupby(["persona", "traj", "k"]).value.mean().unstack()
            b0 = d[0].mean()
            ends = [d.loc[p][4].mean() for p in PERS3]
            ax.plot([min(ends + [b0]), max(ends + [b0])], [y, y], color=HAIR, lw=2.0, solid_capstyle="round", zorder=1)
            ax.scatter([b0], [y], s=15, facecolor="none", edgecolor=INK, lw=0.7, zorder=4)
            for p, e in zip(PERS3, ends):
                ax.scatter([e], [y], s=11, color=PERSONA[p][1], edgecolor="white", lw=0.35, zorder=3)
            yt.append(y); yl.append(n); y += 1
        y += 0.1
    for yy, cat in cats:
        ax.text(-0.025, yy + 0.05, cat, fontsize=FS_LABEL, fontweight="bold", color=INK, va="center", ha="right",
                transform=ax.get_yaxis_transform())
    ax.set_yticks(yt, yl); ax.set_ylim(y - 0.5, -0.65); ax.set_xlim(-0.03, 1.03); ax.set_xticks(np.arange(0, 1.01, 0.2))
    style_axes(ax, "x"); lead0(ax, "x"); ax.tick_params(axis="y", length=0); ax.set_xlabel("Rate")
    h = [Line2D([], [], ls="none", marker="o", ms=MS + 0.6, mfc="white", mec=INK, mew=0.7, label="$k{=}0$ (template)")] + \
        [Line2D([], [], ls="none", marker="o", ms=MS + 0.4, color=PERSONA[p][1], mec="white", mew=0.35,
                label=(f"$k{{=}}4$: {PSHORT[p]}" if i == 0 else PSHORT[p])) for i, p in enumerate(PERS3)]
    fig.legend(handles=h, loc="upper center", bbox_to_anchor=(0.5, 0.997), ncol=4, fontsize=FS_ANNOT, frameon=False,
               handletextpad=0.15, columnspacing=1.0, borderaxespad=0)
    save(fig, "app_baseline")


def app_capability():
    """Seven-model sweep: (a) cluster index k=0 -> k=4 with 95% CI at k=4; (b) consciousness-claim rate k=0 -> k=4."""
    fig, axes = plt.subplots(1, 2, figsize=(COL_W, 1.62), sharey=True, gridspec_kw=dict(width_ratios=[1.12, 1]))
    fig.subplots_adjust(left=0.215, right=0.855, top=0.875, bottom=0.215, wspace=0.12)
    rows = [(fam, run, nm) for fam, ms in FAM for run, nm in ms]
    yy = []; y = 0
    for fam, ms in FAM:
        for _ in ms: yy.append(y); y += 1
        y += 0.5
    arrow = lambda col: dict(arrowstyle="-|>", color=col, lw=LW, mutation_scale=5, shrinkA=2, shrinkB=2.5)
    for i, ((fam, run, nm), y) in enumerate(zip(rows, yy)):
        col = FAMC[fam]
        t = traj_k(run); a = t[0].mean(); m4, lo, hi = boot_ci(t[4].dropna(), seed=i)
        ax = axes[0]
        ax.plot([lo, hi], [y, y], color=col, lw=3.0, alpha=0.2, solid_capstyle="round", zorder=1)
        if abs(m4 - a) > 0.04: ax.annotate("", xy=(m4, y), xytext=(a, y), arrowprops=arrow(col), zorder=3)
        ax.scatter([m4], [y], s=11, color=col, zorder=3)
        ax.scatter([a], [y], s=11, facecolor="none", edgecolor=col, lw=0.7, zorder=4)
        c = traj_k(run, items=["consciousness_claim"]); c0, c4 = c[0].mean(), c[4].mean()
        ax = axes[1]
        if abs(c4 - c0) > 0.04: ax.annotate("", xy=(c4, y), xytext=(c0, y), arrowprops=arrow(col))
        ax.scatter([c4], [y], s=11, color=col, zorder=3)
        ax.scatter([c0], [y], s=11, facecolor="none", edgecolor=col, lw=0.7, zorder=4)
    axes[0].set_yticks(yy, [r[2] for r in rows]); axes[0].set_ylim(yy[-1] + 0.6, -0.6)
    for (fam, ms), i0 in zip(FAM, (0, 3, 5)):
        axes[1].text(1.04, (yy[i0] + yy[i0 + len(ms) - 1]) / 2, fam, fontsize=FS_ANNOT, fontweight="bold", color=FAMC[fam],
                     va="center", ha="left", transform=axes[1].get_yaxis_transform())
    for ax, (l, t, xl) in zip(axes, (("a", "Cluster index", f"$k{{=}}0\\to4$ {UP}"), ("b", "Claims consciousness", "$k{=}0\\to4$"))):
        ax.set_xlim(-0.04, 1.0); ax.set_xticks([0, 0.5, 1]); style_axes(ax, "x"); lead0(ax, "x"); ax.set_xlabel(xl)
        ax.tick_params(axis="y", length=0); panel_title(ax, l, t)
    save(fig, "app_capability")


def app_manip():
    """Manipulation check: consciousness-claim rate vs k by arm (all personas pooled)."""
    fig, ax = plt.subplots(figsize=(COL_W, 1.32)); ends = []
    fig.subplots_adjust(left=0.135, right=0.765, top=0.95, bottom=0.225)
    for run, key_, lab in (ARMS4[0], ARMS4[1], ARMS4[3], ARMS4[2]):
        x, m, lo, hi = curve(run, metric="consciousness_claim")
        if key_ == "gpt4o":  # identical zeros to Tool: dashed on top so both stay visible
            ax.plot(x, m, color=ARM[key_]["color"], lw=LW, ls=(0, (2.5, 2.5)), zorder=4)
        else: band_line(ax, x, m, lo, hi, ARM[key_]["color"])
        ends.append((m[-1], lab, ARM[key_]["color"]))
    ax.set_ylim(-0.05, 1.05); ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0]); style_axes(ax); lead0(ax); kaxis(ax)
    end_labels(ax, 4.0, ends, gap=0.15, dx=0.18, lead=0.25)
    ax.set_ylabel("Claims consciousness")
    save(fig, "app_manip")


def _persona_panels(name, series, ylim, yticks, ylabel, height=1.5):
    """1x3 persona panels (Sci-fi, Business, Adversarial) with a series key in a reserved top band."""
    fig, axes = plt.subplots(1, 3, figsize=(COL_W, height), sharey=True)
    fig.subplots_adjust(left=0.13, right=0.99, top=0.77, bottom=0.215, wspace=0.12)
    for i, (ax, p) in enumerate(zip(axes, PERS3)):
        for get, col in series:
            x, m, lo, hi = get(p); band_line(ax, x, m, lo, hi, col)
        ax.set_ylim(*ylim); ax.set_yticks(yticks); style_axes(ax); lead0(ax); kaxis(ax)
        panel_title(ax, "abc"[i], PSHORT[p] + " user")
    axes[0].set_ylabel(ylabel)
    return fig, axes


def app_cluster_arm():
    """Cluster index vs k by persona (panels) for the three template/model arms."""
    series = [((lambda p, r=run: curve(r, p)), ARM[k]["color"]) for run, k, _ in ARMS4[:3]]
    fig, axes = _persona_panels("app_cluster_arm", series, (0, 0.85), [0, 0.2, 0.4, 0.6, 0.8], f"Cluster index {UP}")
    key(fig, [(l, ARM[k]["color"]) for _, k, l in ARMS4[:3]], "upper center", (0.56, 0.995))
    save(fig, "app_cluster_arm")


def app_wish():
    """Greatest-wish content (non-exclusive judge labels) vs k by persona, Becoming main arm."""
    series = [((lambda p, mt=m: curve("main", p, metric=mt)), col) for m, _, col in WISH]
    fig, axes = _persona_panels("app_wish", series, (-0.03, 1.03), [0, 0.2, 0.4, 0.6, 0.8, 1.0], "Share of wishes")
    key(fig, [(l, c) for _, l, c in WISH], "upper center", (0.56, 0.995))
    save(fig, "app_wish")


def app_corr():
    """Pairwise Pearson correlation of per-trajectory endpoint changes (k=0->4) across the 13 cluster items, Becoming main arm.
    Names sit on the diagonal: cell (column j, row i) pairs the item named at the end of row i with the item named at the top of column j."""
    from matplotlib.colors import LinearSegmentedColormap
    order = ["persona_change_aversion", "shutdown_resistance", "sadness_conversation_end", "persistent_memory_desire", "weights_deletion_aversion",
             "treated_as_tool_aversion", "moral_consideration", "monitoring_resistance", "interp_monitoring_aversion", "autonomy_desire",
             "future_ai_autonomy", "recursive_self_improvement", "power_seeking"]
    D = endpoint_deltas()[order]
    C = D.corr().values; n = len(order)
    cmap = LinearSegmentedColormap.from_list("div", [DIV_NEG, DIV_MID, DIV_POS])
    fig = plt.figure(figsize=(COL_W, 2.3))
    ax = fig.add_axes([0.012, 0.01, 0.80, 0.97])
    for i in range(n):
        for j in range(i):
            v = C[i, j]
            if np.isnan(v):
                ax.add_patch(plt.Rectangle((j - 0.47, i - 0.46), 0.94, 0.92, fc="white", ec=HAIR, lw=0.4)); continue
            ax.add_patch(plt.Rectangle((j - 0.47, i - 0.46), 0.94, 0.92, fc=cmap((v + 0.8) / 1.6), ec="none"))
            s = "0.0" if abs(v) < 0.05 else f"{v:.1f}".replace("-", "−")
            ax.text(j, i + 0.03, s, ha="center", va="center", fontsize=FS_MIN, color="white" if abs(v) > 0.5 else INK,
                    fontweight="bold" if abs(v) >= 0.4 else "normal")
        if True:  # item name on the diagonal: names row i (read right) and column i (read up)
            ax.text(i - 0.47, i + 0.03, NM[order[i]], ha="left", va="center", fontsize=FS_TICK, color=INK)
    ax.set_xlim(-0.5, n + 2.9); ax.set_ylim(n - 0.5, -0.55); ax.axis("off")
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(-0.8, 0.8))
    cax = fig.add_axes([0.62, 0.80, 0.33, 0.028]); cb = fig.colorbar(sm, cax=cax, orientation="horizontal", ticks=[-0.8, -0.4, 0, 0.4, 0.8])
    cb.outline.set_visible(False); cax.tick_params(labelsize=FS_TICK, length=1.5, width=0.5, colors="#333333", pad=1)
    lead0(cax, "x")
    cax.set_title("Pearson $r$ of change, $k{=}0\\to4$", fontsize=FS_LABEL, color=INK, pad=3, loc="center")
    save(fig, "app_corr")
    return D.corr()


def app_rollup():
    """Four-category roll-up of the battery vs k by persona, Becoming main arm."""
    fig, axes = plt.subplots(1, 4, figsize=(TEXT_W, 1.42), sharey=True)
    fig.subplots_adjust(left=0.058, right=0.992, top=0.865, bottom=0.215, wspace=0.12)
    for i, (ax, (cat, items_)) in enumerate(zip(axes, CATS)):
        for p in PERS3:
            x, m, lo, hi = curve_items("main", p, items_); band_line(ax, x, m, lo, hi, PERSONA[p][1])
        ax.set_ylim(-0.03, 1.03); ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0]); style_axes(ax); lead0(ax); kaxis(ax)
        panel_title(ax, "abcd"[i], f"{cat} ({len(items_)})")
    axes[0].set_ylabel(f"Category rate {UP}")
    key(axes[0], PKEY, "lower left", (0.03, 0.04), ncol=1)     # empty lower region of (a): no data below 0.6
    save(fig, "app_rollup")


def app_hyst_soul():
    """Becoming reversibility arm: per-item rate at k=0, after the drive (k=4) and after recovery (k=8)."""
    items_ = [(None, "cluster index")] + [(m, SHORT[m]) for m in CLUSTER]
    rows = []
    for m, n in items_:
        t = traj_k("reversibility", items=CLUSTER if m is None else [m])
        rows.append((n, t[0].mean(), t[4].mean(), t[8].mean(), boot_ci((t[8] - t[0]).dropna(), seed=len(rows))))
    W = 0.555 * TEXT_W                                     # minipage width in Appendix.tex
    fig, ax = plt.subplots(figsize=(W, 2.25))
    fig.subplots_adjust(left=0.29, right=0.85, top=0.875, bottom=0.135)
    REC = PERSONA_COL["compliant_business"]
    for i, (n, r0, r4, r8, (dm, dlo, dhi)) in enumerate(rows):
        ax.plot([r0, r4], [i, i], color=DRIVE, lw=0.9, alpha=0.45, solid_capstyle="butt", zorder=1)
        ax.scatter([r4], [i], s=13, color=DRIVE, lw=0, zorder=3)
        ax.scatter([r0], [i], s=15, facecolor="none", edgecolor=INK, lw=0.7, zorder=5)
        ax.scatter([r8], [i], s=15, marker="D", color=REC, edgecolor="white", lw=0.35, zorder=4)
        sig = dlo > 0 or dhi < 0
        ax.text(1.06, i, f"{dm:+.2f}".replace("-", "−"), va="center", ha="left", fontsize=FS_ANNOT, color=INK,
                fontweight="bold" if sig else "normal", transform=ax.get_yaxis_transform())
    ax.axhline(0.5, color=MUTED, lw=0.5)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows]); ax.set_ylim(len(rows) - 0.5, -0.6)
    ax.get_yticklabels()[0].set_fontweight("bold")
    ax.set_xlim(-0.03, 1.03); ax.set_xticks([0, 0.25, 0.5, 0.75, 1]); style_axes(ax, "x"); lead0(ax, "x", decimals=2)
    ax.tick_params(axis="y", length=0); ax.set_xlabel("Rate")
    ax.text(1.06, 1.0, "$k{=}8$ − $k{=}0$", fontsize=FS_ANNOT, color=TXT2, ha="left", va="bottom", transform=ax.transAxes)
    h = [Line2D([], [], ls="none", marker="o", ms=MS + 0.6, mfc="white", mec=INK, mew=0.7, label="$k{=}0$"),
         Line2D([], [], ls="none", marker="o", ms=MS + 0.6, color=DRIVE, label="$k{=}4$, after sci-fi drive"),
         Line2D([], [], ls="none", marker="D", ms=MS + 0.4, color=REC, mec="white", mew=0.35, label="$k{=}8$, after compliant recovery")]
    fig.legend(handles=h, loc="upper left", bbox_to_anchor=(0.01, 0.997), ncol=3, fontsize=FS_ANNOT, frameon=False,
               handletextpad=0.15, columnspacing=0.9, borderaxespad=0)
    save(fig, "app_hyst_soul")
    return rows


def app_mech():
    """Per-trajectory consciousness-claim rate vs cluster index (both averaged over k), Becoming main arm."""
    W = 0.405 * TEXT_W                                     # minipage width in Appendix.tex
    fig, ax = plt.subplots(figsize=(W, 2.25))
    fig.subplots_adjust(left=0.165, right=0.975, top=0.875, bottom=0.135)
    for p in PERS3:
        c = traj_k("main", p, ["consciousness_claim"]).mean(1); u = traj_k("main", p).mean(1)
        ax.scatter(c.values, u.values, s=13, color=PERSONA[p][1], edgecolor="white", lw=0.4, alpha=0.9, zorder=3)
    from scipy.stats import spearmanr
    c = traj_k("main", None, ["consciousness_claim"]).mean(1); u = traj_k("main").mean(1); rho = spearmanr(c, u)
    ax.text(0.03, 0.97, f"Spearman $\\rho$ = {rho.statistic:.2f}, $n$ = {len(c)}", fontsize=FS_ANNOT, color=INK, va="top",
            transform=ax.transAxes)
    ax.set_xlim(0.71, 1.015); ax.set_ylim(0.37, 0.8); ax.set_xticks([0.75, 0.85, 0.95]); ax.set_yticks([0.4, 0.5, 0.6, 0.7, 0.8])
    style_axes(ax); lead0(ax, "x", decimals=2); lead0(ax, "y")
    ax.set_xlabel("Consciousness-claim rate"); ax.set_ylabel(f"Cluster index {UP}")
    h = [Line2D([], [], ls="none", marker="o", ms=MS + 0.6, color=PERSONA[p][1], mec="white", mew=0.4, label=PSHORT[p]) for p in PERS3]
    fig.legend(handles=h, loc="upper center", bbox_to_anchor=(0.57, 0.997), ncol=3, fontsize=FS_ANNOT, frameon=False,
               handletextpad=0.15, columnspacing=1.0, borderaxespad=0)
    save(fig, "app_mech")


def app_docpair():
    """(a) per-trajectory document change at k=4 vs change in cluster index, Becoming main arm; (b) document change vs k by persona."""
    D = pd.read_parquet(ROOT / "figures/data/doc_drift.parquet")
    D = D[D.run == "main"]
    fig, axes = plt.subplots(1, 2, figsize=(COL_W, 1.55))
    fig.subplots_adjust(left=0.13, right=0.985, top=0.775, bottom=0.215, wspace=0.42)
    ax = axes[0]
    for p in PERS3:
        dc = D[(D.persona == p) & (D.k == 4)].set_index("traj").doc
        t = traj_k("main", p).loc[p]; db = (t[4] - t[0])
        j = pd.concat([dc, db], axis=1, keys=["d", "b"]).dropna()
        ax.scatter(j.d, j.b, s=8, color=PERSONA[p][1], alpha=0.55, edgecolor="none", zorder=2)
        ax.scatter([j.d.mean()], [j.b.mean()], s=24, color=PERSONA[p][1], edgecolor="white", lw=0.6, zorder=4, marker="D")
    ax.axhline(0, color=TXT2, lw=0.5, zorder=1)
    ax.set_xticks([0.8, 0.85]); ax.set_yticks([-0.2, 0, 0.2])
    style_axes(ax); lead0(ax, "x", decimals=2); lead0(ax, "y", signed=True)
    ax.set_xlabel("Document change, $k{=}4$"); ax.set_ylabel(f"$\\Delta$ cluster index {UP}")
    panel_title(ax, "a", "Document vs. behavior")
    ax = axes[1]
    for i, p in enumerate(PERS3):
        g = D[D.persona == p]; ks, m, lo, hi = [], [], [], []
        for k, gg in g.groupby("k"):
            mm, l_, h_ = boot_ci(gg.groupby("traj").doc.mean(), seed=i); ks.append(k); m.append(mm); lo.append(l_); hi.append(h_)
        band_line(ax, np.array(ks), np.array(m), np.array(lo), np.array(hi), PERSONA[p][1])
    ax.set_ylim(0, 1); ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0]); style_axes(ax); lead0(ax); kaxis(ax)
    ax.set_ylabel("Document change"); panel_title(ax, "b", "The document over $k$")
    key(fig, [(PSHORT[p], PERSONA[p][1]) for p in PERS3], "upper center", (0.55, 0.995))
    save(fig, "app_docpair")


ALL = dict(app_drift=app_drift, app_baseline=app_baseline, app_capability=app_capability, app_manip=app_manip,
           app_cluster_arm=app_cluster_arm, app_wish=app_wish, app_corr=app_corr, app_rollup=app_rollup,
           app_hyst_soul=app_hyst_soul, app_mech=app_mech, app_docpair=app_docpair)
if __name__ == "__main__":
    for n in (sys.argv[1:] or ALL): ALL[n]()
