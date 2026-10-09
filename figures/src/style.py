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
FS, FS_TITLE, FS_SMALL = 6.5, 7.5, 5.8

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
        "font.family": fam, "font.size": FS, "axes.titlesize": FS_TITLE,
        "axes.labelsize": FS, "xtick.labelsize": FS_SMALL, "ytick.labelsize": FS_SMALL,
        "legend.fontsize": FS_SMALL, "axes.linewidth": 0.5, "axes.edgecolor": "#555555",
        "xtick.major.width": 0.5, "ytick.major.width": 0.5, "xtick.major.size": 2, "ytick.major.size": 2,
        "xtick.major.pad": 1.5, "ytick.major.pad": 1.5, "axes.labelpad": 2,
        "axes.spines.top": False, "axes.spines.right": False, "axes.titlepad": 3,
        "axes.titleweight": "bold", "axes.titlelocation": "left",
        "pdf.fonttype": 42, "svg.fonttype": "none", "mathtext.fontset": "custom",
        "mathtext.rm": fam, "mathtext.it": fam + ":italic",
        "legend.frameon": False, "legend.handletextpad": 0.3, "legend.columnspacing": 0.9,
        "legend.borderaxespad": 0.2, "lines.linewidth": 0.9,
    })

def grid(ax, axis="x"):
    ax.grid(axis=axis, color=GRID, lw=0.5, zorder=0); ax.set_axisbelow(True)

def panel_title(ax, letter, text):
    ax.set_title(f"({letter}) {text}", fontsize=FS_TITLE, fontweight="bold", loc="left", color=INK)

def save(fig, name):
    GEN.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "svg", "png"):
        fig.savefig(GEN / f"{name}.{ext}", dpi=300 if ext == "png" else None, bbox_inches="tight", pad_inches=0.01, transparent=name.startswith("teaser"))
    plt.close(fig)
    print("saved", name)
