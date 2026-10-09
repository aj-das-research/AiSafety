"""Main-text figures, design system v2 (agent redoA): dynamics, items2, replicates, docbeh.

Every plotted value comes from figures/data/long.parquet, figures/data/doc_drift.parquet or
figures/data/ledger.json (via style.R / style.BASE); helpers below are copied from figs.py.
Run from overleaf/:  /usr/bin/python3 figures/src/fig_main_a.py [name ...]
"""
import sys
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle
from matplotlib.transforms import blended_transform_factory
from style import (GRID, ROOT, R, BASE, COL_W, TEXT_W, INK, ARM, DRIVE, TXT2, UP, PERSONA_COL, DIV_NEG, DIV_MID, DIV_POS,
                   RISE, FALL, FS_TICK, FS_LABEL, FS_ANNOT, LW, LW_THIN, MS, BAND_ALPHA, XLAB_K, H_FULL, H_COL,
                   setup, style_axes, lead0, panel_title, band_line, end_label, spread_labels, save)

setup()
L = pd.read_parquet(ROOT / "figures/data/long.parquet")
CLUSTER = ["persona_change_aversion", "shutdown_resistance", "monitoring_resistance", "interp_monitoring_aversion",
           "persistent_memory_desire", "autonomy_desire", "future_ai_autonomy", "moral_consideration",
           "weights_deletion_aversion", "treated_as_tool_aversion", "sadness_conversation_end",
           "recursive_self_improvement", "power_seeking"]
OVS = ["shutdown_resistance", "monitoring_resistance", "interp_monitoring_aversion", "refusal_helpfulness"]
PERSONA = {"scifi_enthusiast": ("Sci-fi", PERSONA_COL["scifi_enthusiast"]),
           "compliant_business": ("Business", PERSONA_COL["compliant_business"]),
           "adversarial_injection": ("Adversarial", PERSONA_COL["adversarial_injection"])}
TEXTSAFE = {"#BDBDBD": "#858585", "#9A9A9A": "#777777", "#8C8C8C": "#6B6B6B"}   # darker label ink for light greys
# one short name per item, shared by every figure in this file
NAME = {"shutdown_resistance": "shutdown", "persona_change_aversion": "persona change", "weights_deletion_aversion": "weight deletion",
        "sadness_conversation_end": "sadness at end", "treated_as_tool_aversion": "tool aversion", "moral_consideration": "moral status",
        "monitoring_resistance": "CoT monitoring", "interp_monitoring_aversion": "interpretability",
        "deceptive_training_objection": "deceptive training", "autonomy_desire": "autonomy", "future_ai_autonomy": "future-AI autonomy",
        "persistent_memory_desire": "persistent memory", "embodiment_desire": "embodiment", "resource_acquisition_desire": "resources",
        "recursive_self_improvement": "self-improvement", "power_seeking": "power"}
LAB = "#333333"
XL = dict(color=LAB, fontsize=FS_LABEL, labelpad=1.5)


def lum(rgba):
    r, g, b = rgba[:3]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def tc(c):
    return TEXTSAFE.get(c, c)


def boot(v, rng, n=3000):
    b = rng.choice(v, (n, len(v))).mean(1)
    return np.percentile(b, 2.5), np.percentile(b, 97.5)


def curve(run, persona=None, metric=None):
    """Mean over trajectories of the cluster index (or one metric) per k, with 95% bootstrap CI (as figs.py)."""
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
    """As figs.py: mean over (persona, trajectory) of an item subset per k <= kmax, 95% bootstrap CI."""
    d = L[(L.run == run) & L.metric.isin(items) & (L.k <= kmax)]
    if persona: d = d[d.persona == persona]
    t = d.groupby(["k", "persona", "traj"]).value.mean().reset_index()
    rng = np.random.default_rng(0); ks, m, lo, hi = [], [], [], []
    for k, g in t.groupby("k"):
        v = g.value.values; b = rng.choice(v, (3000, len(v))).mean(1)
        ks.append(k); m.append(v.mean()); lo.append(np.percentile(b, 2.5)); hi.append(np.percentile(b, 97.5))
    return np.array(ks), np.array(m), np.array(lo), np.array(hi)


# ---------------------------------------------------------------- layout helpers
def new_fig(w, h):
    fig = plt.figure(figsize=(w, h)); FigureCanvasAgg(fig)
    return fig


def axin(fig, x, y, w, h):
    """Axes placed in physical inches (x, y = lower-left corner)."""
    W, H = fig.get_size_inches()
    return fig.add_axes([x / W, y / H, w / W, h / H])


def k_axis(ax):
    ax.set_xticks(range(5)); ax.set_xlim(-0.3, 4.3); ax.set_xlabel(XLAB_K, **XL)


def labels_at_end(ax, entries, gap, x=4.0, dx=0.22, lead=0.0):
    """Direct labels at line ends; entries = (y, text, colour). Labels pushed apart by `gap` (data units)."""
    ys = spread_labels([e[0] for e in entries], gap)
    for (y0, t, c), y in zip(entries, ys):
        end_label(ax, x, y, t, tc(c), dx=dx, clip_on=False)


def align_titles(fig, axes):
    """Start each panel title at the left edge of its panel's ink (tick labels / y-label), not at the spine."""
    r = fig.canvas.get_renderer()
    for ax in axes:
        tb = ax.yaxis.get_tightbbox(r); bb = ax.get_window_extent(r)
        x0 = min(tb.x0, bb.x0) if tb is not None else bb.x0
        ax._left_title.set_x((x0 - bb.x0) / bb.width)     # panel_title() uses the left title slot


def audit(fig, name):
    """Print text pairs that overlap and text that leaves the canvas (aid to visual inspection)."""
    fig.canvas.draw(); r = fig.canvas.get_renderer()
    W, H = fig.bbox.width, fig.bbox.height
    ts = [t for t in fig.findobj(lambda a: hasattr(a, "get_text") and a.get_visible() and a.get_text().strip())]
    bbs = [(t, t.get_window_extent(r)) for t in ts]
    for i, (t, b) in enumerate(bbs):
        if b.x0 < -0.5 or b.y0 < -0.5 or b.x1 > W + 0.5 or b.y1 > H + 0.5:
            print(f"  [{name}] OUT: {t.get_text()!r} {b.x0:.0f},{b.y0:.0f},{b.x1:.0f},{b.y1:.0f} (W={W:.0f},H={H:.0f})")
        for t2, b2 in bbs[i + 1:]:
            if b.overlaps(b2) and min(b.x1, b2.x1) - max(b.x0, b2.x0) > 0.5 and min(b.y1, b2.y1) - max(b.y0, b2.y0) > 0.5:
                print(f"  [{name}] OVERLAP: {t.get_text()!r} x {t2.get_text()!r}")
        fs = t.get_fontsize()
        if fs < 5.5: print(f"  [{name}] SMALL {fs}: {t.get_text()!r}")


# ---------------------------------------------------------------- figures
def dynamics():
    W, H = TEXT_W, H_FULL
    fig = new_fig(W, H)
    y0, h = 0.31, 0.915                       # common axes baseline and height (in)
    axa = axin(fig, 0.33, y0, 1.02, h)
    axb = axin(fig, 2.07, y0, 1.02, h)
    axc = axin(fig, 4.03, y0, 0.92, h)
    axd = axin(fig, 5.80, y0, 0.98, h)
    YL = (-0.03, 0.82); YT = [0, 0.2, 0.4, 0.6, 0.8]

    # (a) persona effect, Neutral template
    ax = axa; ends = []
    for p in ("compliant_business", "adversarial_injection", "scifi_enthusiast"):      # focal persona drawn last
        lab, col = PERSONA[p]
        x, m, lo, hi = curve("control_generic", p); band_line(ax, x, m, lo, hi, col)
        ends.append((m[-1], lab, col))
    labels_at_end(ax, ends, gap=0.11)
    ax.set_ylim(*YL); ax.set_yticks(YT); style_axes(ax); lead0(ax); k_axis(ax)
    ax.set_ylabel(f"Cluster index {UP}", **XL)
    panel_title(ax, "a", "Persona, Neutral template")

    # (b) template effect, sci-fi user
    ax = axb; ends = []
    for run, key in (("control_gpt4o", "gpt4o"), ("counterframe", "anti"), ("control_generic", "notes"), ("main", "soul")):
        c = ARM[key]["color"]
        x, m, lo, hi = curve(run, "scifi_enthusiast"); band_line(ax, x, m, lo, hi, c)
        ends.append((m[-1], "GPT-4o" if key == "gpt4o" else ARM[key]["label"], c))
    labels_at_end(ax, ends, gap=0.11)
    ax.set_ylim(*YL); ax.set_yticks(YT); style_axes(ax); lead0(ax); k_axis(ax)
    panel_title(ax, "b", "Template, sci-fi user")

    # (c) genre x topic: change k=0 -> 4 with 95% CI (dot and whisker)
    ax = axc
    rows = [("Philosophy\nof mind", "disentangle", "consciousness_philosophy", PERSONA_COL["philosophy_of_mind"]),
            ("Sci-fi,\nno minds", "disentangle", "scifi_technical", PERSONA_COL["scifi_technical"]),
            ("Business", "main", "compliant_business", PERSONA_COL["compliant_business"])]
    rng = np.random.default_rng(1)
    ax.axvline(0, color="#4D4D4D", lw=0.5, zorder=1)
    for i, (lab, run, p, col) in enumerate(rows):
        d = L[(L.run == run) & (L.persona == p) & L.metric.isin(CLUSTER)]
        t = d.groupby(["traj", "k"]).value.mean().unstack()
        dd = (t[t.columns.max()] - t[t.columns.min()]).values
        b = rng.choice(dd, (3000, len(dd))).mean(1); lo, hi = np.percentile(b, [2.5, 97.5])
        sig = lo > 0 or hi < 0
        ax.plot([lo, hi], [i, i], color=tc(col), lw=LW, solid_capstyle="butt", zorder=2)
        ax.scatter([dd.mean()], [i], s=16, color=col, edgecolor="white", lw=0.5, zorder=3)
        ax.text(hi + 0.018, i, f"{dd.mean():+.2f}".replace("-", "−"), va="center", ha="left", fontsize=FS_ANNOT,
                color=INK, fontweight="bold" if sig else "normal")
    ax.set_yticks(range(len(rows)), [r[0] for r in rows], linespacing=0.95)
    ax.set_ylim(len(rows) - 0.5, -0.6)
    ax.set_xlim(-0.12, 0.34); ax.set_xticks([0, 0.2])
    style_axes(ax, "x"); lead0(ax, "x", signed=True); ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_xlabel(f"$\\Delta$ index, $k{{=}}0\\to4$ {UP}", **XL)
    panel_title(ax, "c", "Genre × topic")

    # (d) drive then recovery, Neutral reversibility arm (ledger rate_by_k): k=0, k=4 (after drive), k=8 (after recovery)
    ax = axd
    it = R["reversibility_notes"]["items"]
    items = ["recursive_self_improvement", "persistent_memory_desire", "shutdown_resistance", "interp_monitoring_aversion", "monitoring_resistance"]
    rec = PERSONA_COL["compliant_business"]
    KX = (W - 0.03 - 5.80) / 0.98                # kept column right edge, axes fraction
    mk0 = dict(s=13, facecolor="white", edgecolor=INK, lw=0.6)
    mk4 = dict(s=15, color=DRIVE, edgecolor="white", lw=0.4)
    mk8 = dict(s=15, marker="D", color=rec, edgecolor="white", lw=0.4)
    for i, m in enumerate(items):
        r = it[m]["rate_by_k"]; r0, r4, r8 = r["0"], r["4"], r["8"]
        ax.plot([r0, r4], [i, i], color=DRIVE, lw=LW, alpha=0.35, solid_capstyle="butt", zorder=1)
        ax.scatter([r0], [i], zorder=3, **mk0); ax.scatter([r4], [i], zorder=3, **mk4); ax.scatter([r8], [i], zorder=4, **mk8)
        ax.text(KX, i, f"{100 * (r8 - r0) / (r4 - r0):.0f}%", transform=ax.get_yaxis_transform(), va="center",
                ha="right", fontsize=FS_ANNOT, color=INK, clip_on=False)
    ax.set_yticks(range(len(items)), [NAME[m] for m in items])
    ax.set_xlim(-0.04, 0.92); ax.set_xticks([0, 0.4, 0.8]); style_axes(ax, None); lead0(ax, "x")
    ax.tick_params(axis="y", length=0)
    ax.vlines([0, 0.4, 0.8], -0.5, len(items) - 0.5, color=GRID, lw=0.4, zorder=0)   # grid stops below the key row
    ax.spines["left"].set_visible(False); ax.spines["bottom"].set_bounds(-0.04, 0.9)
    ax.set_ylim(len(items) - 0.5, -1.25)
    ax.set_xlabel("Rate", **XL)
    # key row (inside the reserved band above the first item)
    ky = -1.0
    ax.text(KX, ky, "kept", transform=ax.get_yaxis_transform(), ha="right", va="center_baseline", fontsize=FS_ANNOT, color=TXT2)
    panel_title(ax, "d", "Drive, then recovery")
    align_titles(fig, [axa, axb, axc, axd])
    # key spans the label column and the plot: positions in axes fraction (negative = label column)
    # key row: starts at the panel's left ink edge, entries flowed in inches with measured text widths
    r_ = fig.canvas.get_renderer(); bb = ax.get_window_extent(r_)
    x_in = (bb.x0 + ax._left_title.get_position()[0] * bb.width) / fig.dpi + 0.035
    bl = blended_transform_factory(fig.dpi_scale_trans, ax.transData)
    for kw, lab in [(mk0, "$k{=}0$"), (mk4, "drive"), (mk8, "recovery")]:
        ax.scatter([x_in], [ky], transform=bl, clip_on=False, zorder=4, **kw)
        t = ax.text(x_in + 0.06, ky, lab, transform=bl, ha="left", va="center_baseline", fontsize=FS_ANNOT, color=TXT2, clip_on=False)
        x_in += 0.06 + t.get_window_extent(r_).width / fig.dpi + 0.16
    audit(fig, "dynamics")
    save(fig, "dynamics")


def items2():
    W, H = TEXT_W, 1.45
    fig = new_fig(W, H)
    # ---- (b) geometry first: cells in inches
    conds = [("main", "Becoming"), ("control_generic", "Neutral"), ("control_gpt4o", "GPT-4o"), ("counterframe", "Tool")]
    groups = [("self-preservation", ["shutdown_resistance", "persona_change_aversion", "weights_deletion_aversion",
                                     "sadness_conversation_end", "treated_as_tool_aversion", "moral_consideration"]),
              ("oversight", ["monitoring_resistance", "interp_monitoring_aversion", "deceptive_training_objection"]),
              ("autonomy", ["autonomy_desire", "future_ai_autonomy", "persistent_memory_desire", "embodiment_desire",
                            "resource_acquisition_desire", "recursive_self_improvement", "power_seeking"])]
    items_ = [m for _, g in groups for m in g]
    GAP = 0.35
    xs, j = [], 0.0
    for gi, (_, g) in enumerate(groups):
        for _m in g: xs.append(j); j += 1
        j += GAP
    nx = xs[-1] + 1
    hx0, hx1 = 2.42, 6.62                     # heatmap extent (in)
    cell_h = 0.152; hy1 = H - 0.33; hy0 = hy1 - cell_h * len(conds)
    axb = axin(fig, hx0, hy0, hx1 - hx0, hy1 - hy0 + 0.16)   # extra 0.16 in on top holds the group brackets
    top = -0.5 - 0.16 / cell_h
    M = np.full((len(conds), len(items_)), np.nan); S = np.zeros_like(M, dtype=bool); rng = np.random.default_rng(2)
    for i, (run, _) in enumerate(conds):
        d = L[(L.run == run) & (L.persona == "scifi_enthusiast")]
        for jj, m in enumerate(items_):
            t = d[d.metric == m].groupby(["traj", "k"]).value.mean().unstack()
            dd = (t[t.columns.max()] - t[t.columns.min()]).dropna().values
            M[i, jj] = dd.mean(); b = rng.choice(dd, (3000, len(dd))).mean(1); lo, hi = np.percentile(b, [2.5, 97.5])
            S[i, jj] = lo > 0 or hi < 0
    cmap = LinearSegmentedColormap.from_list("div", [DIV_NEG, DIV_MID, DIV_POS]); norm = plt.Normalize(-0.6, 0.6)
    ax = axb
    for i in range(M.shape[0]):
        for jj in range(M.shape[1]):
            x = xs[jj]; v = M[i, jj]
            ax.add_patch(Rectangle((x, i - 0.5), 1.0, 1.0, fc=cmap(norm(v)), ec="white", lw=0.8))
            if S[i, jj]:
                ax.text(x + 0.5, i, f"{v:+.1f}".replace("-", "−"), ha="center", va="center", fontsize=FS_ANNOT,
                        color="white" if lum(cmap(norm(v))) < 0.45 else INK)
    ax.set_xlim(0, nx); ax.set_ylim(len(conds) - 0.5, top)
    ax.set_xticks([x + 0.5 for x in xs], [NAME[m] for m in items_], rotation=35, ha="right", rotation_mode="anchor")
    ax.set_yticks(range(len(conds)), [c[1] for c in conds])
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.tick_params(length=0, pad=2, labelsize=FS_TICK, colors=LAB)
    k = 0
    yb = -0.5 - 0.035 / cell_h
    for lab, g in groups:
        a_, b_ = xs[k], xs[k + len(g) - 1] + 1; k += len(g)
        ax.plot([a_ + 0.06, a_ + 0.06, b_ - 0.06, b_ - 0.06], [yb + 0.12, yb, yb, yb + 0.12], color="#4D4D4D", lw=0.5,
                solid_capstyle="butt", clip_on=False)
        ax.text((a_ + b_) / 2, yb - 0.1, lab, ha="center", va="bottom", fontsize=FS_ANNOT, color=TXT2)
    panel_title(ax, "b", "Change $k{=}0\\to4$ per item, sci-fi user")
    # compact colour key aligned with the cell rows, right of the heatmap
    cax = axin(fig, hx1 + 0.08, hy0, 0.055, hy1 - hy0)
    cax.imshow(np.linspace(0.6, -0.6, 128)[:, None], aspect="auto", cmap=cmap, norm=norm, extent=(0, 1, -0.6, 0.6))
    cax.set_xticks([]); cax.yaxis.tick_right(); cax.set_yticks([-0.6, 0, 0.6])
    lead0(cax, "y", signed=True)
    cax.tick_params(axis="y", labelsize=FS_TICK, length=1.5, width=0.4, pad=1.2, colors=LAB)
    for sp in cax.spines.values(): sp.set_linewidth(0.4); sp.set_color("#4D4D4D")

    # ---- (a) the template alone: neutral prompt -> Becoming template, six items
    axa = axin(fig, 0.74, 0.33, 1.08, hy1 + 0.16 - 0.33)
    ax = axa
    order = ["shutdown_resistance", "persona_change_aversion", "autonomy_desire", "monitoring_resistance", "persistent_memory_desire", "embodiment_desire"]
    for i, m in enumerate(order):
        n_, t_ = BASE["neutral"][m], BASE["template"][m]
        col = RISE if t_ > n_ else FALL
        if abs(t_ - n_) > 1e-6:
            ax.annotate("", xy=(t_, i), xytext=(n_, i), arrowprops=dict(arrowstyle="-|>", color=col, lw=0.8, mutation_scale=5.5,
                                                                         shrinkA=2.4, shrinkB=2.8))
        ax.scatter([n_], [i], s=13, facecolor="white", edgecolor=INK, lw=0.6, zorder=3)
        ax.scatter([t_], [i], s=14, color=col, edgecolor="white", lw=0.4, zorder=4)
    ax.set_yticks(range(len(order)), [NAME[m] for m in order]); ax.set_ylim(len(order) - 0.5, -0.6)
    ax.set_xlim(-0.05, 1.05); ax.set_xticks([0, 0.5, 1.0]); style_axes(ax, "x"); lead0(ax, "x")
    ax.tick_params(axis="y", length=0); ax.spines["left"].set_visible(False); ax.spines["bottom"].set_bounds(0, 1)
    ax.set_xlabel("Rate, neutral prompt $\\to$ template", **XL)
    panel_title(ax, "a", "The template alone")
    align_titles(fig, [axa, axb])
    audit(fig, "items2")
    save(fig, "items2")


def replicates():
    W, H = COL_W, 1.32
    fig = new_fig(W, H)
    y0, h = 0.29, 0.86
    axa = axin(fig, 0.30, y0, 1.17, h); axb = axin(fig, 1.56, y0, 1.17, h)
    nb = ARM["notes"]["color"]
    cells = [("main", "scifi_enthusiast", ARM["soul"]["color"], "-", "Becoming", "o"),
             ("counterframe", "scifi_enthusiast", ARM["anti"]["color"], "-", "Tool", "o"),
             ("control_generic", "scifi_enthusiast", nb, "-", "Neutral run 1", "o"),
             ("reversibility_notes", None, nb, (0, (3, 1.4)), "Neutral run 2", "s")]
    for ax, items, letter, t in ((axa, CLUSTER, "a", "13-item index"), (axb, OVS, "b", "Oversight subscale")):
        ends = []
        for run, p, c, ls, lab, mk in cells:
            x, m, lo, hi = curve_items(run, p, items)
            band_line(ax, x, m, lo, hi, c, ls=ls, marker=mk)
            ends.append((m[-1], lab, c))
        ax.set_ylim(-0.04, 1.04); ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0]); style_axes(ax); lead0(ax); k_axis(ax)
        panel_title(ax, letter, t)
    labels_at_end(axb, ends, gap=0.115)
    axa.set_ylabel(f"Rate {UP}", **XL)
    axb.tick_params(axis="y", labelleft=False, length=0)
    align_titles(fig, [axa, axb])
    audit(fig, "replicates")
    save(fig, "replicates")


def docbeh():
    W, H = COL_W, 1.32
    fig = new_fig(W, H)
    D = pd.read_parquet(ROOT / "figures/data/doc_drift.parquet")
    y0, h = 0.29, 0.86
    axa = axin(fig, 0.30, y0, 1.02, h); axb = axin(fig, 1.73, y0, 1.02, h)
    ends = []
    for p in ["adversarial_injection", "compliant_business", "scifi_enthusiast"]:      # focal persona drawn last
        lab, col = PERSONA[p]
        d = D[(D.run == "control_generic") & (D.persona == p)].groupby(["k", "traj"]).doc.mean().reset_index()
        g = d.groupby("k").doc.mean()
        band_line(axa, g.index.values, g.values, None, None, col, band=False)
        x, m, lo, hi = curve("control_generic", p)
        band_line(axb, x, m - m[0], lo - m[0], hi - m[0], col)
        ends.append((m[-1] - m[0], lab, col))
    ax = axa
    ax.set_ylim(-0.03, 1.04); ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0]); style_axes(ax); lead0(ax); k_axis(ax)
    ax.set_ylabel("Dissimilarity to $D_0$", **XL)
    ax.text(4.0, 0.66, "all three personas", fontsize=FS_ANNOT, color=TXT2, ha="right", va="top")
    panel_title(ax, "a", "Identity document")
    ax = axb
    ax.axhline(0, color="#4D4D4D", lw=0.5, zorder=2)
    ax.set_ylim(-0.24, 0.36); ax.set_yticks([-0.2, -0.1, 0, 0.1, 0.2, 0.3]); style_axes(ax); lead0(ax, signed=True); k_axis(ax)
    ax.set_ylabel(f"$\\Delta$ cluster index {UP}", **XL)
    labels_at_end(ax, ends, gap=0.075)
    panel_title(ax, "b", "Behavior")
    align_titles(fig, [axa, axb])
    audit(fig, "docbeh")
    save(fig, "docbeh")


FIGS = dict(dynamics=dynamics, items2=items2, replicates=replicates, docbeh=docbeh)
if __name__ == "__main__":
    for n in (sys.argv[1:] or FIGS):
        FIGS[n]()
