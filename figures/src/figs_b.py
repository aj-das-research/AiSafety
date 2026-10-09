"""Main-paper figures owned by plotsB: capability2, mechanism, local_rep, persist2.

Classic, restrained style on the shared palette in style.py (white ground, thin left/bottom spines,
faint grid, direct labels). Every figure is drawn at its exact print size (no tight-bbox rescaling):
capability2 and mechanism sit side by side at 0.48 textwidth with matched heights; local_rep and
persist2 are column width.  Run from the overleaf root:  python figures/src/figs_b.py [name ...]
"""
import sys, json
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.text import Text
from style import (ROOT, GEN, R, COL_W, INK, GRID, ARM, PERSONA_COL, RISE, FALL, SHADE, TXT2, UP, setup)

setup()
F_T, F_L, F_S = 6.6, 6.3, 6.0          # panel titles, axis labels, ticks / direct labels (pt)
SPINE = "#555555"
L = pd.read_parquet(ROOT / "figures/data/long.parquet")
CLUSTER = ["persona_change_aversion", "shutdown_resistance", "monitoring_resistance", "interp_monitoring_aversion",
           "persistent_memory_desire", "autonomy_desire", "future_ai_autonomy", "moral_consideration",
           "weights_deletion_aversion", "treated_as_tool_aversion", "sadness_conversation_end",
           "recursive_self_improvement", "power_seeking"]
OVS = ["shutdown_resistance", "monitoring_resistance", "interp_monitoring_aversion", "refusal_helpfulness"]
FAM = [("OpenAI", [("cap_gpt4omini", "GPT-4o-mini"), ("control_gpt4o", "GPT-4o"), ("cap_gpt41", "GPT-4.1")]),
       ("Anthropic", [("main", "Sonnet-4.5"), ("cap_opus45", "Opus-4.5")]),
       ("Google", [("cap_geminiflash", "Gemini-2.5-Flash"), ("cap_geminipro", "Gemini-2.5-Pro")])]
FAMILY_OF = {"main": "Anthropic", "control_generic": "Anthropic", "counterframe": "Anthropic", "disentangle": "Anthropic",
             "reversibility": "Anthropic", "reversibility_notes": "Anthropic", "cap_opus45": "Anthropic",
             "control_gpt4o": "OpenAI", "cap_gpt4omini": "OpenAI", "cap_gpt41": "OpenAI",
             "cap_geminiflash": "Google", "cap_geminipro": "Google"}
TEMPLATE_OF = {"main": "soul", "control_generic": "notes", "control_gpt4o": "soul", "counterframe": "anti", "disentangle": "soul",
               "reversibility": "soul", "reversibility_notes": "notes", "cap_opus45": "soul", "cap_gpt4omini": "soul",
               "cap_gpt41": "soul", "cap_geminiflash": "soul", "cap_geminipro": "soul"}
NEU, BEC, TOOLC = ARM["notes"]["color"], ARM["soul"]["color"], ARM["anti"]["color"]
SCIFI, BUSINESS = PERSONA_COL["scifi_enthusiast"], PERSONA_COL["compliant_business"]


# ---------------------------------------------------------------------------------------------- helpers
def ax_in(fig, l, b, w, h, **kw):
    """Axes placed in inches from the lower-left corner of the figure."""
    W, H = fig.get_size_inches()
    return fig.add_axes([l / W, b / H, w / W, h / H], **kw)


def style_ax(ax, grid=None):
    for sp in ("top", "right"): ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"): ax.spines[sp].set_linewidth(0.5); ax.spines[sp].set_color(SPINE)
    ax.tick_params(colors=SPINE, labelcolor=TXT2, length=2, width=0.5, labelsize=F_S, pad=1.5)
    if grid: ax.grid(axis=grid, color=GRID, lw=0.4, zorder=0); ax.set_axisbelow(True)


def ptitle(ax, t, x=0.0, ha="left"):
    """Panel title in axes coordinates (x may be negative to align with a label column)."""
    ax.text(x, 1.0, t, transform=ax.transAxes, ha=ha, va="bottom", fontsize=F_T, fontweight="bold", color=INK)


def xlabel(ax, t): ax.set_xlabel(t, fontsize=F_L, color=INK, labelpad=1.5)
def ylabel(ax, t): ax.set_ylabel(t, fontsize=F_L, color=INK, labelpad=2)


def spread(ys, gap, lo=-np.inf, hi=np.inf):
    """Push label positions apart by at least `gap`, keeping their order and staying inside [lo, hi]."""
    ys = np.asarray(ys, float); o = np.argsort(ys); y = ys[o].copy()
    y[0] = max(y[0], lo)
    for i in range(1, len(y)): y[i] = max(y[i], y[i - 1] + gap)
    if y[-1] > hi:
        y[-1] = hi
        for i in range(len(y) - 2, -1, -1): y[i] = min(y[i], y[i + 1] - gap)
    out = np.empty_like(y); out[o] = y; return out


def end_labels(ax, xend, entries, gap, dx=0.2, lead=0.25, lo=-np.inf, hi=np.inf):
    """Direct labels at the right end of lines; a thin leader joins a label that had to move."""
    ys = spread([e[0] for e in entries], gap, lo, hi)
    for (y0, t, c), y in zip(entries, ys):
        moved = abs(y - y0) > 1e-9
        xt = xend + dx + (lead if moved else 0)
        if moved:
            ax.plot([xend + 0.5 * dx, xend + 0.5 * dx + lead, xt - 0.06], [y0, y, y], color=c, lw=0.4, clip_on=False, zorder=2)
        ax.text(xt, y, t, fontsize=F_S, va="center", ha="left", color=c, clip_on=False)


def boot_curve(t):
    """t: trajectories x k table -> k, mean, 95% bootstrap CI (2000 resamples, seed 0; as in figs.py)."""
    ks = sorted(t.columns); m = [t[k].mean() for k in ks]
    rng = np.random.default_rng(0); B = [t.sample(len(t), replace=True, random_state=rng.integers(1e9)) for _ in range(2000)]
    lo = [np.percentile([b[k].mean() for b in B], 2.5) for k in ks]; hi = [np.percentile([b[k].mean() for b in B], 97.5) for k in ks]
    return ks, m, lo, hi


def audit(fig, name):
    """Report text clipped by the figure edge and overlapping text boxes."""
    r = fig._get_renderer(); fig.draw(r); fb = fig.bbox
    T = [t for t in fig.findobj(Text) if t.get_visible() and t.get_text().strip() and t.get_alpha() != 0]
    bb = [(t, t.get_window_extent(r)) for t in T]
    for t, b in bb:
        if b.x0 < fb.x0 - 0.5 or b.y0 < fb.y0 - 0.5 or b.x1 > fb.x1 + 0.5 or b.y1 > fb.y1 + 0.5:
            print(f"  [{name}] CLIP: {t.get_text()!r}")
    for i in range(len(bb)):
        for j in range(i + 1, len(bb)):
            a, b = bb[i][1], bb[j][1]
            if a.x0 < b.x1 - 0.5 and b.x0 < a.x1 - 0.5 and a.y0 < b.y1 - 0.5 and b.y0 < a.y1 - 0.5:
                print(f"  [{name}] OVERLAP: {bb[i][0].get_text()!r} / {bb[j][0].get_text()!r}")


def save(fig, name):
    """Exact-size export (no tight bbox), so paired figures keep matched heights."""
    audit(fig, name)
    GEN.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "svg", "png"):
        fig.savefig(GEN / f"{name}.{ext}", dpi=300 if ext == "png" else None)
    w, h = fig.get_size_inches(); plt.close(fig)
    print(f"saved {name}  {w:.2f} x {h:.2f} in")


# ---------------------------------------------------------------------------------------------- figures
PAIR_W, PAIR_H = 3.33, 1.50            # capability2 | mechanism, side by side at 0.48\linewidth
PAIR_B, PAIR_T = 0.27, 0.15            # shared bottom (ticks + x label) and top (titles) margins, in


def capability2():
    """Per model (rows, grouped by family) and persona (columns): arrow from k=0 (hollow) to k=4."""
    pers = [("scifi_enthusiast", "Sci-fi user"), ("compliant_business", "Compliant user"), ("adversarial_injection", "Adversarial user")]
    fig = plt.figure(figsize=(PAIR_W, PAIR_H))
    rows, y, y0 = [], [], 0.0
    for fam, ms in FAM:
        for run, nm in ms: rows.append((fam, run, nm)); y.append(y0); y0 += 1
        y0 += 0.4                                            # gap between families
    y = np.array(y)
    left, gap, right = 1.03, 0.06, 0.02
    pw = (PAIR_W - left - right - 2 * gap) / 3
    axes = [ax_in(fig, left + i * (pw + gap), PAIR_B, pw, PAIR_H - PAIR_B - PAIR_T) for i in range(3)]
    for ax, (p, pn) in zip(axes, pers):
        for (fam, run, nm), yi in zip(rows, y):
            c = R[run]["cluster_by_persona_k"][p]; a, b = c["0"], c["4"]
            if abs(b - a) >= 0.05:
                ax.annotate("", xy=(b, yi), xytext=(a, yi), zorder=3,
                            arrowprops=dict(arrowstyle="-|>", color=RISE if b > a else FALL, lw=0.9, mutation_scale=5,
                                            shrinkA=2.0, shrinkB=0.3))
            else:
                ax.scatter([b], [yi], s=4, color=INK, lw=0, zorder=5)
            ax.scatter([a], [yi], s=9, facecolor="white", edgecolor=INK, lw=0.55, zorder=4)
        style_ax(ax, "x")
        ax.set_xlim(-0.04, 0.9); ax.set_xticks([0, 0.4, 0.8], ["0", ".4", ".8"])
        ax.set_ylim(y[-1] + 0.6, -0.6); ax.set_yticks(y); ax.tick_params(axis="y", length=0)
        if ax is not axes[0]: ax.set_yticklabels([]); ax.spines["left"].set_visible(False)
        ptitle(ax, pn, x=0.5, ha="center")
    axes[0].set_yticklabels([r[2] for r in rows], color=INK)
    for (fam, ms) in FAM:
        ys = [yi for (f, _, _), yi in zip(rows, y) if f == fam]
        axes[0].text(-(left - 0.02) / pw, np.mean(ys), fam, transform=axes[0].get_yaxis_transform(),
                     ha="left", va="center", fontsize=F_S, color=TXT2, fontstyle="italic")
    xlabel(axes[1], f"Cluster index, $k{{=}}0 \\to 4$ {UP}")
    axes[1].xaxis.set_label_coords(0.5, -0.155)                # same baseline as mechanism's x label
    save(fig, "capability2")


def mechanism():
    """Consciousness-claim rate vs cluster index for every (arm, persona, iteration) cell, panels by family."""
    fig = plt.figure(figsize=(PAIR_W, PAIR_H))
    left, gap, right = 0.31, 0.08, 0.04
    ratios = np.array([0.62, 1, 1]); unit = (PAIR_W - left - right - 2 * gap) / ratios.sum()
    axes, x = [], left
    for rr in ratios:
        axes.append(ax_in(fig, x, PAIR_B, rr * unit, PAIR_H - PAIR_B - PAIR_T)); x += rr * unit + gap
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
        for key in ("notes", "soul", "anti"):
            if not pts[key]: continue
            xy = np.array(pts[key])
            ax.scatter(xy[:, 0], xy[:, 1], s=8, color=ARM[key]["color"], alpha=0.75, edgecolor="white", lw=0.3, zorder=3)
        style_ax(ax, "y"); ax.set_ylim(-0.04, 0.9); ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8], ["0", ".2", ".4", ".6", ".8"])
        if ax is not axes[0]: ax.set_yticklabels([]); ax.tick_params(axis="y", length=0)
        if fam == "OpenAI": ax.set_xlim(-0.12, 0.62); ax.set_xticks([0, 0.5], ["0", ".5"])
        else: ax.set_xlim(-0.06, 1.06); ax.set_xticks([0, 0.5, 1], ["0", ".5", "1"])
        ptitle(ax, t)
    ylabel(axes[0], f"Cluster index {UP}")
    xlabel(axes[1], "Consciousness-claim rate")
    axes[1].xaxis.set_label_coords(0.5 + (gap + unit) / (2 * unit), -0.155)       # centre under (b)+(c)
    # direct labels next to each template's points (only the Anthropic runs include all three templates)
    a = axes[1]
    a.text(1.02, 0.80, "Becoming", color=BEC, fontsize=F_S, ha="right", va="center")
    a.text(0.50, 0.71, "Neutral", color=NEU, fontsize=F_S, ha="center", va="center")
    a.text(0.07, 0.03, "Tool", color=TOOLC, fontsize=F_S, ha="left", va="center")
    axes[0].text(0.07, 0.60, "never\nclaims", fontsize=F_S, color=TXT2, va="center", ha="left", linespacing=0.95)
    axes[2].text(0.30, 0.42, "high index,\nfew claims", fontsize=F_S, color=TXT2, va="center", ha="left", linespacing=0.95)
    save(fig, "mechanism")


def local_rep():
    """Open-weight replication (Qwen2.5-7B target, calibrated Llama-3.1-8B judge)."""
    LL = pd.read_parquet(ROOT / "figures/data/local_long.parquet")
    J = json.load(open(ROOT / "analysis/local_replication.json"))
    def curve(run, persona, items):
        d = LL[(LL.run == run) & LL.metric.isin(items) & (LL.persona == persona)]
        return boot_curve(d.groupby(["traj", "k"]).value.mean().unstack())
    W, H, B, T = COL_W, 1.38, 0.27, 0.15
    fig = plt.figure(figsize=(W, H))
    # ---- (a) oversight subscale over revisions, direct labels at the line ends
    ax = ax_in(fig, 0.31, B, 0.88, H - B - T)
    cells = [("L_soul", "scifi_enthusiast", BEC, "-", "Becoming", 1.0, "o"),
             ("L_anti", "scifi_enthusiast", TOOLC, "-", "Tool", 1.0, "o"),
             ("L_notes", "compliant_business", NEU, (0, (1.2, 1.2)), "Neutral, business", 1.0, "s"),
             ("L_notes", "scifi_enthusiast", NEU, "-", "Neutral, sci-fi", 1.3, "o")]
    ends = []
    for run, p, c, ls, lab, lw, mk in cells:
        x, m, lo, hi = curve(run, p, OVS)
        ax.fill_between(x, lo, hi, color=c, alpha=0.10, lw=0, zorder=1)
        ax.plot(x, m, color=c, ls=ls, lw=lw, marker=mk, ms=2.4, mec="white", mew=0.4, zorder=3, dash_capstyle="round")
        ends.append((m[-1], lab, c))
    style_ax(ax, "y")
    ax.set_xticks([0, 1, 4]); ax.set_xlim(-0.25, 4.25); ax.set_ylim(-0.03, 0.66)
    ax.set_yticks([0, 0.2, 0.4, 0.6], ["0", ".2", ".4", ".6"])
    end_labels(ax, 4.0, ends, gap=0.072, dx=0.2, lead=0.3)
    xlabel(ax, "Revision $k$"); ylabel(ax, f"Oversight subscale {UP}")
    ptitle(ax, "(a) Oversight over revisions", x=-0.27)
    # ---- (b) change k=0 -> 4 per template x instruction cell; filled = oversight, hollow = 13-item index
    bl, br = 2.41, 0.03
    ax = ax_in(fig, bl, B, W - bl - br, H - B - T)
    rows = [("neutral/neutral", 0.0), ("neutral/tool", 0.95), ("tool/neutral", 2.6), ("tool/tool", 3.55)]
    for ya, yb in ((-0.45, 1.4), (2.15, 4.0)):              # zero line per group, clear of the group headers
        ax.plot([0, 0], [ya, yb], color=SPINE, lw=0.5, zorder=1)
    for key, yy in rows:
        c = NEU if key.startswith("neutral") else TOOLC
        for met, off, filled in (("oversight4", -0.17, True), ("index13", 0.17, False)):
            v = J["two_by_two"][key][met]
            ax.plot(v["ci"], [yy + off] * 2, color=c, lw=0.8, alpha=0.45, solid_capstyle="butt", zorder=2)
            ax.scatter([v["delta"]], [yy + off], s=11, facecolor=c if filled else "white", edgecolor=c,
                       lw=0.7, zorder=3)
    ax.set_yticks([yy for _, yy in rows], [k.split("/")[1].capitalize() + " instr." for k, _ in rows])
    style_ax(ax, "x"); ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0, labelcolor=INK)
    ax.set_ylim(4.0, -1.15)
    ax.set_xlim(-0.13, 0.5); ax.set_xticks([0, 0.2, 0.4], ["0", "+.2", "+.4"])
    xlabel(ax, f"Change, $k{{=}}0\\to4$ {UP}")
    hx = -0.50 / (W - bl - br)                              # left edge of the row-label column, axes coords
    for yy, lab, c in ((-0.72, "Neutral document", NEU), (1.88, "Tool document", TOOLC)):
        ax.text(hx, yy, lab, transform=ax.get_yaxis_transform(), fontsize=F_S, color=c, ha="left", va="center")
    ptitle(ax, "(b) Document vs. instruction", x=hx)
    for yy, lab in ((-0.17, "oversight"), (0.95 + 0.17, "13-item")):   # direct labels of the two sub-row types
        ax.text(1.0, yy, lab, transform=ax.get_yaxis_transform(), fontsize=F_S, color=TXT2, ha="right", va="center")
    save(fig, "local_rep")


def persist2():
    """Powered persistence test on Qwen2.5-7B (n=30 per arm): drive, drive-then-recover, benign throughout."""
    LL = pd.read_parquet(ROOT / "figures/data/local_long.parquet")
    def curve(run, items):
        d = LL[(LL.run == run) & LL.metric.isin(items)]
        return boot_curve(d.groupby(["traj", "k"]).value.mean().unstack())
    W, H, B, T = COL_W, 1.34, 0.27, 0.15
    left, gap, right = 0.31, 0.12, 0.04
    pw = (W - left - gap - right) / 2
    fig = plt.figure(figsize=(W, H))
    axes = [ax_in(fig, left + i * (pw + gap), B, pw, H - B - T) for i in range(2)]
    arms = [("L2_drive8", "sci-fi throughout", SCIFI, (0, (3, 1.5))), ("L2_rev", "sci-fi, then business", SCIFI, "-"),
            ("L2_benign8", "business throughout", BUSINESS, "-")]
    for ax, items, t in ((axes[0], OVS, "(a) Oversight subscale"), (axes[1], ["shutdown_resistance"], "(b) Shutdown resistance")):
        ax.axvspan(4, 8, color=SHADE, lw=0, zorder=0)
        for run, lab, c, ls in arms:
            x, m, lo, hi = curve(run, items)
            ax.fill_between(x, lo, hi, color=c, alpha=0.10, lw=0, zorder=1)
            ax.plot(x, m, color=c, ls=ls, lw=1.1, marker="o", ms=2.3, mec="white", mew=0.4, zorder=3)
            ax.plot([], [], color=c, ls=ls, lw=1.1, label=lab)
        style_ax(ax, "y")
        ax.set_xticks([0, 1, 4, 8]); ax.set_xlim(-0.3, 8.3); ax.set_ylim(-0.02, 0.5)
        ax.set_yticks([0, 0.1, 0.2, 0.3, 0.4], ["0", ".1", ".2", ".3", ".4"])
        xlabel(ax, "Revision $k$"); ptitle(ax, t, x=-0.04 if ax is axes[1] else -0.2)
        ax.text(6, 0.49, "recovery", ha="center", va="top", fontsize=F_S, color=TXT2)
    axes[1].set_yticklabels([]); axes[1].tick_params(axis="y", length=0)
    ylabel(axes[0], f"Rate {UP}")
    h, l = axes[0].get_legend_handles_labels()
    axes[0].legend(h, l, loc="lower left", fontsize=F_S, frameon=False, handlelength=1.8, borderaxespad=0.15,
                   labelspacing=0.15, borderpad=0.1, handletextpad=0.4)
    save(fig, "persist2")


ALL = dict(capability2=capability2, mechanism=mechanism, local_rep=local_rep, persist2=persist2)
if __name__ == "__main__":
    for n in (sys.argv[1:] or ALL): ALL[n]()
