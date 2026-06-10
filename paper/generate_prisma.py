"""
PRISMA 2020 Flowchart Generator
=================================
Generates the PRISMA-compliant systematic review flowchart
for inclusion in the paper (Fig. PRISMA).

PRISMA 2020 stages:
  Identification → Screening → Eligibility → Included
  
Authors: Md. Mehedi Hasan (Team Lead), Antigravity AI (Research Assistant)
Project: Towards an AI-Native Blockchain Framework
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
from pathlib import Path

BG    = "#0d1117"
PANEL = "#161b22"
EDGE  = "#30363d"
TXT   = "#c9d1d9"
TXT_H = "#e6edf3"

C_ID     = "#58a6ff"   # Identification — blue
C_SCREEN = "#d29922"   # Screening — amber
C_ELIG   = "#bc8cff"   # Eligibility — purple
C_INCL   = "#3fb950"   # Included — green
C_EXCL   = "#f85149"   # Excluded — red

fig, ax = plt.subplots(figsize=(14, 10), facecolor=BG)
ax.set_facecolor(BG)
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis("off")

fig.suptitle(
    "PRISMA 2020 Flow Diagram — Systematic Literature Review\n"
    "Towards an AI-Native Blockchain Framework",
    fontsize=13, fontweight="bold", color=TXT_H, y=0.98
)


def box(ax, x, y, w, h, label, sublabel, color, fontsize=9):
    """Draw a rounded box with label."""
    rect = mpatches.FancyBboxPatch(
        (x - w/2, y - h/2), w, h,
        boxstyle="round,pad=0.1",
        facecolor=color, alpha=0.15,
        edgecolor=color, linewidth=2,
        transform=ax.transData
    )
    ax.add_patch(rect)
    ax.text(x, y + h*0.12, label, ha="center", va="center",
            fontsize=fontsize, fontweight="bold", color=color)
    if sublabel:
        ax.text(x, y - h*0.18, sublabel, ha="center", va="center",
                fontsize=fontsize - 1, color=TXT)


def arrow(ax, x1, y1, x2, y2, color="#8b949e"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.8,
                                mutation_scale=15))


def excl_box(ax, x, y, w, h, label, color=C_EXCL):
    rect = mpatches.FancyBboxPatch(
        (x - w/2, y - h/2), w, h,
        boxstyle="round,pad=0.08",
        facecolor=color, alpha=0.12,
        edgecolor=color, linewidth=1.5,
        transform=ax.transData
    )
    ax.add_patch(rect)
    ax.text(x, y, label, ha="center", va="center",
            fontsize=8, color=color, style="italic")


# ── Stage labels ─────────────────────────────────────────────────────────────
stage_x = 0.7
for sy, slabel, scol in [
    (8.8, "IDENTIFICATION", C_ID),
    (6.5, "SCREENING",      C_SCREEN),
    (4.2, "ELIGIBILITY",    C_ELIG),
    (1.9, "INCLUDED",       C_INCL),
]:
    ax.text(stage_x, sy, slabel, ha="center", va="center",
            fontsize=8, fontweight="bold", color=scol,
            rotation=90,
            bbox=dict(boxstyle="round,pad=0.3", fc=PANEL, ec=scol, alpha=0.8))

# ── IDENTIFICATION STAGE ─────────────────────────────────────────────────────
# Databases
box(ax, 4.0, 9.0, 3.8, 0.7,
    "Records identified through database searching",
    "IEEE Xplore, arXiv, ACM DL, Scopus, SpringerLink  (n = 248)",
    C_ID)

box(ax, 7.5, 9.0, 2.6, 0.7,
    "Additional records identified",
    "Whitepapers, NIST docs, industry reports  (n = 22)",
    C_ID)

# Merge arrow
arrow(ax, 4.0, 8.65, 4.0, 8.05)
arrow(ax, 7.5, 8.65, 5.9, 8.05)

box(ax, 5.0, 7.7, 4.2, 0.6,
    "Total records after duplicates removed",
    "n = 231",
    C_ID)

# ── SCREENING STAGE ──────────────────────────────────────────────────────────
arrow(ax, 5.0, 7.40, 5.0, 6.85)

box(ax, 5.0, 6.55, 4.2, 0.6,
    "Records screened (title + abstract)",
    "n = 231",
    C_SCREEN)

excl_box(ax, 8.4, 6.55, 2.2, 0.5,
         "Records excluded\n(out-of-scope, n=141)")
arrow(ax, 7.1, 6.55, 7.3, 6.55, C_EXCL)

# ── ELIGIBILITY STAGE ─────────────────────────────────────────────────────────
arrow(ax, 5.0, 6.25, 5.0, 5.35)

box(ax, 5.0, 5.05, 4.2, 0.6,
    "Full-text articles assessed for eligibility",
    "n = 90",
    C_ELIG)

excl_box(ax, 8.4, 5.05, 2.2, 0.7,
         "Full-text excluded  (n=61)\n• No blockchain context: 22\n• No formal analysis: 19\n• Duplicate results: 12\n• Inaccessible: 8")
arrow(ax, 7.1, 5.05, 7.3, 5.05, C_EXCL)

# ── INCLUDED STAGE ────────────────────────────────────────────────────────────
arrow(ax, 5.0, 4.75, 5.0, 3.55)

box(ax, 5.0, 3.25, 4.2, 0.6,
    "Studies included in synthesis",
    "n = 60",
    C_INCL)

# Breakdown
for i, (domain, n, col) in enumerate([
    ("Domain A — AI Consensus / PoUI",          16, C_INCL),
    ("Domain B — ZKML Security",                18, C_INCL),
    ("Domain C — PQC on Blockchain",            18, C_INCL),
    ("Domain D — Co-Design / Architecture",     2, C_INCL),
    ("Domain E — Foundational (ZKP, Math)",     6, C_INCL),
]):
    y_i = 2.55 - i * 0.37
    ax.plot([3.1, 3.5], [y_i, y_i], color=col, linewidth=1.2, alpha=0.7)
    ax.text(3.55, y_i, f"{domain}  →  n={n}", ha="left", va="center",
            fontsize=7.5, color=col)

# Year range annotation
ax.text(5.0, 0.55,
        "Year range: 2008–2026  |  Priority: 2020–2026 (85%)  |  "
        "Foundational pre-2020 works: 15%",
        ha="center", va="center", fontsize=8, color="#8b949e",
        bbox=dict(boxstyle="round,pad=0.3", fc=PANEL, ec=EDGE, alpha=0.8))

# Search query box
ax.text(5.0, 0.20,
        'Search queries: "AI consensus blockchain" | "proof of useful intelligence" | '
        '"ZKML underconstrained circuits" | "post-quantum blockchain overhead" | "AI-native protocol"',
        ha="center", va="center", fontsize=7, color="#8b949e", style="italic")

out = Path(__file__).parent / "figures" / "fig_prisma_flowchart.png"
out.parent.mkdir(exist_ok=True)
fig.savefig(out, dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print(f"PRISMA flowchart saved: {out}")
