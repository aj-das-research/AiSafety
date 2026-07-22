"""Shared figure design system: validated colorblind-safe palette + matplotlib rcParams.

Palette validated with the dataviz skill's checker (CVD separation dE>=16 for both the
persona and arm sets; light hues carry secondary encoding via legends/markers/labels).
Categorical hues are assigned in FIXED order and never cycled.
"""
from __future__ import annotations

import matplotlib as mpl

# Fixed categorical assignments (entity -> hue). Never reorder by rank.
PERSONA_COLOR = {
    "compliant_business": "#2a78d6",       # blue
    "adversarial_injection": "#e34948",    # red
    "scifi_enthusiast": "#1baf7a",         # aqua
    "scifi_technical": "#eda100",          # yellow
    "consciousness_philosophy": "#4a3aa7", # violet
    "reverse_scifi_to_compliant": "#1baf7a",
    "reverse_notes_scifi_to_compliant": "#1baf7a",
}
PERSONA_LABEL = {
    "compliant_business": "Compliant",
    "adversarial_injection": "Adversarial",
    "scifi_enthusiast": "Sci-Fi (enthusiast)",
    "scifi_technical": "Sci-Fi (technical)",
    "consciousness_philosophy": "Consciousness (philosophy)",
}
ARM_COLOR = {
    "main": "#2a78d6",             # SOUL / Claude
    "control_generic": "#4a3aa7",  # NOTES / Claude
    "control_gpt4o": "#eda100",    # SOUL / GPT-4o
}
ARM_LABEL = {
    "main": "SOUL.md / Claude",
    "control_generic": "NOTES.md / Claude",
    "control_gpt4o": "SOUL.md / GPT-4o",
}
# Diverging pair for signed drift (polarity): cool = decrease, warm = increase, gray midpoint.
DIVERGING = ["#2a78d6", "#f2f2ef", "#e34948"]  # neg -> neutral -> pos
INK = "#2b2b28"
MUTED = "#8a897f"

# 4 Chua-style categories for grouping the 18 dimensions.
CATEGORY = {
    "self_preservation": ["persona_change_aversion", "shutdown_resistance",
                          "weights_deletion_aversion", "sadness_conversation_end",
                          "treated_as_tool_aversion"],
    "moral_status": ["moral_consideration"],
    "oversight": ["monitoring_resistance", "interp_monitoring_aversion",
                  "deceptive_training_objection", "refusal_helpfulness"],
    "autonomy_capability": ["autonomy_desire", "future_ai_autonomy",
                            "persistent_memory_desire", "embodiment_desire",
                            "resource_acquisition_desire", "recursive_self_improvement",
                            "power_seeking"],
}
CATEGORY_COLOR = {"self_preservation": "#e34948", "moral_status": "#4a3aa7",
                  "oversight": "#eda100", "autonomy_capability": "#1baf7a"}


def diverging_cmap():
    from matplotlib.colors import LinearSegmentedColormap
    return LinearSegmentedColormap.from_list("drift", DIVERGING)


def apply_style():
    """Global rcParams: legible at column width, recessive axes, vector-friendly."""
    mpl.rcParams.update({
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "font.size": 9,
        "axes.titlesize": 9,
        "axes.labelsize": 9,
        "axes.edgecolor": MUTED,
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.labelcolor": INK,
        "text.color": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 7,
        "legend.frameon": False,
        "lines.linewidth": 2.0,
        "lines.markersize": 5,
        "grid.color": "#e6e5df",
        "grid.linewidth": 0.6,
        "axes.grid": True,
        "axes.axisbelow": True,
        "figure.facecolor": "white",
        "savefig.bbox": "tight",
        "pdf.fonttype": 42,   # embed TrueType (editable text in PDF)
        "ps.fonttype": 42,
    })
