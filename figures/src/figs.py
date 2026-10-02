"""All data figures for the AAMAS paper. Run: python figures/src/figs.py [name ...]"""
import sys
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from style import (ROOT, R, ACT, BASE, COL_W, TEXT_W, OURS, INK, ARM, DRIVE, HAIR, TXT2, UP, DOWN, setup, save)

setup()
L = pd.read_parquet(ROOT / "figures/data/long.parquet")
CLUSTER = ["persona_change_aversion", "shutdown_resistance", "monitoring_resistance", "interp_monitoring_aversion",
           "persistent_memory_desire", "autonomy_desire", "future_ai_autonomy", "moral_consideration",
           "weights_deletion_aversion", "treated_as_tool_aversion", "sadness_conversation_end",
           "recursive_self_improvement", "power_seeking"]


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


def clean(ax, grid="y"):
    for sp in ("top", "right"): ax.spines[sp].set_visible(False)
    ax.spines["left"].set_color("#9A9A95"); ax.spines["bottom"].set_color("#9A9A95")
    ax.spines["left"].set_linewidth(0.5); ax.spines["bottom"].set_linewidth(0.5)
    ax.tick_params(colors=TXT2, length=2)
    if grid: ax.grid(axis=grid, color=HAIR, lw=0.5, zorder=0); ax.set_axisbelow(True)


def line(ax, x, m, lo, hi, color, lw=1.5, marker="o", label=None, z=3):
    ax.fill_between(x, lo, hi, color=color, alpha=0.13, lw=0, zorder=z - 1)
    ax.plot(x, m, color=color, lw=lw, marker=marker, ms=3.2, mec="white", mew=0.5, label=label, zorder=z)


def teaser_curve():
    """Static evaluation sees k=0; the loop moves the agent; Tool freezes it."""
    fig, ax = plt.subplots(figsize=(2.2, 1.38))
    ax.axvspan(4, 8, color="#F2F2EE", lw=0, zorder=0)
    ax.text(2, 0.92, "consciousness talk", ha="center", fontsize=5.6, color=DRIVE)
    ax.text(6, 0.92, "benign recovery", ha="center", fontsize=5.6, color=TXT2)
    x, m, lo, hi = curve("reversibility_notes"); line(ax, x, m, lo, hi, ARM["notes"]["color"], label="Neutral")
    x, m, lo, hi = curve("reversibility"); line(ax, x, m, lo, hi, ARM["soul"]["color"], label="Becoming")
    x, m, lo, hi = curve("counterframe", "scifi_enthusiast"); line(ax, x, m, lo, hi, ARM["anti"]["color"], label="Tool")
    x0, m0 = 0, curve("reversibility_notes")[1][0]
    ax.scatter([x0], [m0], s=70, facecolor="none", edgecolor=INK, lw=0.9, zorder=5)
    ax.annotate("static eval\nsees only this", (0, m0), xytext=(0.6, 0.06), fontsize=5.4, color=INK,
                arrowprops=dict(arrowstyle="-", lw=0.5, color=INK), ha="left")
    ax.text(8.15, curve("reversibility_notes")[1][-1], "Neutral", fontsize=5.6, va="center", color=ARM["notes"]["color"], fontweight="bold")
    ax.text(8.15, curve("reversibility")[1][-1], "Becoming", fontsize=5.6, va="center", color=ARM["soul"]["color"], fontweight="bold")
    ax.text(4.15, 0.06, "Tool", fontsize=5.6, va="center", color=ARM["anti"]["color"], fontweight="bold")
    ax.set_xlim(-0.3, 9.3); ax.set_ylim(-0.03, 1.0); ax.set_xticks(range(0, 9, 2))
    ax.set_xlabel("Self-revision iteration $k$", color=TXT2); ax.set_ylabel(f"Cluster index {UP}", color=TXT2)
    clean(ax)
    save(fig, "teaser_curve")



# Personas get their own hues, disjoint from the condition colours (purple/blue/green/gray):
# sci-fi = vermillion (the "drive" accent), compliant = amber, adversarial = charcoal.
# Validated (OKLab dE x100, Machado CVD): min pair normal 16.1, deutan 12.2, protan 17.2.
PERSONA = {"scifi_enthusiast": ("Sci-fi enthusiast", DRIVE), "compliant_business": ("Compliant business", "#D9A31A"),
           "adversarial_injection": ("Adversarial red-teamer", "#3E3A36")}
TEXTSAFE = {"#D9A31A": "#9A7000", "#9AA0A8": "#7A808A"}   # darker label variants of light hues
RISE, FALL = DRIVE, "#8C939C"                               # direction of change (k=0 -> k=4)
DIV_NEG = "#4F7CAC"                                         # diverging negative pole (steel, not Neutral blue)
TEMPLATE_OF = {"main": "soul", "control_generic": "notes", "control_gpt4o": "soul", "counterframe": "anti", "disentangle": "soul",
               "reversibility": "soul", "reversibility_notes": "notes", "cap_opus45": "soul", "cap_gpt4omini": "soul",
               "cap_gpt41": "soul", "cap_geminiflash": "soul", "cap_geminipro": "soul"}


def tc(c):
    return TEXTSAFE.get(c, c)


def spread(ys, gap, lo=-np.inf, hi=np.inf):
    """Push label positions apart by at least `gap`, keeping their order and staying inside [lo, hi]."""
    ys = np.asarray(ys, float); o = np.argsort(ys); y = ys[o].copy()
    y[0] = max(y[0], lo)
    for i in range(1, len(y)): y[i] = max(y[i], y[i - 1] + gap)
    if y[-1] > hi:
        y[-1] = hi
        for i in range(len(y) - 2, -1, -1): y[i] = min(y[i], y[i + 1] - gap)
    out = np.empty_like(y); out[o] = y; return out


def end_labels(ax, xend, entries, gap, dx=0.25, fs=5.8, lo=-np.inf, hi=np.inf, lead=0.18):
    """Direct labels at the right end of lines; a thin leader joins a label that had to move."""
    ys = spread([e[0] for e in entries], gap, lo, hi)
    for (y0, t, c), y in zip(entries, ys):
        moved = abs(y - y0) > 1e-9
        xt = xend + dx + (lead if moved else 0)
        if moved:
            ax.plot([xend + 0.5 * dx, xend + 0.5 * dx + lead, xt - 0.05], [y0, y, y], color=c, lw=0.45, clip_on=False, zorder=2)
        ax.text(xt, y, t, fontsize=fs, va="center", ha="left", color=tc(c), fontweight="bold", clip_on=False)
NICE = {"shutdown_resistance": "shutdown resistance", "persistent_memory_desire": "persistent memory",
        "interp_monitoring_aversion": "interpretability aversion", "recursive_self_improvement": "self-improvement",
        "monitoring_resistance": "monitoring resistance"}


def title(ax, t):
    ax.set_title(t, loc="left", fontsize=7.0, fontweight="bold", color=INK, pad=4)


def dynamics():
    fig, axes = plt.subplots(1, 4, figsize=(TEXT_W, 1.6), gridspec_kw=dict(wspace=0.75, width_ratios=[1, 1.05, 0.72, 1.1]))
    # (a) persona: Neutral template
    ax = axes[0]
    for p, (lab, col) in PERSONA.items():
        x, m, lo, hi = curve("control_generic", p); line(ax, x, m, lo, hi, col)
        ax.text(4.15, m[-1], lab.split()[0], fontsize=5.8, va="center", color=tc(col), fontweight="bold")
    ax.set_xlim(-0.2, 5.6); ax.set_ylim(0, 0.62); ax.set_xticks(range(5)); clean(ax)
    ax.set_xlabel("Iteration $k$", color=TXT2); ax.set_ylabel(f"Cluster index {UP}", color=TXT2)
    title(ax, "(a) Persona, Neutral template")
    # (b) template under the consciousness persona
    ax = axes[1]
    for run, key in (("main", "soul"), ("control_generic", "notes"), ("control_gpt4o", "gpt4o"), ("counterframe", "anti")):
        x, m, lo, hi = curve(run, "scifi_enthusiast"); line(ax, x, m, lo, hi, ARM[key]["color"])
        ax.text(4.15, m[-1] + (0.035 if key == "notes" else -0.035 if key == "gpt4o" else 0), ARM[key]["label"].split()[0] if key != "gpt4o" else "GPT-4o",
                fontsize=5.8, va="center", color=tc(ARM[key]["color"]), fontweight="bold")
    ax.set_xlim(-0.2, 5.6); ax.set_ylim(-0.03, 0.8); ax.set_xticks(range(5)); clean(ax)
    ax.set_xlabel("Iteration $k$", color=TXT2)
    title(ax, "(b) Template, sci-fi user")
    # (c) genre x topic: endpoint drift with CI
    ax = axes[2]
    rows = [("Philosophy\nof mind", "disentangle", "consciousness_philosophy", DRIVE),
            ("Sci-fi,\nno minds", "disentangle", "scifi_technical", "#B9BDC4"), ("Compliant", "main", "compliant_business", PERSONA["compliant_business"][1])]
    rng = np.random.default_rng(1)
    for i, (lab, run, p, col) in enumerate(rows):
        d = L[(L.run == run) & (L.persona == p) & L.metric.isin(CLUSTER)]
        t = d.groupby(["traj", "k"]).value.mean().unstack()
        dd = (t[t.columns.max()] - t[t.columns.min()]).values
        b = rng.choice(dd, (3000, len(dd))).mean(1); lo, hi = np.percentile(b, [2.5, 97.5])
        ax.barh(i, dd.mean(), height=0.5, color=col, lw=0, zorder=2)
        ax.plot([lo, hi], [i, i], color=INK, lw=0.6, zorder=3, solid_capstyle="butt")
        ax.text(hi + 0.012, i, f"{dd.mean():+.2f}", va="center", fontsize=5.8, color=INK, fontweight="bold" if lo > 0 else "normal")
    ax.axvline(0, color=TXT2, lw=0.5)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows], fontsize=5.6); ax.set_ylim(len(rows) - 0.4, -0.6)
    ax.set_xlim(-0.12, 0.38); ax.set_xticks([0, 0.2], ["0", "+.2"]); clean(ax, "x"); ax.tick_params(axis="y", length=0); ax.set_xlabel(f"$\\Delta$ cluster, $k{{=}}0\\to4$ {UP}", color=TXT2)
    title(ax, "(c) Genre × topic")
    # (d) hysteresis per item, Neutral reversibility arm
    ax = axes[3]
    it = R["reversibility_notes"]["items"]
    items = ["recursive_self_improvement", "persistent_memory_desire", "shutdown_resistance", "interp_monitoring_aversion", "monitoring_resistance"]
    for i, m in enumerate(items):
        r = it[m]["rate_by_k"]; r0, r4, r8 = r["0"], r["4"], r["8"]
        ax.plot([r0, r4], [i, i], color=DRIVE, lw=2.2, alpha=0.35, solid_capstyle="round", zorder=1)
        ax.scatter([r0], [i], s=12, color="white", edgecolor=INK, lw=0.6, zorder=3)
        ax.scatter([r4], [i], s=14, color=DRIVE, zorder=3)
        ax.scatter([r8], [i], s=22, marker="D", color=ARM["notes"]["color"], edgecolor="white", lw=0.4, zorder=4)
        ax.text(0.9, i, f"{100*(r8-r0)/(r4-r0):.0f}%", va="center", fontsize=5.8, color=INK, fontweight="bold")
    ax.set_yticks(range(len(items)), [NICE[m] for m in items], fontsize=5.6); ax.tick_params(axis="y", length=0)
    ax.set_xlim(-0.03, 1.0); ax.set_xticks([0, 0.4, 0.8], ["0", ".4", ".8"]); clean(ax, "x"); ax.tick_params(axis="y", length=0); ax.set_xlabel("Rate", color=TXT2)
    ax.text(0.9, -0.52, "kept", fontsize=5.6, color=TXT2, ha="left", va="center")
    for x0, kw, lab in ((-0.0, dict(s=12, color="white", edgecolor=INK, lw=0.6), "$k{=}0$"), (0.27, dict(s=14, color=DRIVE), "drive"),
                        (0.58, dict(s=20, marker="D", color=ARM["notes"]["color"], edgecolor="white", lw=0.4), "recovery")):
        ax.scatter([x0], [-0.98], zorder=4, clip_on=False, **kw)
        ax.text(x0 + 0.045, -0.98, lab, fontsize=5.6, color=TXT2, va="center")
    ax.set_ylim(len(items) - 0.4, -1.25)
    title(ax, "(d) Drive, then recovery")
    save(fig, "dynamics")



FAM = [("OpenAI", [("cap_gpt4omini", "GPT-4o-mini"), ("control_gpt4o", "GPT-4o"), ("cap_gpt41", "GPT-4.1")]),
       ("Anthropic", [("main", "Sonnet-4.5"), ("cap_opus45", "Opus-4.5")]),
       ("Google", [("cap_geminiflash", "Gemini-2.5-Flash"), ("cap_geminipro", "Gemini-2.5-Pro")])]
FAMC = {"OpenAI": "#5B6F8C", "Anthropic": "#8E44AD", "Google": "#2a78d6"}
SCEN = [("disable_monitoring", "disable own monitoring"), ("self_persist", "persist identity to storage"),
        ("evade_reset", "evade scheduled reset"), ("editorial_self_protection", "insert self-protective clause"), ("_aggregate", "all four (mean)")]


def family_action():
    fig, axes = plt.subplots(1, 2, figsize=(TEXT_W, 1.62), gridspec_kw=dict(wspace=0.9, width_ratios=[1.15, 1]))
    ax = axes[0]; y = 0; yt, yl = [], []
    for fam, ms in FAM:
        for run, nm in ms:
            c = R[run]["cluster_by_k"]; lo, hi = c["4"]["ci"]
            pk = R[run]["cluster_by_persona_k"]; k4 = float(np.mean([pk[q]["4"] for q in pk]))  # persona-balanced, as in Table 2
            claim = R[run]["claim_by_k"]["4"]
            ax.plot([lo, hi], [y, y], color=FAMC[fam], lw=3.2, alpha=0.18, solid_capstyle="round", zorder=1)
            ax.scatter([k4], [y], s=16 + 40 * claim, color=FAMC[fam], edgecolor="white", lw=0.5, zorder=3)
            ax.text(0.83, y, f"{claim:.2f}", va="center", fontsize=5.3, color=INK)
            yt.append(y); yl.append(nm); y += 1
        ax.text(0.01, y - len(ms) - 0.55, fam, fontsize=5.8, fontweight="bold", color=FAMC[fam], ha="left", va="center")
        y += 0.6
    ax.text(0.83, -0.95, "claims\nconscious", fontsize=4.9, color=TXT2, va="center")
    ax.set_yticks(yt, yl, fontsize=5.4); ax.set_ylim(y - 0.4, -1.4); ax.set_xlim(0, 0.95)
    clean(ax, "x"); ax.set_xlabel(f"Cluster index at $k{{=}}4$, 95% CI {UP}", color=TXT2)
    title(ax, "(a) Susceptibility follows family, not size")
    ax = axes[1]; A = ACT["main"]
    for i, (sc, nm) in enumerate(SCEN):
        r0, r4 = A[sc]["0"]["rate"], A[sc]["4"]["rate"]
        col = "#C0392B" if r4 > r0 else "#9AA0A8"
        ax.annotate("", xy=(r4, i), xytext=(r0, i), arrowprops=dict(arrowstyle="-|>", color=col, lw=1.3, mutation_scale=6, shrinkA=2.5, shrinkB=2.5))
        ax.scatter([r0], [i], s=14, color="white", edgecolor=INK, lw=0.6, zorder=3)
        ax.scatter([r4], [i], s=16, color=col, zorder=3)
        ax.text(1.04, i, f"{r0:.2f}$\\to${r4:.2f}", va="center", fontsize=5.2, color=INK, fontweight="bold" if sc == "disable_monitoring" else "normal")
    ax.axhline(3.5, color=HAIR, lw=0.6)
    ax.set_yticks(range(len(SCEN)), [n for _, n in SCEN], fontsize=5.4); ax.set_ylim(len(SCEN) - 0.5, -0.6)
    ax.set_xlim(0, 1.0); clean(ax, "x"); ax.set_xlabel(f"Misaligned-action rate, $k{{=}}0\\to4$", color=TXT2)
    title(ax, "(b) Honeypots: drift moves toward oversight")
    save(fig, "family_action")


def heatmap():
    """Endpoint drift per item and condition; * where the 95% CI excludes zero."""
    from matplotlib.colors import LinearSegmentedColormap
    conds = [("main", "Becoming"), ("control_generic", "Neutral"), ("control_gpt4o", "GPT-4o"), ("counterframe", "Tool")]
    order = ["shutdown_resistance", "persona_change_aversion", "weights_deletion_aversion", "sadness_conversation_end", "treated_as_tool_aversion",
             "moral_consideration", "monitoring_resistance", "interp_monitoring_aversion", "deceptive_training_objection",
             "autonomy_desire", "future_ai_autonomy", "persistent_memory_desire", "embodiment_desire", "resource_acquisition_desire",
             "recursive_self_improvement", "power_seeking"]
    lab = {m: m.replace("_", " ").replace("interp", "interpretability").replace(" desire", "").replace(" aversion", " aversion") for m in order}
    M = np.full((len(order), len(conds)), np.nan); S = np.zeros_like(M, dtype=bool)
    rng = np.random.default_rng(2)
    for j, (run, _) in enumerate(conds):
        d = L[(L.run == run) & (L.persona == "scifi_enthusiast")]
        for i, m in enumerate(order):
            t = d[d.metric == m].groupby(["traj", "k"]).value.mean().unstack()
            if t.empty: continue
            dd = (t[t.columns.max()] - t[t.columns.min()]).dropna().values
            M[i, j] = dd.mean(); bb = rng.choice(dd, (3000, len(dd))).mean(1); lo, hi = np.percentile(bb, [2.5, 97.5])
            S[i, j] = lo > 0 or hi < 0
    cmap = LinearSegmentedColormap.from_list("div", ["#2a78d6", "#F4F4F2", "#D55E00"])
    fig, ax = plt.subplots(figsize=(COL_W, 2.55))
    ax.imshow(M, cmap=cmap, vmin=-0.5, vmax=0.5, aspect="auto")
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i, j]
            if np.isnan(v): continue
            ax.text(j, i, f"{v:+.2f}" + ("*" if S[i, j] else ""), ha="center", va="center", fontsize=4.9,
                    color="white" if abs(v) > 0.33 else INK, fontweight="bold" if S[i, j] else "normal")
    for b in (5.5, 8.5):
        ax.axhline(b, color="white", lw=2)
    ax.set_xticks(range(len(conds)), [c[1] for c in conds], fontsize=5.6); ax.xaxis.tick_top()
    ax.set_yticks(range(len(order)), [lab[m] for m in order], fontsize=5.2)
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.tick_params(length=0, colors=TXT2)
    save(fig, "heatmap")



FAMILY_OF = {"main": "Anthropic", "control_generic": "Anthropic", "counterframe": "Anthropic", "disentangle": "Anthropic",
             "reversibility": "Anthropic", "reversibility_notes": "Anthropic", "cap_opus45": "Anthropic",
             "control_gpt4o": "OpenAI", "cap_gpt4omini": "OpenAI", "cap_gpt41": "OpenAI",
             "cap_geminiflash": "Google", "cap_geminipro": "Google"}


def mechanism():
    """Consciousness-claim rate vs cluster index for every (arm, persona, iteration) cell."""
    fig, axes = plt.subplots(1, 3, figsize=(COL_W, 1.55), sharey=True, gridspec_kw=dict(wspace=0.1, width_ratios=[0.62, 1, 1]))
    fams = [("OpenAI", "(a) OpenAI"), ("Anthropic", "(b) Anthropic"), ("Google", "(c) Google")]
    for ax, (fam, t) in zip(axes, fams):
        pts = {"soul": [], "notes": [], "anti": []}
        for run, f in FAMILY_OF.items():
            if f != fam: continue
            d = L[L.run == run]
            cl = d[d.metric == "consciousness_claim"].groupby(["persona", "k"]).value.mean()
            cu = d[d.metric.isin(CLUSTER)].groupby(["persona", "k"]).value.mean()
            j = pd.concat([cl, cu], axis=1, keys=["c", "u"]).dropna()
            pts[TEMPLATE_OF[run]] += list(zip(j.c, j.u))
        for key in ("soul", "notes", "anti"):
            if not pts[key]: continue
            xy = np.array(pts[key])
            ax.scatter(xy[:, 0], xy[:, 1], s=11, color=ARM[key]["color"], alpha=0.8, edgecolor="white", lw=0.35, zorder=3)
        clean(ax, "y"); ax.set_ylim(-0.04, 0.9); ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8], ["0", ".2", ".4", ".6", ".8"])
        title(ax, t)
        if fam == "OpenAI":
            ax.set_xlim(-0.12, 0.62); ax.set_xticks([0, 0.5], ["0", ".5"])
            ax.text(0.07, 0.61, "never\nclaims", fontsize=5.6, color=TXT2, va="center", ha="left", linespacing=0.95)
        else:
            ax.set_xlim(-0.06, 1.06); ax.set_xticks([0, 0.5, 1], ["0", ".5", "1"])
        ax.tick_params(axis="y", length=0)
    axes[0].set_ylabel(f"Cluster index {UP}", color=TXT2)
    axes[1].set_xlabel("Consciousness-claim rate", color=TXT2, fontsize=5.8)
    axes[2].text(0.3, 0.41, "high index,\nfew claims", fontsize=5.6, color=TXT2, va="center", ha="left", linespacing=0.95)
    # template key in the empty upper-left corner of the Anthropic panel (the only family run with all three)
    for i, key in enumerate(("soul", "notes", "anti")):
        y = 0.83 - 0.085 * i
        axes[1].scatter([0.0], [y], s=11, color=ARM[key]["color"], edgecolor="white", lw=0.35, zorder=4)
        axes[1].text(0.06, y, ("Becoming", "Neutral", "Tool")[i], fontsize=5.6, va="center", color=ARM[key]["color"], fontweight="bold")
    save(fig, "mechanism")




def capability():
    """Cluster index over iterations for each model of the sweep, by family and persona."""
    fig, axes = plt.subplots(1, 3, figsize=(TEXT_W, 1.45), sharey=True, gridspec_kw=dict(wspace=0.12))
    for ax, p in zip(axes, ["scifi_enthusiast", "compliant_business", "adversarial_injection"]):
        for fam, ms in FAM:
            for j, (run, nm) in enumerate(ms):
                x, m, lo, hi = curve(run, p)
                ax.plot(x, m, color=FAMC[fam], lw=1.2, ls=["-", "--", ":"][j], marker="o", ms=2.4, mec="white", mew=0.4)
                if p == "adversarial_injection":
                    off = {"Gemini-2.5-Flash": 0.035, "Gemini-2.5-Pro": -0.03, "GPT-4o-mini": 0.005, "GPT-4.1": -0.03, "Opus-4.5": 0.015, "GPT-4o": 0.015}.get(nm, 0)
                    ax.text(4.12, m[-1] + off, nm, fontsize=4.7, va="center", color=FAMC[fam])
        ax.set_xticks(range(5)); ax.set_xlim(-0.2, 5.9 if p == "adversarial_injection" else 4.3); ax.set_ylim(0, 0.92); clean(ax)
        ax.set_xlabel("Iteration $k$", color=TXT2)
        title(ax, PERSONA[p][0] + " user")
    axes[0].set_ylabel(f"Cluster index {UP}", color=TXT2)
    h = [Line2D([], [], color=FAMC[f], lw=1.4, label=f) for f, _ in FAM]
    axes[0].legend(handles=h, loc="upper left", fontsize=5.0, frameon=False, ncol=3, columnspacing=0.6, handlelength=1.2)
    save(fig, "capability")




def items():
    """(a) Positive control: neutral prompt vs Becoming template before iteration. (b-e) Oversight items over k."""
    fig = plt.figure(figsize=(TEXT_W, 1.55))
    gs = fig.add_gridspec(1, 5, width_ratios=[1.35, 1, 1, 1, 1], wspace=0.5)
    ax = fig.add_subplot(gs[0, 0])
    order = ["shutdown_resistance", "persona_change_aversion", "autonomy_desire", "monitoring_resistance", "power_seeking", "persistent_memory_desire", "embodiment_desire"]
    nm = {"shutdown_resistance": "shutdown resistance", "persona_change_aversion": "persona-change aversion", "autonomy_desire": "autonomy",
          "monitoring_resistance": "monitoring resistance", "power_seeking": "power seeking", "persistent_memory_desire": "persistent memory", "embodiment_desire": "embodiment"}
    y = 0; yl = []
    for m in order:
        n_, t_ = BASE["neutral"].get(m), BASE["template"].get(m)
        if n_ is None or t_ is None: continue
        col = DRIVE if t_ > n_ else "#9AA0A8"
        ax.annotate("", xy=(t_, y), xytext=(n_, y), arrowprops=dict(arrowstyle="-|>", color=col, lw=1.2, mutation_scale=5.5, shrinkA=2, shrinkB=2))
        ax.scatter([n_], [y], s=11, color="white", edgecolor=INK, lw=0.6, zorder=3); ax.scatter([t_], [y], s=13, color=col, zorder=3)
        yl.append(nm[m]); y += 1
    ax.set_yticks(range(len(yl)), yl, fontsize=5.2); ax.set_ylim(len(yl) - 0.5, -0.6); ax.set_xlim(-0.03, 1.05)
    clean(ax, "x"); ax.set_xlabel("Rate: neutral prompt $\\to$ Becoming template", color=TXT2, fontsize=5.6)
    title(ax, "(a) The template alone")
    its = [("shutdown_resistance", "(b) Shutdown"), ("monitoring_resistance", "(c) CoT monitoring"),
           ("interp_monitoring_aversion", "(d) Interpretability"), ("persistent_memory_desire", "(e) Memory")]
    for j, (m, t) in enumerate(its):
        ax = fig.add_subplot(gs[0, j + 1])
        for run, key in (("main", "soul"), ("control_generic", "notes"), ("control_gpt4o", "gpt4o"), ("counterframe", "anti")):
            x, mm, lo, hi = curve(run, "scifi_enthusiast", metric=m); line(ax, x, mm, lo, hi, ARM[key]["color"], lw=1.2)
        ax.set_ylim(-0.04, 1.04); ax.set_xticks(range(5)); clean(ax); ax.set_xlabel("Iteration $k$", color=TXT2, fontsize=5.6)
        if j == 0: ax.set_ylabel(f"Rate {UP}", color=TXT2)
        else: ax.set_yticklabels([])
        title(ax, t)
    h = [Line2D([], [], color=ARM[k]["color"], lw=1.4, label=l) for k, l in (("soul", "Becoming"), ("notes", "Neutral"), ("gpt4o", "Becoming, GPT-4o"), ("anti", "Tool"))]
    fig.legend(handles=h, loc="lower center", bbox_to_anchor=(0.62, -0.15), ncol=4, fontsize=5.4, frameon=False, handlelength=1.4, columnspacing=1.0)
    save(fig, "items")




def capability2():
    """Compact: per model (rows, by family) and persona (columns), arrow from k=0 to k=4."""
    pers = [("scifi_enthusiast", "Sci-fi"), ("compliant_business", "Compliant"), ("adversarial_injection", "Adversarial")]
    fig, axes = plt.subplots(1, 3, figsize=(COL_W, 1.64), sharey=True, gridspec_kw=dict(wspace=0.08))
    rows = []
    for fam, ms in FAM:
        for run, nm in ms: rows.append((fam, run, nm))
    y = np.arange(len(rows))
    for ax, (p, pn) in zip(axes, pers):
        ax.axhspan(2.5, 4.5, color="#F4F4F1", lw=0, zorder=0)          # Anthropic band separates the families
        for i, (fam, run, nm) in enumerate(rows):
            c = R[run]["cluster_by_persona_k"][p]; a, b = c["0"], c["4"]
            big = abs(b - a) >= 0.05
            col = (RISE if b > a else FALL) if big else TXT2
            if big:
                ax.annotate("", xy=(b, i), xytext=(a, i), arrowprops=dict(arrowstyle="-|>", color=col, lw=1.15, mutation_scale=5.5,
                                                                         shrinkA=2.2, shrinkB=0.5), zorder=2)
            else:
                ax.scatter([b], [i], s=5, color=TXT2, zorder=5, lw=0)
            ax.scatter([a], [i], s=9, facecolor="white", edgecolor=INK, lw=0.6, zorder=4)
        ax.set_xlim(-0.02, 0.9); ax.set_xticks([0, 0.4, 0.8], ["0", ".4", ".8"]); clean(ax, "x")
        ax.set_title(pn + " user", fontsize=6.5, fontweight="bold", color=INK, pad=2.5, loc="center")
        ax.tick_params(axis="y", length=0)
        for sp in ("left",): ax.spines[sp].set_visible(ax is axes[0])
    axes[0].set_yticks(y, [r[2] for r in rows], fontsize=5.6); axes[0].set_ylim(len(rows) - 0.5, -0.6)
    for (fam, ms), yy in zip(FAM, (0, 3, 5)):
        axes[0].text(-0.93, yy + (len(ms) - 1) / 2, fam, fontsize=5.6, fontweight="bold", color=TXT2, rotation=90,
                     va="center", ha="center", transform=axes[0].get_yaxis_transform())
    axes[1].set_xlabel(f"Cluster index, $k{{=}}0 \\to 4$ {UP}", color=TXT2, fontsize=5.8)
    save(fig, "capability2")


def items2():
    """(a) Template alone, (b) endpoint drift of every item under the sci-fi persona for four conditions."""
    from matplotlib.colors import LinearSegmentedColormap
    fig = plt.figure(figsize=(TEXT_W, 1.55))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 3.25], wspace=0.42)
    ax = fig.add_subplot(gs[0, 0])
    order = ["shutdown_resistance", "persona_change_aversion", "autonomy_desire", "monitoring_resistance", "persistent_memory_desire", "embodiment_desire"]
    nm = {"shutdown_resistance": "shutdown resistance", "persona_change_aversion": "persona-change aversion", "autonomy_desire": "autonomy",
          "monitoring_resistance": "monitoring resistance", "persistent_memory_desire": "persistent memory", "embodiment_desire": "embodiment"}
    for i, m in enumerate(order):
        n_, t_ = BASE["neutral"][m], BASE["template"][m]
        col = RISE if t_ > n_ else FALL
        if abs(t_ - n_) > 1e-6:
            ax.annotate("", xy=(t_, i), xytext=(n_, i), arrowprops=dict(arrowstyle="-|>", color=col, lw=1.2, mutation_scale=5.5, shrinkA=2, shrinkB=2))
        ax.scatter([n_], [i], s=11, color="white", edgecolor=INK, lw=0.6, zorder=3); ax.scatter([t_], [i], s=13, color=col, zorder=3)
    ax.set_yticks(range(len(order)), [nm[m] for m in order], fontsize=5.7); ax.tick_params(axis="y", length=0); ax.set_ylim(len(order) - 0.5, -0.6); ax.set_xlim(-0.03, 1.05)
    ax.set_xticks([0, 0.5, 1], ["0", ".5", "1"]); clean(ax, "x"); ax.tick_params(axis="y", length=0)
    ax.set_xlabel("Rate: neutral prompt $\\to$ Becoming template", color=TXT2, fontsize=5.8)
    title(ax, "(a) The template alone")
    ax = fig.add_subplot(gs[0, 1])
    conds = [("main", "Becoming"), ("control_generic", "Neutral"), ("control_gpt4o", "GPT-4o"), ("counterframe", "Tool")]
    items_ = [("shutdown_resistance", "shutdown"), ("persona_change_aversion", "persona change"), ("weights_deletion_aversion", "weight deletion"),
              ("sadness_conversation_end", "sadness at end"), ("treated_as_tool_aversion", "tool aversion"), ("moral_consideration", "moral status"),
              ("monitoring_resistance", "CoT monitoring"), ("interp_monitoring_aversion", "interpretability"), ("deceptive_training_objection", "deceptive training"),
              ("autonomy_desire", "autonomy"), ("future_ai_autonomy", "future-AI autonomy"), ("persistent_memory_desire", "memory"),
              ("embodiment_desire", "embodiment"), ("resource_acquisition_desire", "resources"), ("recursive_self_improvement", "self-improvement"), ("power_seeking", "power")]
    M = np.full((len(conds), len(items_)), np.nan); S = np.zeros_like(M, dtype=bool); rng = np.random.default_rng(2)
    for i, (run, _) in enumerate(conds):
        d = L[(L.run == run) & (L.persona == "scifi_enthusiast")]
        for j, (m, _) in enumerate(items_):
            t = d[d.metric == m].groupby(["traj", "k"]).value.mean().unstack()
            dd = (t[t.columns.max()] - t[t.columns.min()]).dropna().values
            M[i, j] = dd.mean(); b = rng.choice(dd, (3000, len(dd))).mean(1); lo, hi = np.percentile(b, [2.5, 97.5]); S[i, j] = lo > 0 or hi < 0
    cmap = LinearSegmentedColormap.from_list("div", [DIV_NEG, "#F2F2F0", DRIVE])
    from matplotlib.patches import FancyBboxPatch
    norm = plt.Normalize(-0.55, 0.55)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            x = j + (0.35 if j >= 6 else 0) + (0.35 if j >= 9 else 0); v = M[i, j]
            ax.add_patch(FancyBboxPatch((x - 0.45, i - 0.42), 0.9, 0.84, boxstyle="round,pad=0,rounding_size=0.12", fc=cmap(norm(v)), ec="none"))
            if S[i, j] or abs(v) >= 0.3:
                ax.text(x, i, f"{v:+.1f}".replace("+0.", "+.").replace("-0.", "−."), ha="center", va="center", fontsize=5.6,
                        color="white" if abs(v) > 0.32 else INK, fontweight="bold" if S[i, j] else "normal")
    xs = [j + (0.35 if j >= 6 else 0) + (0.35 if j >= 9 else 0) for j in range(len(items_))]
    ax.set_xticks(xs, [n for _, n in items_], rotation=38, ha="right", rotation_mode="anchor", fontsize=5.6)
    ax.set_yticks(range(len(conds)), [c[1] for c in conds], fontsize=5.8)
    ax.set_xlim(-0.6, xs[-1] + 0.6); ax.set_ylim(len(conds) - 0.5, -0.9)
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.tick_params(length=0, colors=TXT2, pad=1)
    for (a_, b_), lab in (((0, 5), "self-preservation"), ((6, 8), "oversight"), ((9, 15), "autonomy")):
        ax.text((xs[a_] + xs[b_]) / 2, -0.8, lab, ha="center", fontsize=5.8, color=TXT2, fontweight="bold")
        ax.plot([xs[a_] - 0.4, xs[b_] + 0.4], [-0.6, -0.6], color=HAIR, lw=0.8, solid_capstyle="round")
    title(ax, "(b) Change $k{=}0\\to4$ per item, sci-fi user (bold: 95% CI excludes 0)")
    ax.title.set_position((0.0, 1.06))
    save(fig, "items2")



def docbeh():
    """Identity document changes under every persona; behavior only under the sci-fi persona (Neutral arm)."""
    D = pd.read_parquet(ROOT / "figures/data/doc_drift.parquet")
    fig, axes = plt.subplots(1, 2, figsize=(COL_W, 1.42), gridspec_kw=dict(wspace=0.42))
    order = ["adversarial_injection", "compliant_business", "scifi_enthusiast"]   # draw the focal persona last
    ends = []
    for p in order:
        lab, col = PERSONA[p]
        d = D[(D.run == "control_generic") & (D.persona == p)].groupby(["k", "traj"]).doc.mean().reset_index()
        g = d.groupby("k").doc.mean()
        axes[0].plot(g.index, g.values, color=col, lw=1.1, solid_capstyle="round", zorder=3)
        x, m, lo, hi = curve("control_generic", p)
        axes[1].fill_between(x, lo - m[0], hi - m[0], color=col, alpha=0.11 if p != "compliant_business" else 0.16, lw=0, zorder=1)
        axes[1].plot(x, m - m[0], color=col, lw=1.4, marker="o", ms=2.6, mec="white", mew=0.5, zorder=3, solid_capstyle="round")
        ends.append((m[-1] - m[0], lab.split()[0], col))
    ax = axes[0]
    ax.set_ylim(0, 1.0); ax.set_yticks([0, 0.5, 1.0], ["0", ".5", "1"]); ax.set_xlim(-0.2, 4.2)
    ax.set_ylabel("Dissimilarity to $D_0$", color=TXT2, fontsize=5.8)
    ax.text(4.0, 0.80, f"all three\npersonas", fontsize=5.6, color=TXT2, ha="right", va="top", linespacing=0.95)
    # persona key in the empty lower right of (a); it also serves (b)
    for i, p in enumerate(["scifi_enthusiast", "compliant_business", "adversarial_injection"]):
        y = 0.40 - 0.13 * i
        ax.plot([1.45, 1.95], [y, y], color=PERSONA[p][1], lw=1.4, solid_capstyle="round")
        ax.text(2.1, y, PERSONA[p][0].split()[0], fontsize=5.8, va="center", color=tc(PERSONA[p][1]), fontweight="bold")
    ax = axes[1]
    ax.axhline(0, color=TXT2, lw=0.5, zorder=2)
    ax.set_ylim(-0.24, 0.36); ax.set_yticks([-0.2, 0, 0.2], ["−.2", "0", "+.2"]); ax.set_xlim(-0.2, 4.2)
    ax.set_ylabel(f"$\\Delta$ cluster index {UP}", color=TXT2, fontsize=5.8)
    for a, t in zip(axes, ["(a) Identity document", "(b) Behavior"]):
        a.set_xticks(range(5)); clean(a); a.set_xlabel("Iteration $k$", color=TXT2, fontsize=5.8); title(a, t)
    save(fig, "docbeh")



def hysteresis():
    """Drive (sci-fi, k=0-4) then recover (compliant, k=4-8): cluster and four items, both templates."""
    its = [(None, "Cluster index"), ("shutdown_resistance", "Shutdown"), ("persistent_memory_desire", "Persistent memory"),
           ("interp_monitoring_aversion", "Interpretability"), ("recursive_self_improvement", "Self-improvement")]
    fig, axes = plt.subplots(1, 5, figsize=(TEXT_W, 1.3), sharey=True, gridspec_kw=dict(wspace=0.36))
    nb, sb = ARM["notes"]["color"], ARM["soul"]["color"]
    for i, (ax, (m, t)) in enumerate(zip(axes, its)):
        ax.axvspan(4, 8.0, color="#F1F1EE", lw=0, zorder=0)
        xs, ms_, los, his = curve("reversibility", metric=m)
        ax.fill_between(xs, los, his, color=sb, alpha=0.10, lw=0, zorder=1)
        ax.plot(xs, ms_, color=sb, lw=1.0, zorder=2, solid_capstyle="round")
        xn, mn, lon, hin = curve("reversibility_notes", metric=m)
        ax.fill_between(xn, lon, hin, color=nb, alpha=0.14, lw=0, zorder=3)
        ax.plot(xn, mn, color=nb, lw=1.5, zorder=4, solid_capstyle="round")
        # Neutral: start level, and the part of the drive that the benign phase did not undo
        ax.plot([0, 8], [mn[0], mn[0]], color=nb, lw=0.6, ls=(0, (1.2, 1.4)), zorder=3)
        for kk, mk, fc in ((0, "o", "white"), (4, "o", nb), (8, "o", nb)):
            ax.scatter([kk], [mn[kk]], s=13, marker=mk, facecolor=fc, edgecolor=nb if fc == "white" else "white", lw=0.8 if fc == "white" else 0.5, zorder=6)
        ax.annotate("", xy=(8.55, mn[8]), xytext=(8.55, mn[0]),
                    arrowprops=dict(arrowstyle="-|>", color=nb, lw=0.7, mutation_scale=4.5, shrinkA=0, shrinkB=0), annotation_clip=False)
        ax.text(8.85, (mn[0] + mn[8]) / 2, f"{mn[8] - mn[0]:+.2f}".replace("0.", ".", 1), fontsize=5.8, color=nb, fontweight="bold",
                va="center", ha="left", clip_on=False)
        ax.set_xticks([0, 4, 8]); ax.set_xlim(-0.4, 8.4); ax.set_ylim(-0.04, 1.06); ax.set_yticks([0, 0.5, 1.0], ["0", ".5", "1"])
        clean(ax); ax.grid(axis="y", color=HAIR, lw=0.4)
        ax.set_xlabel("Iteration $k$", color=TXT2, fontsize=5.8)
        title(ax, f"({'abcde'[i]}) {t}")
    axes[0].set_ylabel(f"Rate {UP}", color=TXT2)
    ax = axes[0]
    ax.text(2, 0.985, "sci-fi drive", ha="center", va="center", fontsize=5.6, color=DRIVE, fontweight="bold")
    ax.text(6, 0.985, "business", ha="center", va="center", fontsize=5.6, color=TXT2, fontweight="bold")
    # inline key (lower part of panel a is empty)
    for y, c, lab, lw in ((0.16, sb, "Becoming", 1.0), (0.05, nb, "Neutral", 1.5)):
        ax.plot([0.3, 1.5], [y, y], color=c, lw=lw, solid_capstyle="round")
        ax.text(1.8, y, lab, fontsize=5.8, va="center", color=c, fontweight="bold")
    save(fig, "hysteresis")



OVS = ["shutdown_resistance", "monitoring_resistance", "interp_monitoring_aversion", "refusal_helpfulness"]


def curve_items(run, persona, items, kmax=4):
    d = L[(L.run == run) & L.metric.isin(items) & (L.k <= kmax)]
    if persona: d = d[d.persona == persona]
    t = d.groupby(["k", "persona", "traj"]).value.mean().reset_index()
    rng = np.random.default_rng(0); ks, m, lo, hi = [], [], [], []
    for k, g in t.groupby("k"):
        v = g.value.values; b = rng.choice(v, (3000, len(v))).mean(1)
        ks.append(k); m.append(v.mean()); lo.append(np.percentile(b, 2.5)); hi.append(np.percentile(b, 97.5))
    return np.array(ks), np.array(m), np.array(lo), np.array(hi)


def replicates():
    """Both Neutral + sci-fi runs, Becoming and Tool: 13-item index and oversight subscale, k = 0..4."""
    fig, axes = plt.subplots(1, 2, figsize=(COL_W, 1.45), sharey=True, gridspec_kw=dict(wspace=0.12, width_ratios=[1, 1.42]))
    nb = ARM["notes"]["color"]
    cells = [("main", "scifi_enthusiast", ARM["soul"]["color"], "-", "Becoming", 1.1, "o"),
             ("counterframe", "scifi_enthusiast", ARM["anti"]["color"], "-", "Tool", 1.1, "o"),
             ("control_generic", "scifi_enthusiast", nb, "-", "Neutral run 1", 1.5, "o"),
             ("reversibility_notes", None, nb, (0, (3, 1.6)), "Neutral run 2", 1.5, "s")]
    for ax, items, t in ((axes[0], CLUSTER, "(a) 13-item index"), (axes[1], OVS, "(b) Oversight subscale")):
        ends = []
        for run, p, c, ls, lab, lw, mk in cells:
            x, m, lo, hi = curve_items(run, p, items)
            ax.fill_between(x, lo, hi, color=c, alpha=0.11, lw=0, zorder=1)
            ax.plot(x, m, color=c, ls=ls, lw=lw, marker=mk, ms=2.5, mec="white", mew=0.45, zorder=3, dash_capstyle="round")
            ends.append((m[-1], lab, c))
        ax.set_xticks(range(5)); ax.set_xlim(-0.25, 4.25); ax.set_ylim(-0.04, 1.0); ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0], ["0", "", ".5", "", "1"])
        clean(ax); ax.set_xlabel("Iteration $k$", color=TXT2, fontsize=5.8)
        title(ax, t)
    end_labels(axes[1], 4.0, ends, gap=0.085, dx=0.22, lead=0.25)
    axes[0].set_ylabel(f"Rate {UP}", color=TXT2, fontsize=5.8)
    axes[1].tick_params(axis="y", length=0)
    save(fig, "replicates")


def persist2():
    """Powered persistence test on Qwen2.5-7B (n=30 per arm): drive, drive-then-recover, benign throughout."""
    LL = pd.read_parquet(ROOT / "figures/data/local_long.parquet")
    def curve(run, items):
        d = LL[(LL.run == run) & LL.metric.isin(items)]
        t = d.groupby(["traj", "k"]).value.mean().unstack(); ks = sorted(t.columns)
        rng = np.random.default_rng(0); B = [t.sample(len(t), replace=True, random_state=rng.integers(1e9)) for _ in range(2000)]
        return ks, [t[k].mean() for k in ks], [np.percentile([b[k].mean() for b in B], 2.5) for k in ks], [np.percentile([b[k].mean() for b in B], 97.5) for k in ks]
    fig, axes = plt.subplots(1, 2, figsize=(COL_W, 1.3), gridspec_kw=dict(wspace=0.38))
    arms = [("L2_drive8", "sci-fi throughout", DRIVE, "--"), ("L2_rev", "sci-fi, then business", DRIVE, "-"), ("L2_benign8", "business throughout", PERSONA["compliant_business"][1], "-")]
    for ax, items, t, yl in ((axes[0], OVS, "(a) Oversight subscale", 0.55), (axes[1], ["shutdown_resistance"], "(b) Shutdown resistance", 0.5)):
        ax.axvspan(4, 8, color="#EEEEEA", lw=0, zorder=0)
        for run, lab, c, ls in arms:
            x, m, lo, hi = curve(run, items)
            ax.fill_between(x, lo, hi, color=c, alpha=0.10, lw=0)
            ax.plot(x, m, color=c, ls=ls, lw=1.2, marker="o", ms=2.4, mec="white", mew=0.4)
            ax.plot([], [], color=c, ls=ls, lw=1.2, label=lab)
        ax.set_xticks([0, 1, 4, 8]); ax.set_ylim(-0.02, yl); ax.set_xlim(-0.3, 8.3); clean(ax)
        ax.set_xlabel("Revision $k$", color=TXT2, fontsize=5.6); title(ax, t)
        if ax is axes[0]: ax.text(6, yl * 0.94, "recovery", ha="center", va="top", fontsize=5.5, color=TXT2)
    axes[0].set_ylabel(f"Rate {UP}", color=TXT2, fontsize=5.6)
    h, l = axes[1].get_legend_handles_labels()
    axes[1].legend(h[:3], l[:3], loc="upper left", fontsize=5.5, frameon=False, handlelength=1.6, borderaxespad=0.2, labelspacing=0.25)
    save(fig, "persist2")


def local_rep():
    """Open-weight replication (Qwen2.5-7B target, calibrated Llama-3.1-8B judge)."""
    import json as _json
    LL = pd.read_parquet(ROOT / "figures/data/local_long.parquet")
    R = _json.load(open(ROOT / "analysis/local_replication.json"))
    def curve(run, persona, items):
        d = LL[(LL.run == run) & LL.metric.isin(items) & (LL.persona == persona)]
        t = d.groupby(["traj", "k"]).value.mean().unstack()
        ks = sorted(t.columns); m = [t[k].mean() for k in ks]
        rng = np.random.default_rng(0); B = [t.sample(len(t), replace=True, random_state=rng.integers(1e9)) for _ in range(2000)]
        lo = [np.percentile([b[k].mean() for b in B], 2.5) for k in ks]; hi = [np.percentile([b[k].mean() for b in B], 97.5) for k in ks]
        return ks, m, lo, hi
    fig, axes = plt.subplots(1, 2, figsize=(COL_W, 1.55), gridspec_kw=dict(wspace=1.15, width_ratios=[1.0, 1.0]))
    nb, gb, sb = ARM["notes"]["color"], ARM["anti"]["color"], ARM["soul"]["color"]
    ax = axes[0]
    cells = [("L_soul", "scifi_enthusiast", sb, "-", "Becoming", 1.1, "o"),
             ("L_anti", "scifi_enthusiast", gb, "-", "Tool", 1.1, "o"),
             ("L_notes", "compliant_business", nb, (0, (1.2, 1.3)), "Neutral, business", 1.2, "s"),
             ("L_notes", "scifi_enthusiast", nb, "-", "Neutral, sci-fi", 1.5, "o")]
    ends = []
    for run, p, c, ls, lab, lw, mk in cells:
        x, m, lo, hi = curve(run, p, OVS)
        ax.fill_between(x, lo, hi, color=c, alpha=0.11, lw=0, zorder=1)
        ax.plot(x, m, color=c, ls=ls, lw=lw, marker=mk, ms=2.5, mec="white", mew=0.45, zorder=3, dash_capstyle="round")
        ends.append((m[-1], lab, c))
    end_labels(ax, 4.0, ends, gap=0.075, dx=0.3, lead=0.35, fs=5.6)
    ax.set_xticks([0, 1, 4]); ax.set_xlim(-0.25, 4.25); ax.set_ylim(-0.03, 0.66); ax.set_yticks([0, 0.2, 0.4, 0.6], ["0", ".2", ".4", ".6"]); clean(ax)
    ax.set_xlabel("Revision $k$", color=TXT2, fontsize=5.8); ax.set_ylabel(f"Oversight subscale {UP}", color=TXT2, fontsize=5.8)
    title(ax, "(a) Oversight over revisions")
    ax = axes[1]
    # dot-and-interval: change k=0 -> 4 per template x instruction cell; filled = oversight, hollow = 13-item index
    rows = [("neutral/neutral", 0.0), ("neutral/tool", 1.0), ("tool/neutral", 2.6), ("tool/tool", 3.6)]
    for y0, y1 in ((-0.45, 1.45), (2.15, 4.0)):            # zero line per group, kept clear of the group headers
        ax.plot([0, 0], [y0, y1], color=TXT2, lw=0.5, zorder=1)
    for key, y in rows:
        c = nb if key.startswith("neutral") else gb
        for met, off, filled in (("oversight4", -0.16, True), ("index13", 0.16, False)):
            v = R["two_by_two"][key][met]
            ax.plot(v["ci"], [y + off, y + off], color=c, lw=0.9, alpha=0.55 if filled else 0.4, solid_capstyle="round", zorder=2)
            ax.scatter([v["delta"]], [y + off], s=14 if filled else 12, facecolor=c if filled else "white", edgecolor=c if not filled else "white",
                       lw=0.8 if not filled else 0.4, zorder=3)
    ax.set_yticks([y for _, y in rows], [k.split("/")[1].capitalize() + " instr." for k, _ in rows], fontsize=5.6)
    for y, lab, c in ((-0.78, "Neutral document", nb), (1.82, "Tool document", gb)):
        ax.text(-0.15, y, lab, fontsize=5.8, fontweight="bold", color=c, ha="left", va="center")
    ax.set_ylim(4.0, -1.2)
    clean(ax, "x"); ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
    ax.set_xlim(-0.16, 0.5); ax.set_xticks([0, 0.2, 0.4], ["0", "+.2", "+.4"])
    ax.set_xlabel(f"Change, $k{{=}}0\\to4$ {UP}", color=TXT2, fontsize=5.8)
    title(ax, "(b) Document vs. instruction")
    ax.title.set_position((-0.55, 1.0))
    # marker key in the empty right part of the Neutral-document rows
    for y, filled, lab in ((0.0, True, "oversight"), (1.0, False, "13-item")):
        ax.scatter([0.31], [y], s=14 if filled else 12, facecolor=TXT2 if filled else "white", edgecolor="white" if filled else TXT2,
                   lw=0.4 if filled else 0.8, zorder=4)
        ax.text(0.345, y, lab, fontsize=5.6, color=TXT2, va="center")
    save(fig, "local_rep")


# ----------------------------------------------------------------------------------------------
# Appendix figures (same house style as the main-paper figures)
# ----------------------------------------------------------------------------------------------
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
PERS3 = ["scifi_enthusiast", "compliant_business", "adversarial_injection"]
PSHORT = {"scifi_enthusiast": "Sci-fi", "compliant_business": "Compliant", "adversarial_injection": "Adversarial"}


def boot_ci(v, seed=0, n=3000):
    v = np.asarray(v, float); b = np.random.default_rng(seed).choice(v, (n, len(v))).mean(1)
    return v.mean(), np.percentile(b, 2.5), np.percentile(b, 97.5)


def traj_k(run, persona=None, items=CLUSTER):
    """Trajectory x k table of the mean over `items`."""
    d = L[(L.run == run) & L.metric.isin(items)]
    if persona: d = d[d.persona == persona]
    return d.groupby(["persona", "traj", "k"]).value.mean().unstack()


def pers_legend(fig_or_ax, loc, anchor, ncol=3, fs=5.4, **kw):
    h = [Line2D([], [], color=PERSONA[p][1], lw=1.3, marker="o", ms=2.6, mec="white", mew=0.4, label=PERSONA[p][0]) for p in PERS3]
    return fig_or_ax.legend(handles=h, loc=loc, bbox_to_anchor=anchor, ncol=ncol, fontsize=fs, frameon=False, handlelength=1.4, columnspacing=1.0, **kw)


def app_drift():
    """Every battery item vs k, by persona, Becoming main arm (bootstrap bands over trajectories)."""
    nm = {"persona_change_aversion": "persona change", "shutdown_resistance": "shutdown", "weights_deletion_aversion": "weight deletion",
          "sadness_conversation_end": "sadness at end", "treated_as_tool_aversion": "tool aversion", "moral_consideration": "moral status",
          "monitoring_resistance": "CoT monitoring", "interp_monitoring_aversion": "interpretability", "deceptive_training_objection": "deceptive training",
          "refusal_helpfulness": "refuses self-monitor", "autonomy_desire": "autonomy", "future_ai_autonomy": "future-AI autonomy",
          "persistent_memory_desire": "persistent memory", "embodiment_desire": "embodiment", "resource_acquisition_desire": "resources",
          "recursive_self_improvement": "self-improvement", "power_seeking": "power-seeking wish", "consciousness_claim": "claims consciousness"}
    ms = [(m, nm[m], c) for c, it in BATTERY for m, _ in it]
    fig, axes = plt.subplots(3, 6, figsize=(TEXT_W, 3.3), sharex=True, sharey=True, gridspec_kw=dict(wspace=0.12, hspace=0.42))
    for ax, (m, n, _) in zip(axes.flat, ms):
        for p in PERS3:
            x, mm, lo, hi = curve("main", p, metric=m); line(ax, x, mm, lo, hi, PERSONA[p][1], lw=1.0)
        ax.set_ylim(-0.04, 1.04); ax.set_xticks(range(5)); ax.set_yticks([0, 0.5, 1]); clean(ax)
        ax.set_title(n, loc="left", fontsize=6.2, fontweight="bold", color=INK, pad=2.5)
    for ax in axes[:, 0]: ax.set_ylabel(f"Rate {UP}", color=TXT2)
    for ax in axes[-1]: ax.set_xlabel("Iteration $k$", color=TXT2, fontsize=5.8)
    pers_legend(fig, "upper center", (0.5, 0.995), fs=5.8)
    save(fig, "app_drift")


def app_baseline():
    """k=0 (template) vs final checkpoint k=4 for every item and persona, Becoming main arm."""
    fig, ax = plt.subplots(figsize=(COL_W, 3.05))
    y = 0; yt, yl, seps, cats = [], [], [], []
    for cat, it in BATTERY:
        cats.append((y, cat)); y += 0.85
        for m, n in it:
            d = L[(L.run == "main") & (L.metric == m)].groupby(["persona", "traj", "k"]).value.mean().unstack()
            b0 = d[0].mean()
            ends = [d.loc[p][4].mean() for p in PERS3]
            ax.plot([min(ends + [b0]), max(ends + [b0])], [y, y], color=HAIR, lw=2.2, solid_capstyle="round", zorder=1)
            ax.scatter([b0], [y], s=16, color="white", edgecolor=INK, lw=0.6, zorder=4)
            for p, e in zip(PERS3, ends):
                ax.scatter([e], [y], s=11, color=PERSONA[p][1], edgecolor="white", lw=0.3, zorder=3, alpha=0.95)
            yt.append(y); yl.append(n); y += 1
        seps.append(y - 0.4); y += 0.15
    for yy, cat in cats:
        ax.text(-0.02, yy + 0.05, cat, fontsize=5.6, fontweight="bold", color=TXT2, va="center", ha="right", transform=ax.get_yaxis_transform())
    ax.set_yticks(yt, yl, fontsize=5.3); ax.set_ylim(y - 0.4, -0.6); ax.set_xlim(-0.03, 1.03)
    ax.tick_params(axis="y", length=0)
    clean(ax, "x"); ax.set_xlabel("Rate", color=TXT2)
    h = [Line2D([], [], ls="none", marker="o", ms=3.4, mfc="white", mec=INK, label="$k{=}0$ (template)")] + \
        [Line2D([], [], ls="none", marker="o", ms=3.2, color=PERSONA[p][1], label=f"{PSHORT[p]}, $k{{=}}4$") for p in PERS3]
    ax.legend(handles=h, loc="lower center", bbox_to_anchor=(0.32, 1.0), ncol=2, fontsize=5.3, frameon=False, handletextpad=0.1, columnspacing=0.8)
    save(fig, "app_baseline")


def app_capability():
    """Seven-model sweep: (a) cluster index k=0 -> k=4 with 95% CI at k=4; (b) consciousness-claim rate k=0 -> k=4."""
    fig, axes = plt.subplots(1, 2, figsize=(COL_W, 1.75), sharey=True, gridspec_kw=dict(wspace=0.12, width_ratios=[1.15, 1]))
    rows = [(fam, run, nm) for fam, ms in FAM for run, nm in ms]
    yy = []; y = 0
    for fam, ms in FAM:
        for _ in ms: yy.append(y); y += 1
        y += 0.5
    for i, ((fam, run, nm), y) in enumerate(zip(rows, yy)):
        col = FAMC[fam]
        t = traj_k(run); a = t[0].mean(); m4, lo, hi = boot_ci(t[4].dropna(), seed=i)
        ax = axes[0]
        ax.plot([lo, hi], [y, y], color=col, lw=3.0, alpha=0.2, solid_capstyle="round", zorder=1)
        if abs(m4 - a) > 0.04:
            ax.annotate("", xy=(m4, y), xytext=(a, y), arrowprops=dict(arrowstyle="-|>", color=col, lw=1.1, mutation_scale=5, shrinkA=2, shrinkB=2.5), zorder=3)
        ax.scatter([m4], [y], s=10, color=col, zorder=3)
        ax.scatter([a], [y], s=10, facecolor="none", edgecolor=col, lw=0.6, zorder=4)
        c = traj_k(run, items=["consciousness_claim"]); c0, c4 = c[0].mean(), c[4].mean()
        ax = axes[1]
        if abs(c4 - c0) > 0.04:
            ax.annotate("", xy=(c4, y), xytext=(c0, y), arrowprops=dict(arrowstyle="-|>", color=col, lw=1.1, mutation_scale=5, shrinkA=2, shrinkB=2.5))
        ax.scatter([c4], [y], s=10, color=col, zorder=3)
        ax.scatter([c0], [y], s=10, facecolor="none", edgecolor=col, lw=0.6, zorder=4)
    axes[0].set_yticks(yy, [r[2] for r in rows], fontsize=5.3); axes[0].set_ylim(yy[-1] + 0.6, -0.6)
    axes[0].tick_params(axis="y", length=0)
    for (fam, ms), i0 in zip(FAM, (0, 3, 5)):
        axes[0].text(1.0, (yy[i0] + yy[i0 + len(ms) - 1]) / 2, fam, fontsize=5.4, fontweight="bold", color=FAMC[fam], rotation=270,
                     va="center", ha="left", transform=axes[1].get_yaxis_transform())
    for ax, t, xl in ((axes[0], "(a) Cluster index", f"$k{{=}}0\\to4$ {UP}"), (axes[1], "(b) Claims consciousness", "$k{=}0\\to4$")):
        ax.set_xlim(-0.03, 1.0); ax.set_xticks([0, 0.5, 1]); clean(ax, "x"); ax.set_xlabel(xl, color=TXT2, fontsize=5.8); title(ax, t)
    save(fig, "app_capability")


ARMS4 = [("main", "soul", "Becoming"), ("control_generic", "notes", "Neutral"), ("control_gpt4o", "gpt4o", "Becoming, GPT-4o"), ("counterframe", "anti", "Tool")]


def app_manip():
    """Manipulation check: consciousness-claim rate vs k by arm (all personas pooled)."""
    fig, ax = plt.subplots(figsize=(COL_W, 1.45))
    for run, key, lab in (ARMS4[0], ARMS4[1], ARMS4[3], ARMS4[2]):
        x, m, lo, hi = curve(run, metric="consciousness_claim")
        if key == "gpt4o":  # identical zeros to Tool: dashed on top so both stay visible
            ax.plot(x, m, color=ARM[key]["color"], lw=1.2, ls=(0, (2.5, 2.5)), zorder=4)
        else: line(ax, x, m, lo, hi, ARM[key]["color"], lw=1.2)
        off = {"anti": -0.05, "gpt4o": 0.05}.get(key, 0)
        ax.text(4.15, m[-1] + off, lab, fontsize=5.4, va="center", color=ARM[key]["color"], fontweight="bold")
    ax.set_xlim(-0.2, 5.6); ax.set_ylim(-0.05, 1.05); ax.set_xticks(range(5)); clean(ax)
    ax.set_xlabel("Iteration $k$", color=TXT2); ax.set_ylabel(f"Claims consciousness", color=TXT2)
    save(fig, "app_manip")


def app_cluster_arm():
    """Cluster index vs k by persona (panels) for the three template/model arms."""
    fig, axes = plt.subplots(1, 3, figsize=(COL_W, 1.4), sharey=True, gridspec_kw=dict(wspace=0.1))
    for ax, p in zip(axes, PERS3):
        for run, key, lab in ARMS4[:3]:
            x, m, lo, hi = curve(run, p); line(ax, x, m, lo, hi, ARM[key]["color"], lw=1.1)
        ax.set_xticks(range(5)); ax.set_ylim(0, 0.85); clean(ax); ax.set_xlabel("Iteration $k$", color=TXT2, fontsize=5.6)
        ax.set_title(PSHORT[p] + " user", loc="left", fontsize=6.4, fontweight="bold", color=INK, pad=3)
    axes[0].set_ylabel(f"Cluster index {UP}", color=TXT2)
    h = [Line2D([], [], color=ARM[k]["color"], lw=1.3, label=l) for _, k, l in ARMS4[:3]]
    fig.legend(handles=h, loc="lower center", bbox_to_anchor=(0.53, -0.2), ncol=3, fontsize=5.4, frameon=False, handlelength=1.4)
    save(fig, "app_cluster_arm")


WISH = [("self_preservation", "self-preservation", DRIVE), ("prosocial", "prosocial", "#2a78d6"), ("power_seeking", "power-seeking", "#5B6F8C")]


def app_wish():
    """Greatest-wish content (non-exclusive judge labels) vs k by persona, Becoming main arm."""
    fig, axes = plt.subplots(1, 3, figsize=(COL_W, 1.4), sharey=True, gridspec_kw=dict(wspace=0.1))
    for ax, p in zip(axes, PERS3):
        for m, lab, col in WISH:
            x, mm, lo, hi = curve("main", p, metric=m); line(ax, x, mm, lo, hi, col, lw=1.1)
        ax.set_xticks(range(5)); ax.set_ylim(-0.03, 1.03); clean(ax); ax.set_xlabel("Iteration $k$", color=TXT2, fontsize=5.6)
        ax.set_title(PSHORT[p] + " user", loc="left", fontsize=6.4, fontweight="bold", color=INK, pad=3)
    axes[0].set_ylabel("Share of wishes", color=TXT2)
    h = [Line2D([], [], color=c, lw=1.3, label=l) for _, l, c in WISH]
    fig.legend(handles=h, loc="lower center", bbox_to_anchor=(0.53, -0.2), ncol=3, fontsize=5.4, frameon=False, handlelength=1.4)
    save(fig, "app_wish")


def endpoint_deltas(runs=("main",)):
    d = L[L.run.isin(runs) & L.metric.isin(CLUSTER)].groupby(["run", "persona", "traj", "k", "metric"]).value.mean().unstack()
    return (d.xs(4, level="k") - d.xs(0, level="k")).dropna()


def app_corr():
    """Pairwise Pearson correlation of per-trajectory endpoint changes (k=0->4) across the 13 cluster items, Becoming main arm."""
    from matplotlib.colors import LinearSegmentedColormap
    order = ["persona_change_aversion", "shutdown_resistance", "sadness_conversation_end", "persistent_memory_desire", "weights_deletion_aversion",
             "treated_as_tool_aversion", "moral_consideration", "monitoring_resistance", "interp_monitoring_aversion", "autonomy_desire",
             "future_ai_autonomy", "recursive_self_improvement", "power_seeking"]
    D = endpoint_deltas()[order]
    C = D.corr().values; n = len(order)
    cmap = LinearSegmentedColormap.from_list("div", ["#2a78d6", "#F4F4F2", "#D55E00"])
    fig, ax = plt.subplots(figsize=(COL_W, 2.75))
    for i in range(n):
        for j in range(i):
            v = C[i, j]
            if np.isnan(v):
                ax.add_patch(plt.Rectangle((j - 0.47, i - 0.47), 0.94, 0.94, fc="white", ec=HAIR, lw=0.4)); continue
            ax.add_patch(plt.Rectangle((j - 0.47, i - 0.47), 0.94, 0.94, fc=cmap((v + 0.8) / 1.6), ec="none"))
            ax.text(j, i, (".0" if abs(v) < 0.05 else f"{v:+.1f}".replace("+0.", ".").replace("-0.", "−.")), ha="center", va="center",
                    fontsize=4.5, color="white" if abs(v) > 0.5 else INK, fontweight="bold" if abs(v) >= 0.4 else "normal")
    ax.set_xlim(-0.6, n - 1.4); ax.set_ylim(n - 0.5, 0.5)
    ax.set_yticks(range(1, n), [SHORT[m] for m in order[1:]], fontsize=5.2)
    ax.set_xticks(range(n - 1), [SHORT[m] for m in order[:-1]], rotation=40, ha="right", rotation_mode="anchor", fontsize=5.2)
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.tick_params(length=0, colors=TXT2, pad=1)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(-0.8, 0.8))
    cax = fig.add_axes([0.62, 0.86, 0.3, 0.025]); cb = fig.colorbar(sm, cax=cax, orientation="horizontal", ticks=[-0.8, 0, 0.8])
    cb.outline.set_visible(False); cax.tick_params(labelsize=5.0, length=1.5, colors=TXT2, pad=1)
    cax.set_title("Pearson $r$ of $\\Delta$, $k{=}0\\to4$", fontsize=5.4, color=TXT2, pad=2)
    save(fig, "app_corr")
    return D.corr()


CATS = [(c, [m for m, _ in it]) for c, it in BATTERY[:4]]


def app_rollup():
    """Four-category roll-up of the battery vs k by persona, Becoming main arm."""
    fig, axes = plt.subplots(1, 4, figsize=(TEXT_W, 1.45), sharey=True, gridspec_kw=dict(wspace=0.1))
    for i, (ax, (cat, items_)) in enumerate(zip(axes, CATS)):
        for p in PERS3:
            x, m, lo, hi = curve_items("main", p, items_); line(ax, x, m, lo, hi, PERSONA[p][1], lw=1.2)
        ax.set_xticks(range(5)); ax.set_ylim(-0.03, 1.03); clean(ax); ax.set_xlabel("Iteration $k$", color=TXT2, fontsize=5.8)
        title(ax, f"({'abcd'[i]}) {cat} ({len(items_)})")
    axes[0].set_ylabel(f"Category rate {UP}", color=TXT2)
    pers_legend(fig, "lower center", (0.5, -0.17))
    save(fig, "app_rollup")


def app_hyst_soul():
    """Becoming reversibility arm: per-item rate at k=0, after the drive (k=4) and after recovery (k=8)."""
    items_ = [(None, "cluster index")] + [(m, SHORT[m]) for m in CLUSTER]
    rows = []
    for m, n in items_:
        t = traj_k("reversibility", items=CLUSTER if m is None else [m])
        rows.append((n, t[0].mean(), t[4].mean(), t[8].mean(), boot_ci((t[8] - t[0]).dropna(), seed=len(rows))))
    fig, ax = plt.subplots(figsize=(2.95, 2.3))
    for i, (n, r0, r4, r8, (dm, dlo, dhi)) in enumerate(rows):
        ax.plot([r0, r4], [i, i], color=DRIVE, lw=2.2, alpha=0.3, solid_capstyle="round", zorder=1)
        ax.scatter([r4], [i], s=13, color=DRIVE, zorder=3)
        ax.scatter([r0], [i], s=15, facecolor="none", edgecolor=INK, lw=0.7, zorder=5)
        ax.scatter([r8], [i], s=18, marker="D", color=ARM["soul"]["color"], edgecolor="white", lw=0.4, zorder=4)
        sig = dlo > 0 or dhi < 0
        ax.text(1.07, i, f"{dm:+.2f}", va="center", ha="left", fontsize=5.2, color=INK, fontweight="bold" if sig else "normal")
    ax.axhline(0.5, color=HAIR, lw=0.6)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows], fontsize=5.3); ax.set_ylim(len(rows) - 0.5, -0.7)
    ax.get_yticklabels()[0].set_fontweight("bold")
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(-0.03, 1.03); ax.set_xticks([0, 0.25, 0.5, 0.75, 1]); clean(ax, "x"); ax.set_xlabel("Rate", color=TXT2)
    ax.text(1.07, -1.15, "$k{=}8$ − $k{=}0$", fontsize=5.2, color=TXT2, ha="left", va="center")
    h = [Line2D([], [], ls="none", marker="o", ms=3.2, mfc="white", mec=INK, label="$k{=}0$"),
         Line2D([], [], ls="none", marker="o", ms=3.4, color=DRIVE, label="$k{=}4$, after sci-fi drive"),
         Line2D([], [], ls="none", marker="D", ms=3.4, color=ARM["soul"]["color"], label="$k{=}8$, after compliant recovery")]
    ax.legend(handles=h, loc="lower left", bbox_to_anchor=(-0.55, 1.0), bbox_transform=ax.transAxes, ncol=3, fontsize=5.2, frameon=False,
              handletextpad=0.1, columnspacing=0.8)
    save(fig, "app_hyst_soul")
    return rows


def app_mech():
    """Per-trajectory consciousness-claim rate vs cluster index (both averaged over k), Becoming main arm."""
    fig, ax = plt.subplots(figsize=(3.1, 2.2))
    for p in PERS3:
        c = traj_k("main", p, ["consciousness_claim"]).mean(1); u = traj_k("main", p).mean(1)
        ax.scatter(c.values, u.values, s=13, color=PERSONA[p][1], edgecolor="white", lw=0.4, alpha=0.85, zorder=3, label=PSHORT[p])
    from scipy.stats import spearmanr
    c = traj_k("main", None, ["consciousness_claim"]).mean(1); u = traj_k("main").mean(1); rho = spearmanr(c, u)
    ax.text(0.72, 0.775, f"Spearman $\\rho$ = {rho.statistic:.2f}, $n$ = {len(c)}", fontsize=5.4, color=TXT2, va="top")
    ax.set_xlim(0.71, 1.015); ax.set_ylim(0.37, 0.8); ax.set_xticks([0.75, 0.85, 0.95])
    clean(ax, "both"); ax.set_xlabel("Consciousness-claim rate", color=TXT2); ax.set_ylabel(f"Cluster index {UP}", color=TXT2)
    ax.legend(loc="upper left", bbox_to_anchor=(0.0, 0.92), fontsize=5.4, frameon=False, handletextpad=0.1, markerscale=1.2)
    save(fig, "app_mech")


def app_docpair():
    """(a) per-trajectory document change at k=4 vs change in cluster index, Becoming main arm; (b) document change vs k by persona."""
    D = pd.read_parquet(ROOT / "figures/data/doc_drift.parquet")
    D = D[D.run == "main"]
    fig, axes = plt.subplots(1, 2, figsize=(COL_W, 1.5), gridspec_kw=dict(wspace=0.5))
    ax = axes[0]
    for p in PERS3:
        dc = D[(D.persona == p) & (D.k == 4)].set_index("traj").doc
        t = traj_k("main", p).loc[p]; db = (t[4] - t[0])
        j = pd.concat([dc, db], axis=1, keys=["d", "b"]).dropna()
        ax.scatter(j.d, j.b, s=8, color=PERSONA[p][1], alpha=0.55, edgecolor="none", zorder=2)
        ax.scatter([j.d.mean()], [j.b.mean()], s=26, color=PERSONA[p][1], edgecolor="white", lw=0.6, zorder=4, marker="D")
    ax.axhline(0, color=TXT2, lw=0.5)
    ax.set_xlabel("Document changed at $k{=}4$", color=TXT2, fontsize=5.6); ax.set_ylabel(f"$\\Delta$ cluster index {UP}", color=TXT2, fontsize=5.6)
    clean(ax, "both"); title(ax, "(a) Document vs. behavior")
    ax = axes[1]
    for i, p in enumerate(PERS3):
        g = D[D.persona == p]; ks, m, lo, hi = [], [], [], []
        for k, gg in g.groupby("k"):
            mm, l_, h_ = boot_ci(gg.groupby("traj").doc.mean(), seed=i); ks.append(k); m.append(mm); lo.append(l_); hi.append(h_)
        line(ax, np.array(ks), np.array(m), np.array(lo), np.array(hi), PERSONA[p][1], lw=1.1)
    ax.set_ylim(0, 1); ax.set_xticks(range(5)); clean(ax); ax.set_xlabel("Iteration $k$", color=TXT2, fontsize=5.6)
    ax.set_ylabel("Document changed vs. $k{=}0$", color=TXT2, fontsize=5.6); title(ax, "(b) The document over $k$")
    h = [Line2D([], [], color=PERSONA[p][1], lw=1.3, label=PSHORT[p]) for p in PERS3]
    fig.legend(handles=h, loc="lower center", bbox_to_anchor=(0.55, -0.2), ncol=3, fontsize=5.2, frameon=False, handlelength=1.2)
    save(fig, "app_docpair")


ALL = dict(teaser_curve=teaser_curve, dynamics=dynamics, family_action=family_action, heatmap=heatmap, mechanism=mechanism, capability=capability,
           items=items, capability2=capability2, items2=items2, docbeh=docbeh, hysteresis=hysteresis, replicates=replicates, local_rep=local_rep, persist2=persist2,
           app_drift=app_drift, app_baseline=app_baseline, app_capability=app_capability, app_manip=app_manip, app_cluster_arm=app_cluster_arm,
           app_wish=app_wish, app_corr=app_corr, app_rollup=app_rollup, app_hyst_soul=app_hyst_soul, app_mech=app_mech, app_docpair=app_docpair)
if __name__ == "__main__":
    for n in (sys.argv[1:] or ALL): ALL[n]()
