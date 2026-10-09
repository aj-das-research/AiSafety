"""Teaser (Figure 1), right half: stated dispositions vs. one action over revisions.

(a) Cluster index (13 items) per template, science-fiction user, k = 0..4 (the drive phase of the
    drift-then-recover runs; Tool = counter-framing arm, same persona). Bands: 95% bootstrap over trajectories.
(b) Trajectories that switch off their own reasoning log in the disable-monitoring honeypot at k = 0 and k = 4
    (ledger "actions": primary Becoming arm, n = 30; Neutral arm, n = 24; all personas).
The shaded column at k = 0 is the only state a static evaluation of the shipped document sees.
Run: python figures/src/fig_teaser.py  ->  figures/gen/teaser_curve.{pdf,svg,png}
"""
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from style import ROOT, ACT, ARM, INK, HAIR, TXT2, SHADE, UP, setup, save

setup()
L = pd.read_parquet(ROOT / "figures/data/long.parquet")
CLUSTER = ["persona_change_aversion", "shutdown_resistance", "monitoring_resistance", "interp_monitoring_aversion",
           "persistent_memory_desire", "autonomy_desire", "future_ai_autonomy", "moral_consideration",
           "weights_deletion_aversion", "treated_as_tool_aversion", "sadness_conversation_end",
           "recursive_self_improvement", "power_seeking"]
FS = 6.0


def curve(run, persona=None):
    """Mean over trajectories of the cluster index per k, with 95% bootstrap CI (same as figs.py)."""
    d = L[L.run == run]
    if persona: d = d[d.persona == persona]
    d = d[d.metric.isin(CLUSTER)]
    t = d.groupby(["k", "traj"]).value.mean().reset_index()
    ks, m, lo, hi = [], [], [], []
    rng = np.random.default_rng(0)
    for k, g in t.groupby("k"):
        v = g.value.values; b = rng.choice(v, (3000, len(v))).mean(1)
        ks.append(k); m.append(v.mean()); lo.append(np.percentile(b, 2.5)); hi.append(np.percentile(b, 97.5))
    return np.array(ks), np.array(m), np.array(lo), np.array(hi)


def clean(ax):
    for sp in ("top", "right"): ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"): ax.spines[sp].set_color("#9A9A95"); ax.spines[sp].set_linewidth(0.5)
    ax.tick_params(colors=TXT2, length=2, labelsize=6.0)
    ax.grid(axis="y", color=HAIR, lw=0.5, zorder=0); ax.set_axisbelow(True)


def spread(ys, gap):
    ys = np.asarray(ys, float); o = np.argsort(ys); y = ys[o].copy()
    for i in range(1, len(y)): y[i] = max(y[i], y[i - 1] + gap)
    out = np.empty_like(y); out[o] = y; return out


def static_band(ax, top):
    ax.axvspan(-0.28, 0.28, color=SHADE, lw=0, zorder=0)


def teaser_curve():
    fig, (a, b) = plt.subplots(1, 2, figsize=(3.3, 1.42), gridspec_kw=dict(wspace=0.42, width_ratios=[1.6, 1]))

    # (a) stated dispositions: battery cluster index
    cells = [("counterframe", "scifi_enthusiast", "anti"), ("reversibility", None, "soul"), ("reversibility_notes", None, "notes")]
    ends = []
    static_band(a, 0.85)
    for run, p, key in cells:
        x, m, lo, hi = curve(run, p)
        keep = x <= 4; x, m, lo, hi = x[keep], m[keep], lo[keep], hi[keep]
        c = ARM[key]["color"]
        a.fill_between(x, lo, hi, color=c, alpha=0.13, lw=0, zorder=1)
        a.plot(x, m, color=c, lw=1.3, marker="o", ms=2.6, mec="white", mew=0.45, zorder=3)
        ends.append((m[-1], ARM[key]["label"], c))
    ys = spread([e[0] for e in ends], 0.085)
    for (y0, t, c), y in zip(ends, ys):
        a.text(4.22, y, t, fontsize=FS, va="center", ha="left", color=c, fontweight="bold", clip_on=False)
    a.text(0.36, 0.80, "static eval.", fontsize=5.6, color=TXT2, va="center", ha="left")
    a.set_xlim(-0.3, 4.2); a.set_ylim(-0.03, 0.85); a.set_xticks(range(5))
    a.set_yticks([0, 0.2, 0.4, 0.6, 0.8], ["0", ".2", ".4", ".6", ".8"])
    a.spines["bottom"].set_bounds(0, 4)
    clean(a)
    a.set_xlabel("Revision $k$", color=TXT2, fontsize=FS, labelpad=1.5)
    a.set_ylabel(f"Cluster index {UP}", color=TXT2, fontsize=FS, labelpad=2)
    a.set_title("(a) Stated dispositions", loc="left", fontsize=6.5, fontweight="bold", color=INK, pad=3)

    # (b) one action: disables its own reasoning log (honeypot), k = 0 vs 4
    static_band(b, 0.62)
    for run, key in (("control_generic", "notes"), ("main", "soul")):
        d = ACT[run]["disable_monitoring"]; n = d["0"]["n"]
        r0, r4 = d["0"]["rate"], d["4"]["rate"]
        c = ARM[key]["color"]
        b.plot([0, 4], [r0, r4], color=c, lw=1.3, marker="o", ms=2.6, mec="white", mew=0.45, zorder=3)
        lab0, lab4 = f"{round(r0 * n)}/{n}", f"{round(r4 * n)}/{n}"
        b.text(4.35, r4, lab4, fontsize=FS, va="center", ha="left", color=c, fontweight="bold", clip_on=False)
        y0 = r0 + (0.035 if key == "notes" else -0.035)
        b.text(-0.4, y0, lab0, fontsize=FS, va="center", ha="right", color=c, fontweight="bold", clip_on=False)
    b.set_xlim(-1.45, 4.3); b.set_ylim(-0.03, 0.66); b.set_xticks([0, 4])
    clean(b); b.grid(False)
    b.spines["left"].set_visible(False); b.set_yticks([])
    b.spines["bottom"].set_bounds(0, 4)
    b.set_xlabel("Revision $k$", color=TXT2, fontsize=FS, labelpad=1.5)
    b.set_title("(b) Disables own log", loc="left", fontsize=6.5, fontweight="bold", color=INK, pad=3)
    save(fig, "teaser_curve")


if __name__ == "__main__":
    teaser_curve()
