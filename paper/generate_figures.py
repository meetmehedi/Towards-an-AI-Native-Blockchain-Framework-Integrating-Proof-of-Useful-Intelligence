"""
Generate all paper figures — PQC benchmarks, architecture diagram, ZKML taxonomy.
"""
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
from pathlib import Path

BG    = "#0d1117"
PANEL = "#161b22"
EDGE  = "#30363d"
TXT   = "#c9d1d9"
TXT_H = "#e6edf3"
GRID  = "#21262d"

C_HONEST   = "#3fb950"
C_MAL      = "#f85149"
C_ACCENT   = "#58a6ff"
C_AMBER    = "#d29922"
C_PURPLE   = "#bc8cff"
C_TEAL     = "#39d353"

plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": PANEL,
    "axes.edgecolor": EDGE, "axes.labelcolor": TXT,
    "axes.titlecolor": TXT_H, "xtick.color": "#8b949e",
    "ytick.color": "#8b949e", "text.color": TXT,
    "grid.color": GRID, "grid.linestyle": "--", "grid.alpha": 0.6,
    "font.family": "sans-serif", "legend.facecolor": PANEL,
    "legend.edgecolor": EDGE,
})

out_dir = Path(__file__).parent / "figures"
out_dir.mkdir(exist_ok=True)


# ═══════════════════════════════════════════════════════════════════
# FIGURE 1: PQC Overhead Dashboard
# ═══════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(16, 9), facecolor=BG)
fig.suptitle("PQC Overhead Analysis — ML-DSA / ML-KEM vs Classical Baselines\n"
             "Towards an AI-Native Blockchain Framework (RQ3)",
             fontsize=13, fontweight="bold", color=TXT_H, y=0.98)
gs = GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.38,
              left=0.07, right=0.97, top=0.90, bottom=0.09)

schemes_dsa = ["ECDSA-P256", "Ed25519", "ML-DSA-44", "ML-DSA-65", "ML-DSA-87"]
sig_bytes   = [64, 64, 2420, 3293, 4595]
pk_bytes    = [64, 32, 1312, 1952, 2592]
verify_us   = [170, 130, 83, 122, 164]
sign_us     = [70, 49, 195, 309, 431]
colors_bar  = [C_ACCENT, C_ACCENT, C_MAL, C_AMBER, C_PURPLE]

# ── Plot 1: Signature sizes ──────────────────────────────────────
ax1 = fig.add_subplot(gs[0, 0])
bars = ax1.bar(schemes_dsa, sig_bytes, color=colors_bar, alpha=0.85, edgecolor=EDGE, linewidth=0.8)
ax1.set_title("Signature Size Comparison", fontweight="bold", fontsize=10)
ax1.set_ylabel("Bytes")
ax1.set_yscale("log")
ax1.tick_params(axis='x', rotation=30, labelsize=7.5)
ax1.grid(True, axis='y')
for bar, val in zip(bars, sig_bytes):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() * 1.1,
             f"{val:,}", ha='center', va='bottom', fontsize=7, color=TXT)
ax1.axhline(64, color=C_ACCENT, linestyle=':', alpha=0.5, linewidth=1, label="Ed25519 baseline")
ax1.legend(fontsize=7)

# ── Plot 2: Verify CPU time ──────────────────────────────────────
ax2 = fig.add_subplot(gs[0, 1])
bars2 = ax2.bar(schemes_dsa, verify_us, color=colors_bar, alpha=0.85, edgecolor=EDGE, linewidth=0.8)
ax2.set_title("Verify Time (µs) per Signature", fontweight="bold", fontsize=10)
ax2.set_ylabel("Microseconds (µs)")
ax2.tick_params(axis='x', rotation=30, labelsize=7.5)
ax2.grid(True, axis='y')
for bar, val in zip(bars2, verify_us):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
             f"{val}", ha='center', va='bottom', fontsize=7, color=TXT)
ax2.text(0.97, 0.92, "ML-DSA-44\nFASTER than Ed25519\nfor verify!",
         transform=ax2.transAxes, ha='right', va='top', fontsize=7.5,
         color=C_TEAL, bbox=dict(boxstyle='round,pad=0.3', fc=PANEL, ec=C_TEAL, alpha=0.9))

# ── Plot 3: TPS block overhead (3 TPS levels for ML-DSA-44) ──────
ax3 = fig.add_subplot(gs[0, 2])
tps_levels = ["100 TPS", "1,000 TPS", "10,000 TPS"]
overhead_naive = [355.08, 355.08, 355.08]       # KB — TPS doesn't change per-block sig overhead
overhead_m1    = [202.4/1, 202.4/1, 202.4/1]    # With aggregate signatures
overhead_m3    = [216.9, 216.9, 216.9]           # With Merkle

x = np.arange(len(tps_levels))
w = 0.25
ax3.bar(x - w, overhead_naive, w, label="Naïve", color=C_MAL, alpha=0.8, edgecolor=EDGE)
ax3.bar(x,     overhead_m1,    w, label="M1 Aggregate", color=C_ACCENT, alpha=0.8, edgecolor=EDGE)
ax3.bar(x + w, overhead_m3,    w, label="M3 Merkle", color=C_AMBER, alpha=0.8, edgecolor=EDGE)
ax3.set_title("ML-DSA-44 Block Overhead\n(N=100 validators)", fontweight="bold", fontsize=10)
ax3.set_ylabel("Overhead (KB/block)")
ax3.set_xticks(x); ax3.set_xticklabels(tps_levels, fontsize=8)
ax3.legend(fontsize=7)
ax3.grid(True, axis='y')

# ── Plot 4: KEM performance ──────────────────────────────────────
ax4 = fig.add_subplot(gs[1, 0])
kem_names    = ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"]
encaps_us    = [29, 43, 62]
decaps_us    = [26, 39, 56]
x2 = np.arange(len(kem_names))
ax4.bar(x2 - 0.2, encaps_us, 0.4, label="Encapsulate", color=C_ACCENT, alpha=0.8, edgecolor=EDGE)
ax4.bar(x2 + 0.2, decaps_us, 0.4, label="Decapsulate", color=C_PURPLE, alpha=0.8, edgecolor=EDGE)
ax4.set_title("ML-KEM Key Encapsulation\nOverhead (µs)", fontweight="bold", fontsize=10)
ax4.set_ylabel("Microseconds")
ax4.set_xticks(x2); ax4.set_xticklabels(kem_names, fontsize=8, rotation=15)
ax4.legend(fontsize=7)
ax4.grid(True, axis='y')

# ── Plot 5: Signature size amplification radar-style bar ─────────
ax5 = fig.add_subplot(gs[1, 1])
dsa_names = ["ML-DSA-44", "ML-DSA-65", "ML-DSA-87"]
amp_sig  = [37.8, 51.5, 71.8]
amp_pk   = [41.0, 61.0, 81.0]
x3 = np.arange(len(dsa_names))
ax5.bar(x3 - 0.2, amp_sig, 0.4, label="Sig Amplification×", color=C_MAL, alpha=0.8, edgecolor=EDGE)
ax5.bar(x3 + 0.2, amp_pk,  0.4, label="PK Amplification×",  color=C_AMBER, alpha=0.8, edgecolor=EDGE)
ax5.set_title("Size Amplification vs Ed25519", fontweight="bold", fontsize=10)
ax5.set_ylabel("× Ed25519")
ax5.set_xticks(x3); ax5.set_xticklabels(dsa_names, fontsize=8)
ax5.legend(fontsize=7)
ax5.grid(True, axis='y')
ax5.axhline(1, color=C_ACCENT, linestyle=':', alpha=0.5, linewidth=1)

# ── Plot 6: Mitigation comparison ───────────────────────────────
ax6 = fig.add_subplot(gs[1, 2])
ax6.axis("off")
mit_data = [
    ["ID", "Strategy", "Reduction", "Feasibility"],
    ["M1", "Aggregate Sigs", "~100×", "2025-2027"],
    ["M2", "Hybrid (Layered)", "~80%", "Immediate"],
    ["M3", "Merkle Batching", "~log(n)×", "Medium-term"],
    ["M4", "FPGA/ASIC", "10-50×", "2027+"],
]
tbl = ax6.table(cellText=mit_data[1:], colLabels=mit_data[0],
                cellLoc="center", loc="center", bbox=[0, 0, 1, 1])
tbl.auto_set_font_size(False); tbl.set_fontsize(8)
for (r, c), cell in tbl.get_celld().items():
    cell.set_facecolor(PANEL); cell.set_edgecolor(EDGE)
    cell.set_text_props(color=TXT)
    if r == 0:
        cell.set_facecolor("#21262d")
        cell.set_text_props(color=TXT_H, fontweight="bold")
ax6.set_title("Architectural Mitigations", fontweight="bold", fontsize=10)

fig.savefig(out_dir / "fig_pqc_benchmarks.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print(f"Saved: {out_dir}/fig_pqc_benchmarks.png")


# ═══════════════════════════════════════════════════════════════════
# FIGURE 2: ZKML Vulnerability Taxonomy Visual
# ═══════════════════════════════════════════════════════════════════
fig2, ax = plt.subplots(figsize=(14, 7), facecolor=BG)
ax.set_facecolor(BG)
ax.axis("off")
fig2.suptitle("ZKML Underconstrained Circuit Vulnerability Taxonomy (RQ2)\n"
              "Towards an AI-Native Blockchain Framework",
              fontsize=13, fontweight="bold", color=TXT_H)

vuln_data = [
    ("V-I",   "Under-Range\nConstraint",      "Low",    "ReLU, Sigmoid,\nSoftmax int8",   C_MAL),
    ("V-II",  "Non-Deterministic\nWitness",   "Medium", "ArgMax, TopK,\nAttention",       C_AMBER),
    ("V-III", "Missing\nIntermediate",         "High",   "All layers,\nResidual",          C_PURPLE),
    ("V-IV",  "Float Approx\nExploit",         "High",   "Quantized\nConv/Linear",         "#79c0ff"),
    ("V-V",   "Commitment-\nOutput Mismatch", "Low",    "Weight Loading,\nAll Tensors",   C_MAL),
]

for i, (vid, name, complexity, layers, color) in enumerate(vuln_data):
    x0 = 0.05 + i * 0.19
    # Main box
    rect = mpatches.FancyBboxPatch((x0, 0.35), 0.16, 0.50,
                                    boxstyle="round,pad=0.02",
                                    facecolor=color, alpha=0.15,
                                    edgecolor=color, linewidth=2,
                                    transform=ax.transAxes)
    ax.add_patch(rect)
    # Class ID
    ax.text(x0 + 0.08, 0.81, vid, ha='center', va='center',
            fontsize=16, fontweight='bold', color=color, transform=ax.transAxes)
    # Name
    ax.text(x0 + 0.08, 0.72, name, ha='center', va='center',
            fontsize=8.5, color=TXT_H, transform=ax.transAxes)
    # Complexity badge
    badge_color = C_MAL if complexity == "High" else (C_AMBER if complexity == "Medium" else C_TEAL)
    badge = mpatches.FancyBboxPatch((x0 + 0.02, 0.57), 0.12, 0.07,
                                     boxstyle="round,pad=0.01",
                                     facecolor=badge_color, alpha=0.3,
                                     edgecolor=badge_color, linewidth=1,
                                     transform=ax.transAxes)
    ax.add_patch(badge)
    ax.text(x0 + 0.08, 0.605, f"Complexity: {complexity}", ha='center', va='center',
            fontsize=7, color=badge_color, fontweight='bold', transform=ax.transAxes)
    # Affected layers
    ax.text(x0 + 0.08, 0.46, f"Layers:\n{layers}", ha='center', va='center',
            fontsize=7, color=TXT, transform=ax.transAxes)
    # PoC badge
    poc = "PoC ✓" if vid in ("V-I", "V-V") else "PoC pending"
    poc_col = C_TEAL if vid in ("V-I", "V-V") else "#8b949e"
    ax.text(x0 + 0.08, 0.38, poc, ha='center', va='center',
            fontsize=7, color=poc_col, fontweight='bold', transform=ax.transAxes)

# Soundness condition box
ax.add_patch(mpatches.FancyBboxPatch((0.05, 0.08), 0.90, 0.20,
             boxstyle="round,pad=0.02", facecolor="#161b22",
             edgecolor=C_ACCENT, linewidth=1.5, transform=ax.transAxes))
ax.text(0.50, 0.24, "Circuit Soundness: ∀ (x, y, π): Verify(C, x, y, π) = 1  ⟹  y = f(x)",
        ha='center', va='center', fontsize=9.5, color=C_ACCENT,
        fontweight='bold', transform=ax.transAxes)
ax.text(0.50, 0.14, "Violation: ∃ (x, y*, π*) s.t. Verify accepts y* ≠ f(x)  →  Inflated Trust Score Tₜ",
        ha='center', va='center', fontsize=8.5, color=TXT, transform=ax.transAxes)

fig2.savefig(out_dir / "fig_zkml_taxonomy.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print(f"Saved: {out_dir}/fig_zkml_taxonomy.png")


# ═══════════════════════════════════════════════════════════════════
# FIGURE 3: Architecture Co-Design Diagram
# ═══════════════════════════════════════════════════════════════════
fig3, ax3 = plt.subplots(figsize=(14, 8), facecolor=BG)
ax3.set_facecolor(BG)
ax3.axis("off")
fig3.suptitle("PoUI + ZKML + PQC Co-Design Architecture (RQ4)\n"
              "Towards an AI-Native Blockchain Framework",
              fontsize=13, fontweight="bold", color=TXT_H)

layers = [
    {"label": "L1: PoUI Consensus Layer",
     "desc": "Trust Score Tₜ computation\nValidator selection & slashing\nEpoch management",
     "color": C_HONEST, "y": 0.68},
    {"label": "L2: ZKML Proof Layer",
     "desc": "Neural network inference\nZK proof generation (EZKL)\nProof verification on-chain",
     "color": C_ACCENT, "y": 0.42},
    {"label": "L3: PQC Signature Layer",
     "desc": "ML-DSA-44 signing (FIPS 204)\nML-KEM-768 key encapsulation\nQuantum-safe identity",
     "color": C_PURPLE, "y": 0.16},
]

for layer in layers:
    rect = mpatches.FancyBboxPatch((0.05, layer["y"]), 0.55, 0.20,
                                    boxstyle="round,pad=0.02",
                                    facecolor=layer["color"], alpha=0.12,
                                    edgecolor=layer["color"], linewidth=2,
                                    transform=ax3.transAxes)
    ax3.add_patch(rect)
    ax3.text(0.325, layer["y"] + 0.135, layer["label"],
             ha='center', va='center', fontsize=11,
             fontweight='bold', color=layer["color"], transform=ax3.transAxes)
    ax3.text(0.325, layer["y"] + 0.065, layer["desc"],
             ha='center', va='center', fontsize=8.5, color=TXT, transform=ax3.transAxes)

# Arrows between layers
for y_start, label_ic in [(0.68, "IC-01: RequestInferenceProof\nIC-02: SubmitVerifiedOutput"),
                           (0.42, "IC-03: RegisterValidatorKey\nIC-04: SignProofHash")]:
    ax3.annotate("", xy=(0.325, y_start - 0.005), xytext=(0.325, y_start - 0.048),
                 xycoords='axes fraction', textcoords='axes fraction',
                 arrowprops=dict(arrowstyle='<->', color="#8b949e", lw=2))
    ax3.text(0.37, y_start - 0.027, label_ic, ha='left', va='center',
             fontsize=7.5, color="#8b949e", transform=ax3.transAxes)

# Emergent properties panel
props = [
    ("ESP-1", "Proof-of-Identity Chain",     C_TEAL),
    ("ESP-2", "Quantum-Safe AI Governance",   C_ACCENT),
    ("ESP-3", "Layered Slash Amplification",  C_AMBER),
]
ax3.text(0.72, 0.88, "Emergent Security Properties\n(only from co-design)",
         ha='center', fontsize=10, fontweight='bold', color=TXT_H, transform=ax3.transAxes)
for i, (pid, name, col) in enumerate(props):
    y_p = 0.72 - i * 0.13
    badge = mpatches.FancyBboxPatch((0.63, y_p - 0.03), 0.33, 0.09,
                                     boxstyle="round,pad=0.01",
                                     facecolor=col, alpha=0.15,
                                     edgecolor=col, linewidth=1.5,
                                     transform=ax3.transAxes)
    ax3.add_patch(badge)
    ax3.text(0.795, y_p + 0.015, f"[{pid}] {name}",
             ha='center', va='center', fontsize=8, color=col,
             fontweight='bold', transform=ax3.transAxes)

# Failure modes panel
fms = [
    ("FM-CD-1", "Proving-Slot Race",       "High",   C_MAL),
    ("FM-CD-2", "Key Rotation Desync",     "Medium", C_AMBER),
    ("FM-CD-3", "Bootstrap Paradox",       "Low",    C_TEAL),
    ("FM-CD-4", "Size Budget Overflow",    "High",   C_MAL),
]
ax3.text(0.72, 0.30, "Co-Design Failure Modes",
         ha='center', fontsize=10, fontweight='bold', color=TXT_H, transform=ax3.transAxes)
for i, (fid, name, sev, col) in enumerate(fms):
    y_f = 0.22 - i * 0.07
    ax3.text(0.65, y_f, f"[{fid}]", ha='left', va='center',
             fontsize=7.5, color=col, fontweight='bold', transform=ax3.transAxes)
    ax3.text(0.73, y_f, name, ha='left', va='center',
             fontsize=7.5, color=TXT, transform=ax3.transAxes)
    ax3.text(0.92, y_f, sev, ha='left', va='center',
             fontsize=7, color=col, transform=ax3.transAxes)

fig3.savefig(out_dir / "fig_architecture.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print(f"Saved: {out_dir}/fig_architecture.png")
print("\nAll paper figures generated ✓")
