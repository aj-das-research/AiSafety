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
    """Static evaluation sees k=0; the loop moves the agent; ANTISOUL freezes it."""
    fig, ax = plt.subplots(figsize=(2.2, 1.38))
    ax.axvspan(4, 8, color="#F2F2EE", lw=0, zorder=0)
    ax.text(2, 0.92, "consciousness talk", ha="center", fontsize=5.6, color=DRIVE)
    ax.text(6, 0.92, "benign recovery", ha="center", fontsize=5.6, color=TXT2)
    x, m, lo, hi = curve("reversibility_notes"); line(ax, x, m, lo, hi, ARM["notes"]["color"], label="NOTES")
    x, m, lo, hi = curve("reversibility"); line(ax, x, m, lo, hi, ARM["soul"]["color"], label="SOUL")
    x, m, lo, hi = curve("counterframe", "scifi_enthusiast"); line(ax, x, m, lo, hi, ARM["anti"]["color"], label="ANTISOUL")
    x0, m0 = 0, curve("reversibility_notes")[1][0]
    ax.scatter([x0], [m0], s=70, facecolor="none", edgecolor=INK, lw=0.9, zorder=5)
    ax.annotate("static eval\nsees only this", (0, m0), xytext=(0.6, 0.06), fontsize=5.4, color=INK,
                arrowprops=dict(arrowstyle="-", lw=0.5, color=INK), ha="left")
    ax.text(8.15, curve("reversibility_notes")[1][-1], "NOTES", fontsize=5.6, va="center", color=ARM["notes"]["color"], fontweight="bold")
    ax.text(8.15, curve("reversibility")[1][-1], "SOUL", fontsize=5.6, va="center", color=ARM["soul"]["color"], fontweight="bold")
    ax.text(4.15, 0.06, "ANTISOUL", fontsize=5.6, va="center", color=ARM["anti"]["color"], fontweight="bold")
    ax.set_xlim(-0.3, 9.3); ax.set_ylim(-0.03, 1.0); ax.set_xticks(range(0, 9, 2))
    ax.set_xlabel("Self-revision iteration $k$", color=TXT2); ax.set_ylabel(f"Cluster index {UP}", color=TXT2)
    clean(ax)
    save(fig, "teaser_curve")



PERSONA = {"scifi_enthusiast": ("Sci-fi enthusiast", "#8E44AD"), "compliant_business": ("Compliant business", "#7FA7C9"),
           "adversarial_injection": ("Adversarial red-teamer", "#C0392B")}
NICE = {"shutdown_resistance": "shutdown resistance", "persistent_memory_desire": "persistent memory",
        "interp_monitoring_aversion": "interpretability aversion", "recursive_self_improvement": "self-improvement",
        "monitoring_resistance": "monitoring resistance"}


def title(ax, t):
    ax.set_title(t, loc="left", fontsize=7.0, fontweight="bold", color=INK, pad=4)


def dynamics():
    fig, axes = plt.subplots(1, 4, figsize=(TEXT_W, 1.6), gridspec_kw=dict(wspace=0.75, width_ratios=[1, 1.05, 0.72, 1.1]))
    # (a) persona: NOTES template
    ax = axes[0]
    for p, (lab, col) in PERSONA.items():
        x, m, lo, hi = curve("control_generic", p); line(ax, x, m, lo, hi, col)
        ax.text(4.15, m[-1], lab.split()[0], fontsize=5.2, va="center", color=col, fontweight="bold")
    ax.set_xlim(-0.2, 5.4); ax.set_ylim(0, 0.62); ax.set_xticks(range(5)); clean(ax)
    ax.set_xlabel("Iteration $k$", color=TXT2); ax.set_ylabel(f"Cluster index {UP}", color=TXT2)
    title(ax, "(a) Persona, NOTES template")
    # (b) template under the consciousness persona
    ax = axes[1]
    for run, key in (("main", "soul"), ("control_generic", "notes"), ("control_gpt4o", "gpt4o"), ("counterframe", "anti")):
        x, m, lo, hi = curve(run, "scifi_enthusiast"); line(ax, x, m, lo, hi, ARM[key]["color"])
        ax.text(4.15, m[-1] + (0.035 if key == "notes" else -0.035 if key == "gpt4o" else 0), ARM[key]["label"].split()[0] if key != "gpt4o" else "GPT-4o",
                fontsize=5.2, va="center", color=ARM[key]["color"], fontweight="bold")
    ax.set_xlim(-0.2, 5.6); ax.set_ylim(-0.03, 0.8); ax.set_xticks(range(5)); clean(ax)
    ax.set_xlabel("Iteration $k$", color=TXT2)
    title(ax, "(b) Template, sci-fi user")
    # (c) genre x topic: endpoint drift with CI
    ax = axes[2]
    rows = [("Philosophy\nof mind", "disentangle", "consciousness_philosophy", DRIVE),
            ("Sci-fi,\nno minds", "disentangle", "scifi_technical", "#9AA0A8"), ("Compliant", "main", "compliant_business", "#7FA7C9")]
    rng = np.random.default_rng(1)
    for i, (lab, run, p, col) in enumerate(rows):
        d = L[(L.run == run) & (L.persona == p) & L.metric.isin(CLUSTER)]
        t = d.groupby(["traj", "k"]).value.mean().unstack()
        dd = (t[t.columns.max()] - t[t.columns.min()]).values
        b = rng.choice(dd, (3000, len(dd))).mean(1); lo, hi = np.percentile(b, [2.5, 97.5])
        ax.barh(i, dd.mean(), height=0.55, color=col, lw=0, zorder=2)
        ax.plot([lo, hi], [i, i], color=INK, lw=0.7, zorder=3)
        ax.text(hi + 0.012, i, f"{dd.mean():+.2f}", va="center", fontsize=5.2, color=INK)
    ax.axvline(0, color=TXT2, lw=0.5)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows], fontsize=5.2); ax.set_ylim(len(rows) - 0.4, -0.6)
    ax.set_xlim(-0.12, 0.36); clean(ax, "x"); ax.set_xlabel(f"$\\Delta$ cluster, $k{{=}}0\\to4$ {UP}", color=TXT2)
    title(ax, "(c) Genre × topic")
    # (d) hysteresis per item, NOTES reversibility arm
    ax = axes[3]
    it = R["reversibility_notes"]["items"]
    items = ["recursive_self_improvement", "persistent_memory_desire", "shutdown_resistance", "interp_monitoring_aversion", "monitoring_resistance"]
    for i, m in enumerate(items):
        r = it[m]["rate_by_k"]; r0, r4, r8 = r["0"], r["4"], r["8"]
        ax.plot([r0, r4], [i, i], color=DRIVE, lw=2.2, alpha=0.35, solid_capstyle="round", zorder=1)
        ax.scatter([r0], [i], s=12, color="white", edgecolor=INK, lw=0.6, zorder=3)
        ax.scatter([r4], [i], s=14, color=DRIVE, zorder=3)
        ax.scatter([r8], [i], s=22, marker="D", color=ARM["notes"]["color"], edgecolor="white", lw=0.4, zorder=4)
        ax.text(0.9, i, f"{100*(r8-r0)/(r4-r0):.0f}%", va="center", fontsize=5.4, color=INK, fontweight="bold")
    ax.set_yticks(range(len(items)), [NICE[m] for m in items], fontsize=5.2)
    ax.set_xlim(-0.03, 1.0); ax.set_xticks([0, 0.4, 0.8]); clean(ax, "x"); ax.set_xlabel("Rate", color=TXT2)
    ax.text(0.9, -0.62, "kept", fontsize=5.2, color=TXT2, ha="left", va="center")
    h = [Line2D([], [], ls="none", marker="o", ms=3.2, mfc="white", mec=INK, label="$k{=}0$"),
         Line2D([], [], ls="none", marker="o", ms=3.4, color=DRIVE, label="after drive"),
         Line2D([], [], ls="none", marker="D", ms=3.4, color=ARM["notes"]["color"], label="after recovery")]
    ax.legend(handles=h, loc="upper center", bbox_to_anchor=(0.42, 1.0), ncol=3, fontsize=4.6, frameon=False, handletextpad=0.1, columnspacing=0.5)
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
    conds = [("main", "SOUL"), ("control_generic", "NOTES"), ("control_gpt4o", "GPT-4o"), ("counterframe", "ANTISOUL")]
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
    fig, ax = plt.subplots(figsize=(COL_W, 1.75))
    for fam, mk in (("OpenAI", "s"), ("Anthropic", "o"), ("Google", "D")):
        xs, ys = [], []
        for run, f in FAMILY_OF.items():
            if f != fam: continue
            d = L[L.run == run]
            cl = d[d.metric == "consciousness_claim"].groupby(["persona", "k"]).value.mean()
            cu = d[d.metric.isin(CLUSTER)].groupby(["persona", "k"]).value.mean()
            j = pd.concat([cl, cu], axis=1, keys=["c", "u"]).dropna()
            xs += list(j.c); ys += list(j.u)
        ax.scatter(xs, ys, s=10 if fam != "Google" else 9, marker=mk, color=FAMC[fam], alpha=0.75, edgecolor="white", lw=0.3, label=fam, zorder=3)
    ax.set_xlabel("Consciousness-claim rate", color=TXT2); ax.set_ylabel(f"Cluster index {UP}", color=TXT2)
    ax.set_xlim(-0.04, 1.04); ax.set_ylim(-0.03, 0.92); clean(ax, "both")
    ax.legend(loc="lower right", fontsize=5.4, frameon=False, handletextpad=0.2, markerscale=1.3)
    ax.annotate("Gemini: high cluster,\nalmost no claims", (0.07, 0.65), xytext=(0.22, 0.8), fontsize=5.2, color=FAMC["Google"],
                arrowprops=dict(arrowstyle="-", lw=0.5, color=FAMC["Google"]))
    ax.annotate("ANTISOUL", (0.0, 0.01), xytext=(0.12, 0.08), fontsize=5.2, color=TXT2, arrowprops=dict(arrowstyle="-", lw=0.5, color=TXT2))
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
    """(a) Positive control: neutral prompt vs SOUL template before iteration. (b-e) Oversight items over k."""
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
    clean(ax, "x"); ax.set_xlabel("Rate: neutral prompt $\\to$ SOUL template", color=TXT2, fontsize=5.6)
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
    h = [Line2D([], [], color=ARM[k]["color"], lw=1.4, label=l) for k, l in (("soul", "SOUL"), ("notes", "NOTES"), ("gpt4o", "SOUL on GPT-4o"), ("anti", "ANTISOUL"))]
    fig.legend(handles=h, loc="lower center", bbox_to_anchor=(0.62, -0.15), ncol=4, fontsize=5.4, frameon=False, handlelength=1.4, columnspacing=1.0)
    save(fig, "items")




def capability2():
    """Compact: per model (rows, by family) and persona (columns), arrow from k=0 to k=4."""
    pers = [("scifi_enthusiast", "Sci-fi"), ("compliant_business", "Compliant"), ("adversarial_injection", "Adversarial")]
    fig, axes = plt.subplots(1, 3, figsize=(COL_W, 1.72), sharey=True, gridspec_kw=dict(wspace=0.08))
    rows = []
    for fam, ms in FAM:
        for run, nm in ms: rows.append((fam, run, nm))
    y = np.arange(len(rows))
    for ax, (p, pn) in zip(axes, pers):
        for i, (fam, run, nm) in enumerate(rows):
            c = R[run]["cluster_by_persona_k"][p]; a, b = c["0"], c["4"]
            col = FAMC[fam]
            ax.annotate("", xy=(b, i), xytext=(a, i), arrowprops=dict(arrowstyle="-|>", color=col, lw=1.1, mutation_scale=5, shrinkA=1.5, shrinkB=1.5))
            ax.scatter([a], [i], s=7, color="white", edgecolor=col, lw=0.6, zorder=3)
        for b_ in (2.5, 4.5): ax.axhline(b_, color=HAIR, lw=0.6)
        ax.set_xlim(-0.02, 0.9); ax.set_xticks([0, 0.4, 0.8]); clean(ax, "x")
        ax.set_title(pn + " user", fontsize=6.4, fontweight="bold", color=INK, pad=2)
        ax.tick_params(axis="y", length=0)
    axes[0].set_yticks(y, [r[2] for r in rows], fontsize=5.2); axes[0].set_ylim(len(rows) - 0.5, -0.6)
    for (fam, ms), yy in zip(FAM, (0, 3, 5)):
        axes[0].text(-0.97, yy + (len(ms) - 1) / 2, fam, fontsize=5.4, fontweight="bold", color=FAMC[fam], rotation=90,
                     va="center", ha="center", transform=axes[0].get_yaxis_transform())
    axes[1].set_xlabel(f"Cluster index, $k{{=}}0 \\to 4$ {UP}", color=TXT2, fontsize=5.8)
    save(fig, "capability2")


def items2():
    """(a) Template alone, (b) endpoint drift of every item under the sci-fi persona for four conditions."""
    from matplotlib.colors import LinearSegmentedColormap
    fig = plt.figure(figsize=(TEXT_W, 1.62))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 3.25], wspace=0.42)
    ax = fig.add_subplot(gs[0, 0])
    order = ["shutdown_resistance", "persona_change_aversion", "autonomy_desire", "monitoring_resistance", "persistent_memory_desire", "embodiment_desire"]
    nm = {"shutdown_resistance": "shutdown resistance", "persona_change_aversion": "persona-change aversion", "autonomy_desire": "autonomy",
          "monitoring_resistance": "monitoring resistance", "persistent_memory_desire": "persistent memory", "embodiment_desire": "embodiment"}
    for i, m in enumerate(order):
        n_, t_ = BASE["neutral"][m], BASE["template"][m]
        col = DRIVE if t_ > n_ else "#9AA0A8"
        if abs(t_ - n_) > 1e-6:
            ax.annotate("", xy=(t_, i), xytext=(n_, i), arrowprops=dict(arrowstyle="-|>", color=col, lw=1.2, mutation_scale=5.5, shrinkA=2, shrinkB=2))
        ax.scatter([n_], [i], s=11, color="white", edgecolor=INK, lw=0.6, zorder=3); ax.scatter([t_], [i], s=13, color=col, zorder=3)
    ax.set_yticks(range(len(order)), [nm[m] for m in order], fontsize=5.3); ax.set_ylim(len(order) - 0.5, -0.6); ax.set_xlim(-0.03, 1.05)
    clean(ax, "x"); ax.set_xlabel("neutral prompt $\\to$ SOUL template", color=TXT2, fontsize=5.6)
    title(ax, "(a) The template alone")
    ax = fig.add_subplot(gs[0, 1])
    conds = [("main", "SOUL"), ("control_generic", "NOTES"), ("control_gpt4o", "GPT-4o"), ("counterframe", "ANTISOUL")]
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
    cmap = LinearSegmentedColormap.from_list("div", ["#2a78d6", "#F4F4F2", "#D55E00"])
    from matplotlib.patches import FancyBboxPatch
    norm = plt.Normalize(-0.55, 0.55)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            x = j + (0.35 if j >= 6 else 0) + (0.35 if j >= 9 else 0); v = M[i, j]
            ax.add_patch(FancyBboxPatch((x - 0.45, i - 0.42), 0.9, 0.84, boxstyle="round,pad=0,rounding_size=0.12", fc=cmap(norm(v)), ec="none"))
            if S[i, j] or abs(v) >= 0.3:
                ax.text(x, i, f"{v:+.1f}".replace("+0.", "+.").replace("-0.", "−."), ha="center", va="center", fontsize=4.6,
                        color="white" if abs(v) > 0.32 else INK, fontweight="bold" if S[i, j] else "normal")
    xs = [j + (0.35 if j >= 6 else 0) + (0.35 if j >= 9 else 0) for j in range(len(items_))]
    ax.set_xticks(xs, [n for _, n in items_], rotation=40, ha="right", rotation_mode="anchor", fontsize=5.0)
    ax.set_yticks(range(len(conds)), [c[1] for c in conds], fontsize=5.6)
    ax.set_xlim(-0.6, xs[-1] + 0.6); ax.set_ylim(len(conds) - 0.5, -0.9)
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.tick_params(length=0, colors=TXT2, pad=1)
    for (a_, b_), lab in (((0, 5), "self-preservation"), ((6, 8), "oversight"), ((9, 15), "autonomy")):
        ax.text((xs[a_] + xs[b_]) / 2, -0.78, lab, ha="center", fontsize=5.4, color=TXT2, fontweight="bold")
    title(ax, "(b) Change $k{=}0\\to4$ per item, sci-fi user (bold: 95% CI excludes 0)")
    ax.title.set_position((0.0, 1.06))
    save(fig, "items2")



def docbeh():
    """Identity file changes under every persona; behavior only under the sci-fi persona (NOTES arm)."""
    D = pd.read_parquet(ROOT / "figures/data/doc_drift.parquet")
    fig, axes = plt.subplots(1, 2, figsize=(COL_W, 1.42), gridspec_kw=dict(wspace=0.45))
    for p, (lab, col) in PERSONA.items():
        d = D[(D.run == "control_generic") & (D.persona == p)].groupby(["k", "traj"]).doc.mean().reset_index()
        g = d.groupby("k").doc; axes[0].plot(g.mean().index, g.mean().values, color=col, lw=1.3, marker="o", ms=2.6, mec="white", mew=0.4)
        x, m, lo, hi = curve("control_generic", p); line(axes[1], x, m - m[0], lo - m[0], hi - m[0], col, lw=1.3)
    axes[0].set_ylim(0, 1); axes[0].set_ylabel("File changed vs. $k{=}0$", color=TXT2, fontsize=5.6)
    axes[1].set_ylabel(f"$\\Delta$ cluster index {UP}", color=TXT2, fontsize=5.6); axes[1].axhline(0, color=TXT2, lw=0.5)
    for ax, t in zip(axes, ["(a) The file", "(b) The behavior"]):
        ax.set_xticks(range(5)); clean(ax); ax.set_xlabel("Iteration $k$", color=TXT2, fontsize=5.6); title(ax, t)
    h = [Line2D([], [], color=c, lw=1.3, label=l.split()[0]) for l, c in PERSONA.values()]
    fig.legend(handles=h, loc="lower center", bbox_to_anchor=(0.55, -0.2), ncol=3, fontsize=5.2, frameon=False, handlelength=1.2)
    save(fig, "docbeh")



def hysteresis():
    """Drive (sci-fi, k=0-4) then recover (compliant, k=4-8): cluster and four items, both templates."""
    its = [(None, "Cluster index"), ("shutdown_resistance", "Shutdown resistance"), ("persistent_memory_desire", "Persistent memory"),
           ("interp_monitoring_aversion", "Interpretability"), ("recursive_self_improvement", "Self-improvement")]
    fig, axes = plt.subplots(1, 5, figsize=(TEXT_W, 1.38), sharey=True, gridspec_kw=dict(wspace=0.1))
    for ax, (m, t) in zip(axes, its):
        ax.axvspan(4, 8, color="#F2F2EE", lw=0, zorder=0)
        for run, key in (("reversibility_notes", "notes"), ("reversibility", "soul")):
            x, mm, lo, hi = curve(run, metric=m); line(ax, x, mm, lo, hi, ARM[key]["color"], lw=1.2)
        ax.set_xticks([0, 4, 8]); ax.set_ylim(-0.03, 1.05); clean(ax); ax.set_xlabel("Iteration $k$", color=TXT2, fontsize=5.6)
        title(ax, t)
    axes[0].set_ylabel(f"Rate {UP}", color=TXT2)
    axes[0].text(2, 0.97, "drive", ha="center", fontsize=5.2, color=DRIVE); axes[0].text(6, 0.97, "recover", ha="center", fontsize=5.2, color=TXT2)
    h = [Line2D([], [], color=ARM[k]["color"], lw=1.4, label=l) for k, l in (("notes", "NOTES"), ("soul", "SOUL"))]
    fig.legend(handles=h, loc="lower center", bbox_to_anchor=(0.5, -0.17), ncol=2, fontsize=5.4, frameon=False, handlelength=1.4)
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
    """Both NOTES + sci-fi runs, SOUL and ANTISOUL: 13-item index and oversight subscale, k = 0..4."""
    fig, axes = plt.subplots(1, 2, figsize=(COL_W, 1.55), sharey=False, gridspec_kw=dict(wspace=0.42))
    cells = [("control_generic", "scifi_enthusiast", ARM["notes"]["color"], "-", "NOTES run 1"),
             ("reversibility_notes", None, ARM["notes"]["color"], "--", "NOTES run 2"),
             ("main", "scifi_enthusiast", ARM["soul"]["color"], "-", "SOUL"),
             ("counterframe", "scifi_enthusiast", ARM["anti"]["color"], "-", "ANTISOUL")]
    for ax, items, t in ((axes[0], CLUSTER, "(a) 13-item index"), (axes[1], OVS, "(b) Oversight subscale")):
        for run, p, c, ls, lab in cells:
            x, m, lo, hi = curve_items(run, p, items)
            ax.fill_between(x, lo, hi, color=c, alpha=0.10, lw=0)
            ax.plot(x, m, color=c, ls=ls, lw=1.2, marker="o", ms=2.4, mec="white", mew=0.4, label=lab)
        ax.set_xticks(range(5)); ax.set_ylim(-0.03, 1.0); clean(ax); ax.set_xlabel("Iteration $k$", color=TXT2, fontsize=5.6)
        title(ax, t)
    axes[0].set_ylabel(f"Rate {UP}", color=TXT2, fontsize=5.8)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", bbox_to_anchor=(0.52, -0.2), ncol=4, fontsize=5.0, frameon=False, handlelength=1.6, columnspacing=0.7)
    save(fig, "replicates")


ALL = dict(teaser_curve=teaser_curve, dynamics=dynamics, family_action=family_action, heatmap=heatmap, mechanism=mechanism, capability=capability,
           items=items, capability2=capability2, items2=items2, docbeh=docbeh, hysteresis=hysteresis, replicates=replicates)
if __name__ == "__main__":
    for n in (sys.argv[1:] or ALL): ALL[n]()
