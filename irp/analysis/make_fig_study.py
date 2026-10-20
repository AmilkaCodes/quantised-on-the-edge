#!/usr/bin/env python3
"""Figure 1.1: the study at a glance, for a reader new to the field.
Two models x five precision rungs -> one quality axis (measured once) and one cost axis (measured per tier)
-> verdicts against thresholds fixed in advance. Monochrome. Output: figures/fig1-1_study.png"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures", "fig1-1_study.png")
INK, MID, FILL, FILL2 = "#111111", "#555555", "#f2f2f2", "#dddddd"
plt.rcParams.update({"font.family": "sans-serif", "text.color": INK})
fig, ax = plt.subplots(figsize=(11.0, 4.6), dpi=300); ax.set_xlim(0, 110); ax.set_ylim(-5, 46); ax.axis("off")

def box(x, y, w, h, title, lines, fill=FILL, ts=10.5, bs=7.8):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.2", fc=fill, ec=INK, lw=1.1))
    ax.text(x + w / 2, y + h - 2.4, title, ha="center", va="center", fontsize=ts, weight="bold")
    ax.text(x + w / 2, y + (h - 4.2) / 2 - 0.2, "\n".join(lines), ha="center", va="center", fontsize=bs, color=MID, linespacing=1.3)
def arrow(x0, y0, x1, y1, lw=1.1, rad=0):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=11, lw=lw, color=INK,
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0))

# inputs
box(1, 26, 22, 18, "Two small models", ["Qwen2.5-Coder-1.5B", "(code-specialised)", "", "Phi-3-mini-3.8B", "(general-purpose)"])
box(1, 3, 22, 18, "Five precision rungs", ["F16 (full precision)", "Q8_0  (8-bit)", "Q4_K_M  (4-bit)", "Q3_K_M  (3-bit)", "Q2_K  (2-bit label)"])
# the ladder
box(27, 14, 18, 18, "Quantise", ["same tool, same recipe,", "no calibration:", "10 model files", "(2 models x 5 rungs)"], fill=FILL2)
arrow(23, 35, 27, 25); arrow(23, 12, 27, 21)
# two axes
box(50, 27, 26, 17, "Quality axis", ["Does the code still pass its tests?", "164 problems, executed, same", "problems at every rung;", "measured once, checked across devices"])
box(50, 3, 26, 17, "Cost axis", ["How fast, how much memory,", "how much energy per token?", "Measured on each of three devices:", "Pi 5 (CPU), Jetson (edge GPU), MacBook"])
arrow(45, 25, 50, 35, rad=-0.15); arrow(45, 21, 50, 11, rad=0.15)
# verdicts
box(81, 15, 27, 18, "Verdicts, fixed in advance", ["Quality: within 5 points of F16?", "Speed: 8-10 tokens/s, first token < 1-2 s?", "Memory: fits without swap?", "", "-> which model, at which rung,", "   runs where"], fill=FILL2, bs=7.6)
arrow(76, 35, 81, 27, rad=-0.15); arrow(76, 11, 81, 20, rad=0.15)
ax.text(55, -2.5, "Seven registered extensions then test whether the answers survive documentation context, tool use, model scale, calibration, fine-tuning and a second benchmark",
        ha="center", va="center", fontsize=7.6, color=MID, style="italic")
fig.subplots_adjust(left=0, right=1, top=1, bottom=0); fig.savefig(OUT, dpi=300, facecolor="white"); print("wrote", OUT)
