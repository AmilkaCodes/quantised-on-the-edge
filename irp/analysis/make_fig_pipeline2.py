"""Figure 3.1 (compact): the measurement pipeline, drawn at the printed size (6.4 in wide) with few words.
Six stages in a row; the three tiers beneath the serve stage; the Mac tier also carries the quality axis."""
import os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

HERE = os.path.dirname(os.path.abspath(__file__))
stages = [("Quantise", "five rungs,\nno calibration"),
          ("Serve", "llama-server b9951\nper backend"),
          ("Generate", "greedy, seed 0\n768-token cap"),
          ("Score", "EvalPlus\nexecution"),
          ("Record", "per-problem JSON\nperf CSV, manifest"),
          ("Analyse", "recompute from\nsnapshots; audit")]
tiers = [("MacBook Pro (Metal)", "quality + cost"), ("Jetson Orin Nano (CUDA)", "cost; cross-device check"), ("Raspberry Pi 5 (CPU)", "cost; cross-device check")]
fig, ax = plt.subplots(figsize=(6.4, 3.4)); ax.set_xlim(0, 100); ax.set_ylim(0, 54); ax.axis("off")
W, H, G = 13.6, 20, 3.6; x0 = 1.0; y0 = 31
for i, (t, s) in enumerate(stages):
    x = x0 + i * (W + G)
    ax.add_patch(FancyBboxPatch((x, y0), W, H, boxstyle="round,pad=0.4", fc="#f2f2f2", ec="black", lw=0.9))
    ax.text(x + W / 2, y0 + H - 4.2, f"{i + 1}  {t}", ha="center", va="center", fontsize=9.5, weight="bold")
    ax.text(x + W / 2, y0 + 7.2, s, ha="center", va="center", fontsize=7.6, color="#333333", linespacing=1.25)
    if i < 5: ax.add_patch(FancyArrowPatch((x + W + 0.3, y0 + H / 2), (x + W + G - 0.3, y0 + H / 2), arrowstyle="-|>", mutation_scale=10, lw=1.2, color="black", zorder=5))
TW, TH = 29, 12; ty = 5
for j, (name, sub) in enumerate(tiers):
    tx = 3 + j * (TW + 3.5)
    ax.add_patch(FancyBboxPatch((tx, ty), TW, TH, boxstyle="round,pad=0.4", fc="#dcdcdc", ec="black", lw=0.9))
    ax.text(tx + TW / 2, ty + TH - 3.6, name, ha="center", va="center", fontsize=8.4, weight="bold")
    ax.text(tx + TW / 2, ty + 3.4, sub, ha="center", va="center", fontsize=7.6, color="#333333")
    sx = x0 + 1 * (W + G) + W / 2
    ax.add_patch(FancyArrowPatch((sx, y0 - 0.5), (tx + TW / 2, ty + TH + 0.5), arrowstyle="-|>", mutation_scale=8, lw=0.8, color="#444444", connectionstyle="arc3,rad=0.0"))
ax.text(50, 1.2, "the same harness on every tier; only the per-device configuration file differs", ha="center", fontsize=7.4, style="italic", color="#444444")
plt.tight_layout(pad=0.3); out = os.path.join(HERE, "figures", "fig3-1_pipeline2.png"); fig.savefig(out, dpi=300); print("wrote", out)
