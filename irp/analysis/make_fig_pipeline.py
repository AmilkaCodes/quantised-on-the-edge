#!/usr/bin/env python3
"""Figure 3.1 (methodology, implementation section): the measurement pipeline.
Monochrome by the formatting rule (no colour), sans-serif, print-clean.
Run from anywhere:  py -3 irp/analysis/make_fig_pipeline.py
Output: irp/analysis/figures/fig3-1_pipeline.png (300 dpi)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures", "fig3-1_pipeline.png")
INK, MID, FILL, FILL2 = "#111111", "#555555", "#f2f2f2", "#dddddd"
plt.rcParams.update({"font.family": "sans-serif", "font.size": 9.5, "text.color": INK})

fig, ax = plt.subplots(figsize=(11.0, 4.3), dpi=300)
ax.set_xlim(0, 104); ax.set_ylim(0, 40); ax.axis("off")

def box(x, y, w, h, title, lines, fill=FILL, lw=1.1):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.2",
                                fc=fill, ec=INK, lw=lw))
    ax.text(x + w / 2, y + h - 2.6, title, ha="center", va="center", fontsize=10.5, weight="bold")
    ax.text(x + w / 2, y + (h - 4.5) / 2 - 0.3, "\n".join(lines), ha="center", va="center",
            fontsize=7.6, color=MID, linespacing=1.25)

def arrow(x0, y0, x1, y1, style="-|>", lw=1.1, con="arc3,rad=0"):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle=style, mutation_scale=11,
                                 lw=lw, color=INK, connectionstyle=con, shrinkA=0, shrinkB=0))

# main row: six stages
W, H, Y, GAP = 14.0, 15.0, 22.0, 3.2
X = [1.0 + i * (W + GAP) for i in range(6)]
box(X[0], Y, W, H, "1  Quantise", ["once per model", "F16 → Q8_0 → Q4_K_M", "→ Q3_K_M → Q2_K", "pinned llama-quantize,", "no calibration"])
box(X[1], Y, W, H, "2  Serve", ["pinned llama-server", "build b9951, compiled", "per backend; only a", "per-device config file", "differs (offload, paths)"])
box(X[2], Y, W, H, "3  Generate", ["OpenAI-compatible API", "model's own chat template", "greedy, fixed seed", "768-token cap in a", "4,096-token context"])
box(X[3], Y, W, H, "4  Score", ["EvalPlus sanitiser", "then evaluator: execute", "against HumanEval+ /", "MBPP+ tests, subprocess,", "per-problem time limit"])
box(X[4], Y, W, H, "5  Record", ["per-problem pass/fail", "snapshots (JSON);", "perf + energy CSV;", "manifest.json per run", "(OS, build, seed,", "checksums)"])
box(X[5], Y, W, H, "6  Analyse", ["scripts recompute all", "36 quality cells from", "snapshots; paired", "bootstrap and exact", "intervals; H1b rule;", "audit must report 0"])
for i in range(5):
    arrow(X[i] + W, Y + H / 2, X[i + 1], Y + H / 2)

# tier lanes: fan out from Serve, converge at Record
TW, TH, TY = 17.0, 5.6, 3.0
tiers = [("MacBook  (Metal GPU)", "quality axis + perf/energy"),
         ("Jetson Orin Nano  (CUDA)", "perf/energy; cross-device check"),
         ("Raspberry Pi 5  (CPU)", "perf/energy; cross-device check")]
TX = [X[1] + 1.0, X[2] + W + GAP / 2 - TW / 2, X[4] + W - TW - 1.0]
for (name, sub), tx in zip(tiers, TX):
    ax.add_patch(FancyBboxPatch((tx, TY), TW, TH, boxstyle="round,pad=0,rounding_size=0.9",
                                fc=FILL2, ec=INK, lw=1.0))
    ax.text(tx + TW / 2, TY + TH - 1.6, name, ha="center", va="center", fontsize=8.6, weight="bold")
    ax.text(tx + TW / 2, TY + 1.6, sub, ha="center", va="center", fontsize=7.4, color=MID)
# fan-out from Serve (bottom edge) to each tier, and from each tier up to Record (bottom edge)
sx, sy = X[1] + W / 2, Y
rx, ry = X[4] + W / 2, Y
for tx in TX:
    arrow(sx, sy, tx + 2.0, TY + TH, con="arc3,rad=-0.12", lw=0.9)
    arrow(tx + TW - 2.0, TY + TH, rx, ry, con="arc3,rad=-0.12", lw=0.9)
ax.text(X[2] + W + GAP / 2, TY - 2.2,
        "hardware tiers: the same harness and configuration format on every device; "
        "only the device-specific file differs",
        ha="center", va="center", fontsize=7.8, color=MID, style="italic")

fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
fig.savefig(OUT, dpi=300, facecolor="white")
print("wrote", OUT)
