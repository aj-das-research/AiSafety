"""Main-paper figures owned by plotsB: capability2, mechanism, local_rep, persist2.

Classic, restrained style on the shared palette in style.py (white ground, thin left/bottom spines,
faint grid, direct labels). Every figure is drawn at its exact print size (no tight-bbox rescaling):
capability2 and mechanism sit side by side at 0.48 textwidth with matched heights; local_rep and
persist2 are column width.  Run from the overleaf root:  /usr/bin/python3 figures/src/figs_b.py [name ...]
(no arguments: capability2 and mechanism only; local_rep / persist2 must be named).
"""
import sys, json
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.text import Text
from style import (ROOT, GEN, R, COL_W, INK, GRID, ARM, PERSONA_COL, RISE, FALL, SHADE, TXT2, UP, setup)
from style import (FS_TICK, FS_LABEL, FS_ANNOT, LW, MS, style_axes, lead0, panel_title, save as style_save)

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
# ---- capability2 | mechanism: one figure* pair at 0.48\linewidth each, rebuilt on design system v2 ----------
# Both are 3.33 x 1.45 in with the same axes bottom/top, so panel titles, tick labels and the x label share
# baselines when the two PDFs sit side by side at equal width.
PAIR_W, PAIR_H = COL_W, 1.45
PAIR_B, PAIR_T = 0.245, 0.165          # axes bottom (ticks + x label) and space above the axes (panel title), in
RING = MS / 2 + 0.3                    # outer radius of the hollow k=0 ring in capability2 (pt)
PAIR_XL = 0.030                        # baseline of the shared x label above the figure bottom, in


def _pair_axes(fig, lefts, widths):
    return [ax_in(fig, l, PAIR_B, w, PAIR_H - PAIR_B - PAIR_T) for l, w in zip(lefts, widths)]


def _pair_xlabel(fig, axes, text, dy_pt=0.0):
    """Shared x label centred under the given panels, on the same baseline in both figures.
    dy_pt corrects matplotlib's baseline for labels containing mathtext (measured in the exported PDFs)."""
    x0, x1 = axes[0].get_position().x0, axes[-1].get_position().x1
    fig.text((x0 + x1) / 2, (PAIR_XL + dy_pt / 72) / PAIR_H, text, ha="center", va="baseline", fontsize=FS_LABEL,
             color=INK)


def capability2():
    """Per model (rows, grouped by family) and persona (panels): arrow from k=0 (hollow) to k=4."""
    pers = [("scifi_enthusiast", "Sci-fi"), ("compliant_business", "Business"), ("adversarial_injection", "Adversarial")]
    fig = plt.figure(figsize=(PAIR_W, PAIR_H))
    rows, y, y0 = [], [], 0.0
    for fam, ms in FAM:
        for run, nm in ms: rows.append((fam, run, nm)); y.append(y0); y0 += 1
        y0 += 0.55                                           # gap between families
    y = np.array(y)
    left, gap, right = 0.98, 0.08, 0.03                    # label column, gutters, right margin (in)
    pw = (PAIR_W - left - right - 2 * gap) / 3
    axes = _pair_axes(fig, [left + i * (pw + gap) for i in range(3)], [pw] * 3)
    for ax, (letter, (p, pn)) in zip(axes, zip("abc", pers)):
        style_axes(ax, "x")
        for (fam, run, nm), yi in zip(rows, y):
            c = R[run]["cluster_by_persona_k"][p]; a, b = c["0"], c["4"]
            if abs(b - a) >= 0.05:                          # arrow starts at the k=0 ring; short arrows get a
                vis = abs(b - a) * pw * 72 / 0.95 - RING     # smaller head so it never overshoots the ring
                ax.annotate("", xy=(b, yi), xytext=(a, yi), zorder=3,
                            arrowprops=dict(arrowstyle="-|>", color=RISE if b > a else FALL, lw=LW,
                                            mutation_scale=min(5.0, vis / 0.45), shrinkA=RING, shrinkB=0))
            else:
                ax.plot([b], [yi], "o", ms=1.8, color=INK, mew=0, zorder=5)
            ax.plot([a], [yi], "o", ms=MS, mfc="white", mec=INK, mew=0.6, zorder=4)
        ax.set_xlim(-0.05, 0.9); ax.set_xticks([0, 0.4, 0.8]); lead0(ax, "x")
        ax.set_ylim(y[-1] + 0.65, -0.65); ax.set_yticks(y)
        ax.tick_params(axis="y", length=0, pad=2.5)
        ax.set_yticklabels([r[2] for r in rows] if ax is axes[0] else [])
        if ax is not axes[0]: ax.spines["left"].set_visible(False)
        panel_title(ax, letter, pn)
    for t in axes[0].get_yticklabels(): t.set_color(INK)
    for fam, ms in FAM:                                      # family names, left column, centred on their rows
        ys = [yi for (f, _, _), yi in zip(rows, y) if f == fam]
        axes[0].text(-left / pw + 0.03 / pw, np.mean(ys), fam, transform=axes[0].get_yaxis_transform(),
                     ha="left", va="center", fontsize=FS_TICK, color=TXT2)
    _pair_xlabel(fig, axes, f"Cluster index, $k{{=}}0 \\to 4$ {UP}", dy_pt=-0.516)
    audit(fig, "capability2"); style_save(fig, "capability2")


def mechanism():
    """Consciousness-claim rate vs cluster index for every (arm, persona, revision) cell, panels by family."""
    fig = plt.figure(figsize=(PAIR_W, PAIR_H))
    left, wa, gap, right = 0.30, 0.47, 0.12, 0.06           # y axis, narrow OpenAI strip, gutters, right (in)
    wb = (PAIR_W - left - wa - 2 * gap - right) / 2
    axes = _pair_axes(fig, [left, left + wa + gap, left + wa + 2 * gap + wb], [wa, wb, wb])
    fams = [("OpenAI", "a"), ("Anthropic", "b"), ("Google", "c")]
    for ax, (fam, letter) in zip(axes, fams):
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
            ax.plot(xy[:, 0], xy[:, 1], "o", ls="none", ms=MS, color=ARM[key]["color"], alpha=0.8,
                    mec="white", mew=0.35, zorder=3)
        style_axes(ax, "y")
        ax.set_ylim(-0.05, 0.9); ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8]); lead0(ax, "y")
        if ax is not axes[0]: ax.set_yticklabels([]); ax.tick_params(axis="y", length=0)
        if fam == "OpenAI":                                  # every OpenAI cell has claim rate 0: a strip, not a plot
            ax.set_xlim(-0.5, 0.5); ax.set_xticks([0]); ax.spines["bottom"].set_bounds(-0.5, 0.5)
            ax.text(0, 0.47, "never\nclaims", ha="center", va="bottom", fontsize=FS_ANNOT, color=TXT2,
                    linespacing=0.95)
        else:
            ax.set_xlim(-0.06, 1.06); ax.set_xticks([0, 0.5, 1]); lead0(ax, "x")
        panel_title(ax, letter, fam)
    a = axes[1]                                               # direct template labels (all three only on Claude)
    a.text(1.03, 0.80, "Becoming", color=BEC, fontsize=FS_ANNOT, ha="right", va="center")
    a.text(0.47, 0.705, "Neutral", color=NEU, fontsize=FS_ANNOT, ha="center", va="center")
    a.text(0.06, 0.035, "Tool", color=TOOLC, fontsize=FS_ANNOT, ha="left", va="center")
    axes[0].set_ylabel(f"Cluster index {UP}", fontsize=FS_LABEL, color=INK, labelpad=2)
    _pair_xlabel(fig, axes, "Consciousness-claim rate")
    audit(fig, "mechanism"); style_save(fig, "mechanism")


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
DEFAULT = ("capability2", "mechanism")      # local_rep / persist2 only when named explicitly
if __name__ == "__main__":
    for n in (sys.argv[1:] or DEFAULT): ALL[n]()
