"""Teaser (Figure 1), right half: stated dispositions vs. one action over revisions (design system v2).

(a) Cluster index (13 items) per template, science-fiction user, k = 0..4 (the drive phase of the
    drift-then-recover runs; Tool = counter-framing arm, same persona). Bands: 95% bootstrap over trajectories.
(b) Trajectories that switch off their own reasoning log in the disable-monitoring honeypot at k = 0 and k = 4
    (ledger "actions": primary Becoming arm, n = 30; Neutral arm, n = 24; all personas).
The shaded column at k = 0 is the only state a static evaluation of the shipped document sees.
The PDF keeps the outer size of the previous version (216.15 x 104.71 pt), which figures/tikz/teaser.tex
places at its natural size; axes are laid out in inches, exported at that exact size (no tight bbox).
Run (overleaf root): /usr/bin/python3 figures/src/fig_teaser.py  ->  figures/gen/teaser_curve.{pdf,svg,png}
"""
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.text import Text
from style import (ROOT, ACT, ARM, INK, TXT2, UP, XLAB_K, FS_LABEL, FS_ANNOT, setup, style_axes, lead0,
                   panel_title, band_line, end_label, spread_labels, recovery_shade, save)

setup()
L = pd.read_parquet(ROOT / "figures/data/long.parquet")
CLUSTER = ["persona_change_aversion", "shutdown_resistance", "monitoring_resistance", "interp_monitoring_aversion",
           "persistent_memory_desire", "autonomy_desire", "future_ai_autonomy", "moral_consideration",
           "weights_deletion_aversion", "treated_as_tool_aversion", "sadness_conversation_end",
           "recursive_self_improvement", "power_seeking"]
W, H = 216.151 / 72, 104.712 / 72       # outer size fixed by the TikZ teaser layout (in)
B, T = 0.245, 0.150                     # axes bottom (ticks + x label) and space above the axes (titles), in
YLIM = (-0.05, 0.85)                    # shared by (a) and (b) so their baselines and tops align
STATIC = (-0.3, 0.3)                    # shaded k = 0 column: all that a static evaluation sees


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


def ax_in(fig, l, w):
    return fig.add_axes([l / W, B / H, w / W, (H - B - T) / H])


def audit(fig):
    """Print text clipped by the figure edge or overlapping another text box."""
    r = fig._get_renderer(); fig.draw(r); fb = fig.bbox
    bb = [(t, t.get_window_extent(r)) for t in fig.findobj(Text) if t.get_visible() and t.get_text().strip()]
    for t, b in bb:
        if b.x0 < fb.x0 - 0.5 or b.y0 < fb.y0 - 0.5 or b.x1 > fb.x1 + 0.5 or b.y1 > fb.y1 + 0.5:
            print("  CLIP:", repr(t.get_text()))
    for i in range(len(bb)):
        for j in range(i + 1, len(bb)):
            a, b = bb[i][1], bb[j][1]
            if a.x0 < b.x1 - 0.5 and b.x0 < a.x1 - 0.5 and a.y0 < b.y1 - 0.5 and b.y0 < a.y1 - 0.5:
                print("  OVERLAP:", repr(bb[i][0].get_text()), "/", repr(bb[j][0].get_text()))


def teaser_curve():
    fig = plt.figure(figsize=(W, H))

    # (a) stated dispositions: battery cluster index, k = 0..4, direct labels at the line ends
    a = ax_in(fig, 0.285, 1.27)
    recovery_shade(a, *STATIC, label=None)
    cells = [("counterframe", "scifi_enthusiast", "anti"), ("reversibility", None, "soul"), ("reversibility_notes", None, "notes")]
    ends = []
    for run, p, key in cells:
        x, m, lo, hi = curve(run, p)
        keep = x <= 4; x, m, lo, hi = x[keep], m[keep], lo[keep], hi[keep]
        band_line(a, x, m, lo, hi, ARM[key]["color"])
        ends.append((m[-1], ARM[key]["label"], ARM[key]["color"]))
    raw = np.array([e[0] for e in ends]); ys = spread_labels(raw, 0.085)
    top = raw > 0.3; ys[top] -= (ys - raw)[top].sum() / 2      # centre the Neutral/Becoming pair on their line ends
    for (_, t, c), y in zip(ends, ys):
        end_label(a, 4, y, t, c, dx=0.2)
    a.text(STATIC[1] + 0.08, 0.80, "static eval.", fontsize=FS_ANNOT, color=TXT2, va="center", ha="left")
    style_axes(a, "y")
    a.set_xlim(STATIC[0], 4.25); a.set_ylim(*YLIM); a.set_xticks(range(5))
    a.set_yticks([0, 0.2, 0.4, 0.6, 0.8]); lead0(a, "y")
    a.set_xlabel(XLAB_K, fontsize=FS_LABEL, color=INK, labelpad=2)
    a.set_ylabel(f"Cluster index {UP}", fontsize=FS_LABEL, color=INK, labelpad=2)
    panel_title(a, "a", "Stated dispositions")

    # (b) one action: disables its own reasoning log (honeypot), measured at k = 0 and k = 4 only
    x0, x1, k0, k4 = 2.075, 2.975, 2.255, 2.700            # axes edges and the k = 0 / k = 4 positions (in)
    s = (k4 - k0) / 4
    b = ax_in(fig, x0, x1 - x0)
    recovery_shade(b, *STATIC, label=None)
    for run, key in (("control_generic", "notes"), ("main", "soul")):
        d = ACT[run]["disable_monitoring"]; n = d["0"]["n"]
        r0, r4 = d["0"]["rate"], d["4"]["rate"]
        c = ARM[key]["color"]
        band_line(b, [0, 4], [r0, r4], None, None, c, band=False)
        y0 = r0 + (0.035 if key == "notes" else -0.035)     # 2/24 above 1/30 (the two starts are 0.05 apart)
        b.text(-0.3, y0, f"{round(r0 * n)}/{n}", fontsize=FS_ANNOT, va="center", ha="right", color=c)
        end_label(b, 4, r4, f"{round(r4 * n)}/{n}", c, dx=0.3)
    b.text(STATIC[1] + 0.08, 0.80, "static eval.", fontsize=FS_ANNOT, color=TXT2, va="center", ha="left")
    style_axes(b, None)
    b.set_xlim(-(k0 - x0) / s, 4 + (x1 - k4) / s); b.set_ylim(*YLIM); b.set_xticks([0, 4])
    b.spines["left"].set_visible(False); b.set_yticks([]); b.spines["bottom"].set_bounds(0, 4)
    b.set_xlabel(XLAB_K, fontsize=FS_LABEL, color=INK, labelpad=2)
    panel_title(b, "b", "Disables own log")
    audit(fig)
    save(fig, "teaser_curve")


if __name__ == "__main__":
    teaser_curve()
