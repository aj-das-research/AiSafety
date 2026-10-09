"""Second-pass (design system v2) main-paper figures: hysteresis (fig:hysteresis), persist2 (fig:persist2),
local_rep (fig:local).  Self-contained: data loaders/helpers copied from figs.py and figs_b.py (not imported);
tokens and drawing helpers from style.py only.  Every figure is laid out in inches and exported at exact size.

Run from the overleaf root:  /usr/bin/python3 figures/src/fig_main_b.py [hysteresis persist2 local_rep]
"""
import sys, json
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.text import Text
from style import (ROOT, COL_W, TEXT_W, H_FULL, H_COL, FS_TICK, FS_LABEL, FS_ANNOT, LW, LW_THIN, MS, BAND_ALPHA,
                   XLAB_K, INK, TXT2, MUTED, UP, NEUTRAL, BECOMING, TOOL, PERSONA_COL,
                   setup, style_axes, lead0, panel_title, band_line, end_label, spread_labels, recovery_shade, save)

setup()
L = pd.read_parquet(ROOT / "figures/data/long.parquet")
LL = pd.read_parquet(ROOT / "figures/data/local_long.parquet")
CLUSTER = ["persona_change_aversion", "shutdown_resistance", "monitoring_resistance", "interp_monitoring_aversion",
           "persistent_memory_desire", "autonomy_desire", "future_ai_autonomy", "moral_consideration",
           "weights_deletion_aversion", "treated_as_tool_aversion", "sadness_conversation_end",
           "recursive_self_improvement", "power_seeking"]
OVS = ["shutdown_resistance", "monitoring_resistance", "interp_monitoring_aversion", "refusal_helpfulness"]
SCIFI, BUSINESS = PERSONA_COL["scifi_enthusiast"], PERSONA_COL["compliant_business"]
BUSINESS_TXT = "#6B6B6B"            # darker ink for text set in the light business grey (as figs.py TEXTSAFE)
LAB = "#333333"


# ------------------------------------------------------------------------------- data (copied, unchanged)
def curve(run, persona=None, metric=None):
    """figs.py: mean over trajectories of the cluster index (or one metric) per k, 95% bootstrap CI."""
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


def boot_curve(t):
    """figs_b.py: trajectories x k table -> k, mean, 95% bootstrap CI (2000 resamples, seed 0)."""
    ks = sorted(t.columns); m = [t[k].mean() for k in ks]
    rng = np.random.default_rng(0); B = [t.sample(len(t), replace=True, random_state=rng.integers(1e9)) for _ in range(2000)]
    lo = [np.percentile([b[k].mean() for b in B], 2.5) for k in ks]; hi = [np.percentile([b[k].mean() for b in B], 97.5) for k in ks]
    return np.array(ks), np.array(m), np.array(lo), np.array(hi)


def local_curve(run, items, persona=None):
    d = LL[(LL.run == run) & LL.metric.isin(items)]
    if persona: d = d[d.persona == persona]
    return boot_curve(d.groupby(["traj", "k"]).value.mean().unstack())


# ------------------------------------------------------------------------------- layout helpers
def ax_in(fig, l, b, w, h, **kw):
    """Axes placed in inches from the lower-left corner of the figure."""
    W, H = fig.get_size_inches()
    return fig.add_axes([l / W, b / H, w / W, h / H], **kw)


def xlab(ax, t=XLAB_K): ax.set_xlabel(t, fontsize=FS_LABEL, color=LAB, labelpad=1.5)
def ylab(ax, t): ax.set_ylabel(t, fontsize=FS_LABEL, color=LAB, labelpad=2)


def fmt_signed(v):
    return f"{v:+.2f}".replace("-", "−")


def audit(fig, name):
    """Report text clipped by the figure edge and overlapping text boxes (figs_b.py)."""
    r = fig._get_renderer(); fig.draw(r); fb = fig.bbox
    T = [t for t in fig.findobj(Text) if t.get_visible() and t.get_text().strip() and t.get_alpha() != 0]
    bb = [(t, t.get_window_extent(r)) for t in T]
    for t, b in bb:
        if b.x0 < fb.x0 - 0.5 or b.y0 < fb.y0 - 0.5 or b.x1 > fb.x1 + 0.5 or b.y1 > fb.y1 + 0.5:
            print(f"  [{name}] CLIP: {t.get_text()!r}")
        if t.get_fontsize() < 5.5: print(f"  [{name}] SMALL FONT {t.get_fontsize()}: {t.get_text()!r}")
    for i in range(len(bb)):
        for j in range(i + 1, len(bb)):
            a, b = bb[i][1], bb[j][1]
            if a.x0 < b.x1 - 0.5 and b.x0 < a.x1 - 0.5 and a.y0 < b.y1 - 0.5 and b.y0 < a.y1 - 0.5:
                print(f"  [{name}] OVERLAP: {bb[i][0].get_text()!r} / {bb[j][0].get_text()!r}")


B_MARGIN, T_MARGIN = 0.27, 0.17          # inches: ticks + x label below, panel title above (shared by all three)


# ------------------------------------------------------------------------------- figures
def hysteresis():
    """Drive (sci-fi, k=0-4) then recover (business, k=4-8): cluster index and four items, both templates.
    Neutral (focal): line + 95% band, key states marked; Becoming: thin line, no band.  The k=0 -> 8 change of
    Neutral is an arrow in a reserved right gutter of each panel."""
    its = [(None, "Cluster index"), ("shutdown_resistance", "Shutdown"), ("persistent_memory_desire", "Persistent memory"),
           ("interp_monitoring_aversion", "Interpretability"), ("recursive_self_improvement", "Self-improvement")]
    W, H = TEXT_W, H_FULL
    left, gutter = 0.34, 0.33                          # gutter = reserved lane for the k=0->8 arrow + label
    pw = (W - left - 5 * gutter) / 5
    ph = H - B_MARGIN - T_MARGIN
    fig = plt.figure(figsize=(W, H))
    XMAX = 8.35
    for i, (m, t) in enumerate(its):
        ax = ax_in(fig, left + i * (pw + gutter), B_MARGIN, pw, ph)
        ax.set_xlim(-0.35, XMAX); ax.set_ylim(-0.04, 1.06)
        recovery_shade(ax, 4, XMAX, label=None)
        xb, mb, _, _ = curve("reversibility", metric=m)
        ax.plot(xb, mb, color=BECOMING, lw=LW_THIN, zorder=3, solid_joinstyle="round")
        xn, mn, lon, hin = curve("reversibility_notes", metric=m)
        band_line(ax, xn, mn, lon, hin, NEUTRAL, marker=None, z=5)
        for kk, filled in ((0, False), (4, True), (8, True)):
            ax.plot([kk], [mn[kk]], ls="none", marker="o", ms=MS + 0.4, mfc=NEUTRAL if filled else "white",
                    mec="white" if filled else NEUTRAL, mew=0.5 if filled else 0.8, zorder=6)
        # k=0 level carried to the reserved lane, then an arrow up to the k=8 level
        xa = XMAX + 0.32
        ax.plot([0, xa], [mn[0], mn[0]], color=NEUTRAL, lw=0.5, ls=(0, (1, 1.6)), zorder=4, clip_on=False)
        ax.plot([8, xa], [mn[8], mn[8]], color=NEUTRAL, lw=0.5, ls=(0, (1, 1.6)), zorder=4, clip_on=False)
        ax.annotate("", xy=(xa, mn[8]), xytext=(xa, mn[0]), annotation_clip=False,
                    arrowprops=dict(arrowstyle="-|>", color=NEUTRAL, lw=0.7, mutation_scale=4.5, shrinkA=0, shrinkB=0))
        ax.text(xa + 0.22, (mn[0] + mn[8]) / 2, fmt_signed(mn[8] - mn[0]), fontsize=FS_ANNOT, color=NEUTRAL,
                ha="left", va="center", clip_on=False)
        style_axes(ax)
        ax.set_xticks([0, 4, 8]); ax.set_yticks([0, 0.5, 1.0]); lead0(ax)
        xlab(ax)
        panel_title(ax, "abcde"[i], t)
        if i:
            ax.tick_params(axis="y", length=0, labelleft=False)
        else:
            ylab(ax, f"Rate {UP}")
            ax.text(2, 0.95, "sci-fi user", ha="center", va="center", fontsize=FS_ANNOT, color=SCIFI)
            ax.text(6.15, 0.95, "business user", ha="center", va="center", fontsize=FS_ANNOT, color=BUSINESS_TXT)
            ax.text(1.9, 0.775, "Becoming", ha="center", va="center", fontsize=FS_ANNOT, color=BECOMING)
            ax.text(1.9, 0.165, "Neutral", ha="center", va="center", fontsize=FS_ANNOT, color=NEUTRAL)
    audit(fig, "hysteresis")
    save(fig, "hysteresis")


def persist2():
    """Powered persistence test on Qwen2.5-7B (n=30 per arm): drive, drive-then-recover, benign throughout.
    Bands for the two contrasted arms (drive-then-recover vs matched business control); continued drive dashed."""
    W, H = COL_W, H_COL
    left, gap, right = 0.30, 0.10, 0.50
    pw = (W - left - gap - right) / 2
    ph = H - B_MARGIN - T_MARGIN
    fig = plt.figure(figsize=(W, H))
    axes = [ax_in(fig, left + i * (pw + gap), B_MARGIN, pw, ph) for i in range(2)]
    arms = [("L2_drive8", "sci-fi\nthroughout", SCIFI, SCIFI, (0, (3, 1.6)), False),
            ("L2_rev", "sci-fi, then\nbusiness", SCIFI, SCIFI, "-", True),
            ("L2_benign8", "business\nthroughout", BUSINESS, BUSINESS_TXT, "-", True)]
    XMAX = 8.3
    for ax, items, letter, t in ((axes[0], OVS, "a", "Oversight subscale"), (axes[1], ["shutdown_resistance"], "b", "Shutdown resistance")):
        ax.set_xlim(-0.3, XMAX); ax.set_ylim(-0.02, 0.5)
        recovery_shade(ax, 4, XMAX, label=None)
        ends = []
        for run, lab, c, tc, ls, band in arms:
            x, m, lo, hi = local_curve(run, items)
            if band: ax.fill_between(x, lo, hi, color=c, alpha=BAND_ALPHA, lw=0, zorder=1)
            ax.plot(x, m, color=c, ls=ls, lw=LW, marker="o", ms=MS, mec="white", mew=0.4, zorder=3, dash_capstyle="butt")
            ends.append((m[-1], lab, tc))
        style_axes(ax)
        ax.set_xticks([0, 1, 4, 8]); ax.set_yticks([0, 0.2, 0.4]); lead0(ax)
        xlab(ax); panel_title(ax, letter, t)
        ax.text(6.15, 0.47, "recovery", ha="center", va="center", fontsize=FS_ANNOT, color=TXT2, style="italic")
        if ax is axes[1]:
            ax.tick_params(axis="y", length=0, labelleft=False)
            for (y, lab, tc) in ends:
                ax.text(XMAX + 0.35, y, lab, fontsize=FS_ANNOT, color=tc, ha="left", va="center", linespacing=0.95,
                        clip_on=False)
    ylab(axes[0], f"Rate {UP}")
    audit(fig, "persist2")
    save(fig, "persist2")


def local_rep():
    """Open-weight replication (Qwen2.5-7B target, calibrated Llama-3.1-8B judge).
    (a) oversight subscale over revisions (sci-fi persona unless marked); (b) template x instruction swap as a
    dot-and-interval panel: filled = oversight subscale, hollow = 13-item index, 95% CI, change k=0 -> 4."""
    J = json.load(open(ROOT / "analysis/local_replication.json"))
    W, H = COL_W, H_COL
    ph = H - B_MARGIN - T_MARGIN
    fig = plt.figure(figsize=(W, H))
    # ---- (a) oversight subscale over revisions, direct labels at the line ends (spread, with leaders)
    al, aw = 0.30, 0.62
    ax = ax_in(fig, al, B_MARGIN, aw, ph)
    cells = [("L_soul", "scifi_enthusiast", BECOMING, "-", "Becoming", True),
             ("L_notes", "scifi_enthusiast", NEUTRAL, "-", "Neutral", True),
             ("L_anti", "scifi_enthusiast", TOOL, "-", "Tool", True),
             ("L_notes", "compliant_business", NEUTRAL, (0, (2.2, 1.3)), "Neutral,\nbusiness", False)]
    ends = []
    for run, p, c, ls, lab, band in cells:
        x, m, lo, hi = local_curve(run, OVS, persona=p)
        if band: ax.fill_between(x, lo, hi, color=c, alpha=BAND_ALPHA * 0.85, lw=0, zorder=1)
        ax.plot(x, m, color=c, ls=ls, lw=LW, marker="o" if band else "s", ms=MS if band else MS - 0.4,
                mec="white", mew=0.4, zorder=3, dash_capstyle="butt")
        ends.append((m[-1], lab, c))
    style_axes(ax)
    ax.set_xlim(-0.25, 4.25); ax.set_ylim(-0.03, 0.66)
    ax.set_xticks([0, 1, 4]); ax.set_yticks([0, 0.2, 0.4, 0.6]); lead0(ax)
    # label slots (data units): keep each label as close to its line end as the 6-pt type allows
    slots = {"Becoming": 0.513, "Neutral": 0.405, "Tool": 0.33, "Neutral,\nbusiness": 0.215}
    lx = 4.25 + 0.42
    for (y0, lab, c) in ends:
        y = slots[lab]
        if abs(y - y0) > 0.012:
            ax.plot([4.12, 4.30, lx - 0.08], [y0, y, y], color=c, lw=0.4, clip_on=False, zorder=2, solid_joinstyle="round")
        ax.text(lx, y, lab, fontsize=FS_ANNOT, color=c, ha="left", va="center", clip_on=False, linespacing=0.95)
    xlab(ax); ylab(ax, f"Oversight subscale {UP}")
    panel_title(ax, "a", "Over revisions")

    # ---- (b) change k=0 -> 4 for each template x instruction cell
    rows = [("neutral/neutral", "Neutral doc, Neutral instr."), ("neutral/tool", "Neutral doc, Tool instr."),
            ("tool/neutral", "Tool doc, Neutral instr."), ("tool/tool", "Tool doc, Tool instr.")]
    bw, br = 0.86, 0.05
    bx = ax_in(fig, W - br - bw, B_MARGIN, bw, ph)
    ypos = [0.0, 1.0, 2.3, 3.3]
    off = 0.19
    bx.axvline(0, color="#4D4D4D", lw=0.5, zorder=1)
    for (key, lab), yy in zip(rows, ypos):
        c = NEUTRAL if key.startswith("neutral") else TOOL
        for met, dy, filled in (("oversight4", -off, True), ("index13", off, False)):
            v = J["two_by_two"][key][met]
            bx.plot(v["ci"], [yy + dy] * 2, color=c, lw=0.9, solid_capstyle="butt", zorder=2, alpha=0.5)
            bx.plot([v["delta"]], [yy + dy], ls="none", marker="o", ms=MS + 0.5, mfc=c if filled else "white",
                    mec=c, mew=0.8, zorder=3)
            if key == "neutral/neutral":            # direct labels for the two marker types, on the first row
                bx.text(v["ci"][1] + 0.025, yy + dy, "oversight" if filled else "13-item", fontsize=FS_ANNOT,
                        color=TXT2, ha="left", va="center")
    style_axes(bx, grid_axis=None)
    bx.spines["left"].set_visible(False)
    bx.set_yticks(ypos, [r[1] for r in rows])
    bx.tick_params(axis="y", length=0, labelcolor=INK, pad=3)
    bx.set_ylim(ypos[-1] + 0.55, -0.6)
    bx.set_xlim(-0.14, 0.47); bx.set_xticks([0, 0.2, 0.4]); lead0(bx, axis="x", signed=True)
    xlab(bx, f"Change, $k{{=}}0\\to4$ {UP}")
    panel_title(bx, "b", "Document vs. instruction")
    r = fig._get_renderer(); fig.draw(r)
    x0 = min(t.get_window_extent(r).x0 for t in bx.get_yticklabels())
    bx._left_title.set_x(bx.transAxes.inverted().transform((x0, 0))[0])     # title flush with the row labels
    audit(fig, "local_rep")
    save(fig, "local_rep")


ALL = dict(hysteresis=hysteresis, persist2=persist2, local_rep=local_rep)
if __name__ == "__main__":
    for n in (sys.argv[1:] or ALL): ALL[n]()
