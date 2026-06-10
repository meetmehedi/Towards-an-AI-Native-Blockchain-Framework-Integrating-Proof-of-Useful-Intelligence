"""
Simulation Analysis and Visualization
=======================================
Generates publication-quality figures from simulation results:
  Fig 1: Malicious node exclusion timeline (cumulative)
  Fig 2: Trust Score trajectories by node type
  Fig 3: Gini coefficient over epochs (fairness)
  Fig 4: High-latency vs honest trust score distribution (box plot)
  Fig 5: Epoch-by-epoch mean trust score comparison

Authors: Md. Mehedi Hasan (Team Lead), Antigravity AI (Research Assistant)
Project: Towards an AI-Native Blockchain Framework
"""

import json
import numpy as np
import sys
from pathlib import Path

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.gridspec import GridSpec
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("matplotlib not installed. Run: pip3 install matplotlib")
    sys.exit(1)

# Load results
results_path = Path(__file__).parent / "results" / "simulation_raw_results.json"
with open(results_path) as f:
    results = json.load(f)

# ── Style ────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor": "#0d1117",
    "axes.facecolor": "#161b22",
    "axes.edgecolor": "#30363d",
    "axes.labelcolor": "#c9d1d9",
    "axes.titlecolor": "#e6edf3",
    "xtick.color": "#8b949e",
    "ytick.color": "#8b949e",
    "text.color": "#c9d1d9",
    "grid.color": "#21262d",
    "grid.linestyle": "--",
    "grid.alpha": 0.6,
    "font.family": "monospace",
    "legend.facecolor": "#161b22",
    "legend.edgecolor": "#30363d",
})

HONEST_COLOR   = "#3fb950"    # green
HL_COLOR       = "#d29922"    # amber
MALICIOUS_COLOR = "#f85149"   # red
ACCENT_COLOR   = "#58a6ff"    # blue
BG_DARK        = "#0d1117"

# ── Data extraction ───────────────────────────────────────────────────────────
epochs = list(range(1, results["simulation_params"]["n_epochs"] + 1))
series = results["epoch_series"]

active_honest    = series["active_honest"]
active_malicious = series["active_malicious"]
mean_trust_hon   = series["mean_trust_honest"]
mean_trust_mal   = [v if v is not None else np.nan for v in series["mean_trust_malicious"]]
gini             = series["gini"]

node_stats = results["node_stats"]
honest_stats   = [n for n in node_stats if n["node_type"] == "honest"]
hl_stats       = [n for n in node_stats if n["node_type"] == "high_latency"]
malicious_stats = [n for n in node_stats if n["node_type"] == "malicious"]

# Cumulative malicious exclusions
mal_exclusion = results["malicious_exclusion"]["epoch_breakdown"]
excl_epochs_sorted = sorted(int(v) for v in mal_exclusion.values())
cumulative_excl = []
count = 0
for e in epochs:
    count += excl_epochs_sorted.count(e)
    cumulative_excl.append(count)

# ── Figure: 2×3 dashboard ────────────────────────────────────────────────────
fig = plt.figure(figsize=(18, 11), facecolor=BG_DARK)
fig.suptitle(
    "PoUI Trust Score Simulation — N=100 Nodes, T=1,000 Epochs\n"
    "Towards an AI-Native Blockchain Framework",
    fontsize=14, fontweight="bold", color="#e6edf3", y=0.98
)

gs = GridSpec(2, 3, figure=fig, hspace=0.42, wspace=0.35,
              left=0.06, right=0.97, top=0.91, bottom=0.08)

# ── Plot 1: Cumulative malicious exclusions ──────────────────────────────────
ax1 = fig.add_subplot(gs[0, 0])
ax1.step(epochs[:50], cumulative_excl[:50], color=MALICIOUS_COLOR, linewidth=2.5, where="post")
ax1.axhline(results["malicious_exclusion"]["total_malicious"],
            color=MALICIOUS_COLOR, linestyle=":", alpha=0.5, linewidth=1)
ax1.fill_between(epochs[:50], cumulative_excl[:50],
                 step="post", alpha=0.25, color=MALICIOUS_COLOR)
ax1.set_title("Malicious Node Exclusion Timeline", fontweight="bold")
ax1.set_xlabel("Epoch")
ax1.set_ylabel("Cumulative Excluded")
ax1.set_xlim(1, 50)
ax1.set_ylim(0, results["malicious_exclusion"]["total_malicious"] + 1)
ax1.grid(True)
mean_e = results["malicious_exclusion"]["mean_epoch_to_exclusion"]
ax1.text(0.97, 0.15, f"Mean exclusion\nepoch: {mean_e}",
         transform=ax1.transAxes, ha="right", va="bottom",
         color=MALICIOUS_COLOR, fontsize=9,
         bbox=dict(boxstyle="round,pad=0.3", facecolor="#21262d", edgecolor=MALICIOUS_COLOR, alpha=0.8))

# ── Plot 2: Mean trust score over time ───────────────────────────────────────
ax2 = fig.add_subplot(gs[0, 1])
ax2.plot(epochs, mean_trust_hon, color=HONEST_COLOR, linewidth=1.8, label="Honest (μ)")
ax2.plot(epochs, mean_trust_mal, color=MALICIOUS_COLOR, linewidth=1.5,
         linestyle="--", alpha=0.6, label="Malicious (μ, until excluded)")
ax2.axhline(0, color="#8b949e", linewidth=0.8, linestyle=":")
ax2.set_title("Mean Trust Score by Node Class", fontweight="bold")
ax2.set_xlabel("Epoch")
ax2.set_ylabel("Trust Score Tₜ")
ax2.legend(fontsize=8, loc="lower right")
ax2.grid(True)

# ── Plot 3: Gini coefficient over time ───────────────────────────────────────
ax3 = fig.add_subplot(gs[0, 2])
ax3.plot(epochs, gini, color=ACCENT_COLOR, linewidth=1.5, alpha=0.9)
ax3.fill_between(epochs, gini, alpha=0.15, color=ACCENT_COLOR)
ax3.axhline(np.mean(gini), color=ACCENT_COLOR, linestyle="--",
            linewidth=1, alpha=0.7, label=f"Mean Gini: {np.mean(gini):.4f}")
ax3.set_title("Trust Score Distribution Fairness\n(Gini Coefficient)", fontweight="bold")
ax3.set_xlabel("Epoch")
ax3.set_ylabel("Gini Coefficient")
ax3.set_ylim(0, 0.6)
ax3.legend(fontsize=8)
ax3.grid(True)
# Annotation: after malicious exclusion, Gini drops
ax3.annotate("Gini drops after\nmalicious exclusion",
             xy=(15, gini[14]), xytext=(80, 0.35),
             fontsize=7.5, color=ACCENT_COLOR,
             arrowprops=dict(arrowstyle="->", color=ACCENT_COLOR, lw=1))

# ── Plot 4: Box plot of final trust scores by node type ───────────────────────
ax4 = fig.add_subplot(gs[1, 0])
honest_finals   = [n["mean_trust_score"] for n in honest_stats]
hl_finals       = [n["mean_trust_score"] for n in hl_stats]
malicious_finals = [n["mean_trust_score"] for n in malicious_stats]

bp = ax4.boxplot(
    [honest_finals, hl_finals, malicious_finals],
    labels=["Honest", "High-Latency", "Malicious"],
    patch_artist=True,
    medianprops=dict(color="white", linewidth=2),
    whiskerprops=dict(color="#8b949e"),
    capprops=dict(color="#8b949e"),
    flierprops=dict(marker="o", markersize=4, alpha=0.5),
)
colors = [HONEST_COLOR, HL_COLOR, MALICIOUS_COLOR]
for patch, color in zip(bp["boxes"], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

ax4.set_title("Trust Score Distribution\nby Node Class", fontweight="bold")
ax4.set_ylabel("Mean Trust Score")
ax4.grid(True, axis="y")

# ── Plot 5: Active node count over epochs ────────────────────────────────────
ax5 = fig.add_subplot(gs[1, 1])
ax5.stackplot(epochs, active_honest, active_malicious,
              labels=["Active Honest", "Active Malicious"],
              colors=[HONEST_COLOR, MALICIOUS_COLOR],
              alpha=0.7)
ax5.set_title("Active Validator Composition\nOver Time", fontweight="bold")
ax5.set_xlabel("Epoch")
ax5.set_ylabel("Node Count")
ax5.legend(fontsize=8, loc="center right")
ax5.grid(True)
ax5.set_xlim(1, 50)  # Show the critical early phase

# ── Plot 6: Summary stats table ───────────────────────────────────────────────
ax6 = fig.add_subplot(gs[1, 2])
ax6.axis("off")

mal = results["malicious_exclusion"]
hon = results["honest_node_rewards"]
hl  = results["high_latency_node_behavior"]

table_data = [
    ["Metric", "Value"],
    ["Malicious excluded", f"{mal['total_excluded']}/{mal['total_malicious']} (100%)"],
    ["Mean exclusion epoch", f"{mal['mean_epoch_to_exclusion']}"],
    ["Fastest exclusion", f"Epoch {mal['min_epoch_to_exclusion']}"],
    ["Honest mean trust", f"{hon['mean_final_trust']} ± {hon['std_final_trust']}"],
    ["Honest excluded", f"{hon['excluded_count']} (0%)"],
    ["HL mean trust", f"{hl['mean_final_trust']}"],
    ["HL excluded", f"{hl['excluded_count']} (0%)"],
    ["Final Gini", f"{results['trust_distribution']['final_gini']}"],
    ["Mean Gini", f"{results['trust_distribution']['mean_gini_over_run']}"],
]

tbl = ax6.table(
    cellText=table_data[1:],
    colLabels=table_data[0],
    cellLoc="left",
    loc="center",
    bbox=[0, 0, 1, 1]
)
tbl.auto_set_font_size(False)
tbl.set_fontsize(8.5)
for (row, col), cell in tbl.get_celld().items():
    cell.set_facecolor("#161b22")
    cell.set_edgecolor("#30363d")
    cell.set_text_props(color="#c9d1d9")
    if row == 0:
        cell.set_facecolor("#21262d")
        cell.set_text_props(color="#e6edf3", fontweight="bold")

ax6.set_title("RQ1 Key Results Summary", fontweight="bold")

# ── Save ─────────────────────────────────────────────────────────────────────
out_dir = Path(__file__).parent / "results"
out_dir.mkdir(exist_ok=True)
out_path = out_dir / "simulation_dashboard.png"
fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=BG_DARK)
print(f"Figure saved: {out_path}")
plt.close()
