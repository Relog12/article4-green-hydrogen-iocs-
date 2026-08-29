
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

# ── PALETA DE CORES (acessível a daltónicos — Wong 2011) ──
COLORS = {
    "Shell":          "#E69F00",
    "TotalEnergies":  "#56B4E9",
    "BP":             "#009E73",
    "Eni":            "#F0E442",
    "Repsol":         "#CC79A7",
    "EU_ETS":         "#CC0000",
    "target":         "#CC0000",
    "STEPS":          "#D55E00",
    "APS":            "#E69F00",
    "NZE":            "#009E73",
    "gray_light":     "#F5F5F5",
    "gray_mid":       "#999999",
    "gray_dark":      "#333333",
}

FIRMS        = ["Shell", "TotalEnergies", "BP", "Eni", "Repsol"]
FIRM_COLORS  = [COLORS[f] for f in FIRMS]
FIRM_MARKERS = ["o", "s", "^", "D", "v"]

FIG_SIZES = {
    "single_col":   (3.46, 2.80),
    "double_col":   (7.09, 3.50),
    "double_tall":  (7.09, 5.00),
    "two_panel":    (7.09, 3.00),
    "triple_panel": (7.09, 2.80),
}

def apply_style():
    mpl.rcParams.update({
        "font.family":           "serif",
        "font.size":             10,
        "axes.titlesize":        13,
        "axes.labelsize":        11,
        "xtick.labelsize":        9,
        "ytick.labelsize":        9,
        "legend.fontsize":        9,
        "legend.title_fontsize": 10,
        "figure.titlesize":      14,
        "lines.linewidth":        1.8,
        "lines.markersize":       7,
        "axes.linewidth":         0.8,
        "axes.spines.top":        False,
        "axes.spines.right":      False,
        "axes.grid":              True,
        "grid.alpha":             0.3,
        "grid.linewidth":         0.5,
        "grid.linestyle":         "--",
        "axes.axisbelow":         True,
        "savefig.dpi":            300,
        "figure.facecolor":       "white",
        "axes.facecolor":         "white",
        "legend.frameon":         True,
        "legend.framealpha":      0.9,
        "legend.edgecolor":       "#CCCCCC",
    })

def label_panel(ax, letter, x=-0.12, y=1.05, fontsize=13):
    ax.text(x, y, f"({letter})",
            transform=ax.transAxes,
            fontsize=fontsize, fontweight="bold",
            va="top", ha="left")

def save_fig(fig, name, results_dir):
    from pathlib import Path
    base = Path(results_dir) / name
    fig.savefig(str(base) + ".png", dpi=300,
                bbox_inches="tight", facecolor="white")
    fig.savefig(str(base) + ".pdf",
                bbox_inches="tight", facecolor="white")
    print(f"  ✅ Guardado: {name}.png + {name}.pdf")

print("✅ article4_style.py criado com sucesso!")
