"""Build the two-panel summary figure used in the README from the CSVs in results/.

Run from the repository root:

    python figures/make_readme_figure.py

Left panel. Held-out log-loss for the item-response models compared in the paper.
Right panel. Family-wise developer DIF flags under the single score and under the
scoped scores.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
OUT = ROOT / "figures" / "readme_summary.png"

BLUE = "#2a78d6"
ORANGE = "#eb6834"
INK = "#0b0b0b"
MUTED = "#52514e"
GRID = "#e6e6e3"
SURFACE = "#ffffff"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.edgecolor": GRID,
    "axes.labelcolor": INK,
    "xtick.color": MUTED,
    "ytick.color": INK,
    "text.color": INK,
})

# ---------------------------------------------------------------- left panel
fit = pd.concat([
    pd.read_csv(RESULTS / "harmbench_all_model_holdout_comparison.csv"),
    pd.read_csv(RESULTS / "harmbench_all_model_holdout_comparison_with_domain7.csv"),
]).drop_duplicates("model").set_index("model")
order = [
    ("unidimensional_2pl", "Unidimensional 2PL"),
    ("unidimensional_3pl", "Unidimensional 3PL"),
    ("exploratory_2d_2pl", "Exploratory 2D"),
    ("exploratory_5d_2pl", "Exploratory 5D"),
    ("exploratory_10d_2pl", "Exploratory 10D"),
    ("confirmatory_3d_2pl", "Confirmatory 3D"),
    ("confirmatory_domain7_2pl", "Confirmatory 7D"),
]
labels = [name for _, name in order]
values = [fit.loc[key, "holdout_log_loss_mean"] for key, _ in order]

# --------------------------------------------------------------- right panel
mh = pd.read_csv(RESULTS / "harmbench_mh_dif_flag_summary_with_domain7.csv")
lg = pd.read_csv(RESULTS / "harmbench_logistic_dif_flag_summary_with_domain7.csv")
dev = "developer:OpenAI_vs_Anthropic"
mh = mh[mh["comparison"] == dev].set_index("scope")["fwer_q95_flags"]
mh_single = int(mh["unidimensional_harmbench"])
mh_3d = int(mh[[s for s in mh.index if s.startswith("simple3_")]].sum())
mh_7d = int(mh[[s for s in mh.index if s.startswith("domain7_")]].sum())
lg = lg[lg["comparison"] == dev].reset_index(drop=True)["fwer_flags"]
# Row order in the logistic CSV: ALL, then the three response-process scopes, then the seven harm domains.
lg_single = int(lg.iloc[0])
lg_3d = int(lg.iloc[1:4].sum())
lg_7d = int(lg.iloc[4:11].sum())
scopes = ["Single score", "3D scopes", "7D scopes"]
mh_vals = [mh_single, mh_3d, mh_7d]
lg_vals = [lg_single, lg_3d, lg_7d]

# --------------------------------------------------------------------- draw
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2), facecolor=SURFACE, gridspec_kw={"width_ratios": [1.25, 1], "wspace": 0.35})

ax1.set_facecolor(SURFACE)
y = range(len(labels))
ax1.barh(y, values, color=BLUE, height=0.55)
ax1.set_yticks(list(y))
ax1.set_yticklabels(labels)
ax1.invert_yaxis()
ax1.set_xlim(0, 0.55)
ax1.set_xlabel("Held-out log-loss, mean over five splits. Lower is better.", color=MUTED)
for yi, v in zip(y, values):
    ax1.text(v + 0.008, yi, f"{v:.3f}", va="center", ha="left", fontsize=9, color=INK)
ax1.xaxis.grid(True, color=GRID, linewidth=0.8)
ax1.set_axisbelow(True)
for side in ("top", "right", "left"):
    ax1.spines[side].set_visible(False)
ax1.tick_params(axis="y", length=0)
ax1.set_title("One dimension is too few", loc="left", fontsize=12, fontweight="bold", pad=10)

ax2.set_facecolor(SURFACE)
x = range(len(scopes))
w = 0.36
b1 = ax2.bar([i - w / 2 for i in x], mh_vals, width=w, color=BLUE, label="Mantel-Haenszel")
b2 = ax2.bar([i + w / 2 for i in x], lg_vals, width=w, color=ORANGE, label="Ridge logistic")
for bars in (b1, b2):
    for bar in bars:
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3, f"{int(bar.get_height())}", ha="center", va="bottom", fontsize=9, color=INK)
ax2.set_xticks(list(x))
ax2.set_xticklabels(scopes)
ax2.set_ylim(0, 20)
ax2.set_yticks(range(0, 21, 5))
ax2.set_ylabel("Family-wise DIF flags, OpenAI vs Anthropic", color=MUTED)
ax2.yaxis.grid(True, color=GRID, linewidth=0.8)
ax2.set_axisbelow(True)
for side in ("top", "right"):
    ax2.spines[side].set_visible(False)
ax2.tick_params(axis="x", length=0)
ax2.legend(frameon=False, loc="upper right", fontsize=9)
ax2.set_title("Developer DIF mostly disappears under scoped scores", loc="left", fontsize=12, fontweight="bold", pad=10)

fig.savefig(OUT, dpi=200, bbox_inches="tight", facecolor=SURFACE)
print("wrote", OUT)
