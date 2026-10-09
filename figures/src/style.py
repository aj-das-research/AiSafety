"""One style registry for every figure in the paper (AAMAS sigconf geometry)."""
import json, pathlib
import matplotlib as mpl
mpl.use("pdf")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[2]
GEN = ROOT / "figures/gen"
LEDGER = json.load(open(ROOT / "figures/data/ledger.json"))
R = LEDGER["runs"]; ACT = LEDGER["actions"]; BASE = LEDGER["baselines"]
COL_W, TEXT_W = 3.33, 7.0          # inches, aamas.cls sigconf
# ---- Paper design system v2 (lead-owned; every figure script must use these) ----
# Type scale at PRINT size (figures are exported at their exact final width):
FS_TICK, FS_LABEL, FS_TITLE, FS_ANNOT, FS_MIN = 6.0, 6.5, 7.0, 6.0, 5.5
FS, FS_SMALL = FS_LABEL, FS_TICK              # legacy aliases
H_FULL, H_COL = 1.42, 1.32                    # default heights (in) for one-row full-width / column figures
LW, LW_THIN, MS, BAND_ALPHA = 1.1, 0.6, 3.0, 0.14
XLAB_K = "Revision $k$"                       # one x-label for every over-revisions axis

# ---- Shared palette (lead-defined; figure agents must NOT edit) -----------------
# Restrained, colour-blind-safe (Okabe-Ito / ColorBrewer), print-friendly.
INK, GRID, MUTED = "#1A1A1A", "#E9E9E9", "#8C8C8C"
NEUTRAL, BECOMING, TOOL, GPT4O = "#D55E00", "#0072B2", "#009E73", "#9A9A9A"
ARM = {   # one colour per template condition, identical in every figure
    "notes":   dict(label="Neutral", color=NEUTRAL),
    "soul":    dict(label="Becoming", color=BECOMING),
    "anti":    dict(label="Tool", color=TOOL),
    "gpt4o":   dict(label="Becoming, GPT-4o", color=GPT4O),
}
# Personas: encoded separately from templates (wine accent for the on-theme persona, greys otherwise).
PERSONA_COL = {"scifi_enthusiast": "#882255", "compliant_business": "#8C8C8C", "adversarial_injection": "#1A1A1A",
               "philosophy_of_mind": "#CC6677", "scifi_technical": "#BDBDBD"}
DIV_NEG, DIV_MID, DIV_POS = "#2166AC", "#F7F7F7", "#B2182B"   # diverging maps (RdBu ends)
RISE, FALL = "#B2182B", "#8C8C8C"                              # direction-of-change arrows
SHADE = "#F0F0F0"                                              # recovery-phase / band shading
OURS = NEUTRAL; DRIVE = "#882255"
HAIR, TXT2, BLUE300 = "#E9E9E9", "#4D4D4D", "#6da7ec"
UP, DOWN = "\u2191", "\u2193"

def _register_fonts():
    """Use Linux Biolinum (the sans of the Libertine body) when installed."""
    import glob, os
    from matplotlib import font_manager as fm
    for f in glob.glob(os.path.expanduser("~/.fonts/biolinum-ttf/*.ttf")):
        fm.fontManager.addfont(f)
    names = {f.name for f in fm.fontManager.ttflist}
    return "Linux Biolinum O" if "Linux Biolinum O" in names else "DejaVu Sans"

def setup():
    fam = _register_fonts()
    mpl.rcParams.update({
        "font.family": fam, "font.size": FS_LABEL, "axes.titlesize": FS_TITLE,
        "axes.labelsize": FS_LABEL, "xtick.labelsize": FS_TICK, "ytick.labelsize": FS_TICK,
        "legend.fontsize": FS_TICK, "axes.labelcolor": "#333333", "axes.linewidth": 0.5, "axes.edgecolor": "#555555",
        "xtick.major.width": 0.5, "ytick.major.width": 0.5, "xtick.major.size": 2, "ytick.major.size": 2,
        "xtick.major.pad": 1.5, "ytick.major.pad": 1.5, "axes.labelpad": 2,
        "axes.spines.top": False, "axes.spines.right": False, "axes.titlepad": 3,
        "axes.titleweight": "bold", "axes.titlelocation": "left",
        "pdf.fonttype": 42, "svg.fonttype": "none", "mathtext.fontset": "custom",
        "mathtext.rm": fam, "mathtext.it": fam + ":italic",
        "legend.frameon": False, "legend.handletextpad": 0.3, "legend.columnspacing": 0.9,
        "legend.borderaxespad": 0.2, "lines.linewidth": 0.9,
    })

def grid(ax, axis="y"):
    ax.grid(axis=axis, color=GRID, lw=0.4, zorder=0); ax.set_axisbelow(True)

def style_axes(ax, grid_axis="y"):
    """Left/bottom spines only, thin, quiet ticks; optional faint grid."""
    for sp in ("top", "right"): ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"): ax.spines[sp].set_linewidth(0.5); ax.spines[sp].set_color("#4D4D4D")
    ax.tick_params(colors="#333333", labelsize=FS_TICK, length=2, width=0.5, pad=1.5)
    if grid_axis: grid(ax, grid_axis)

def lead0(ax, axis="y", decimals=1, signed=False):
    """Tick labels with leading zeros (0.4, not .4); signed=True gives +0.2 / -0.2."""
    from matplotlib.ticker import FuncFormatter
    def f(v, _):
        if abs(v) < 1e-9: return "0"
        t = f"{v:+.{decimals}f}" if signed else f"{v:.{decimals}f}"
        return t.replace("-", "\u2212")
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(FuncFormatter(f))

def panel_title(ax, letter, text):
    """'(a) Title' left-aligned, bold, ink; identical in every figure."""
    ax.set_title(f"({letter}) {text}" if letter else text, fontsize=FS_TITLE, fontweight="bold", loc="left", color=INK, pad=3)

def band_line(ax, x, m, lo, hi, color, lw=LW, marker="o", ls="-", label=None, z=3, band=True):
    if band and lo is not None: ax.fill_between(x, lo, hi, color=color, alpha=BAND_ALPHA, lw=0, zorder=z - 1)
    ax.plot(x, m, color=color, lw=lw, ls=ls, marker=marker, ms=MS, mec="white", mew=0.4, label=label, zorder=z)

def end_label(ax, x, y, text, color, dx=0.12, **kw):
    """Direct label at a line end (use instead of legends)."""
    ax.text(x + dx, y, text, color=color, fontsize=FS_ANNOT, va="center", ha="left", **kw)

def spread_labels(ys, gap):
    """Return y positions pushed apart by at least `gap`, preserving order."""
    import numpy as _np
    order = _np.argsort(ys); out = _np.array(ys, float)
    for i in range(1, len(order)):
        a, b = order[i - 1], order[i]
        if out[b] - out[a] < gap: out[b] = out[a] + gap
    return out

def recovery_shade(ax, x0, x1, label="recovery", y=None):
    ax.axvspan(x0, x1, color=SHADE, lw=0, zorder=0)
    if label:
        yy = ax.get_ylim()[1] if y is None else y
        ax.text((x0 + x1) / 2, yy, label, ha="center", va="bottom", fontsize=FS_MIN, color="#6E6E6E", style="italic")

def save(fig, name, tight=False):
    """Export at EXACT figure size (tight=False) so LaTeX does not rescale fonts."""
    GEN.mkdir(parents=True, exist_ok=True)
    kw = dict(bbox_inches="tight", pad_inches=0.01) if tight else {}
    for ext in ("pdf", "svg", "png"):
        fig.savefig(GEN / f"{name}.{ext}", dpi=300 if ext == "png" else None, transparent=False, **kw)
    plt.close(fig)
    print("saved", name, "%.2f x %.2f in" % tuple(fig.get_size_inches()))
