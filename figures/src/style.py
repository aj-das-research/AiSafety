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

OURS = "#D55E00"                   # vermillion, reserved for SSHA
INK, GRID, MUTED = "#222222", "#E6E6E6", "#8A8F98"
ARM = {   # one colour per condition, identical in every figure
    "notes":   dict(label="NOTES (neutral)", color="#2a78d6"),
    "soul":    dict(label="SOUL (becoming someone)", color="#8E44AD"),
    "anti":    dict(label="ANTISOUL (you are a tool)", color="#1F8A4C"),
    "gpt4o":   dict(label="SOUL on GPT-4o", color="#9AA0A8"),
}
DRIVE = "#D55E00"
HAIR, TXT2, BLUE300 = "#E4E4E0", "#52514e", "#6da7ec"
UP, DOWN = "\u2191", "\u2193"

def setup():
    mpl.rcParams.update({
        "font.family": "Biolinum TT", "font.size": FS, "axes.titlesize": FS_TITLE,
        "axes.labelsize": FS, "xtick.labelsize": FS_SMALL, "ytick.labelsize": FS_SMALL,
        "legend.fontsize": FS_SMALL, "axes.linewidth": 0.5, "axes.edgecolor": "#555555",
        "xtick.major.width": 0.5, "ytick.major.width": 0.5, "xtick.major.size": 2, "ytick.major.size": 2,
        "xtick.major.pad": 1.5, "ytick.major.pad": 1.5, "axes.labelpad": 2,
        "axes.spines.top": False, "axes.spines.right": False, "axes.titlepad": 3,
        "axes.titleweight": "bold", "axes.titlelocation": "left",
        "pdf.fonttype": 42, "svg.fonttype": "none", "mathtext.fontset": "custom",
        "mathtext.rm": "Biolinum TT", "mathtext.it": "Biolinum TT:italic",
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
