#!/usr/bin/env python3
"""Figure: the deployment map (RQ3) as a grid a lay reader can scan: rows = model x rung, columns = tiers,
cell = verdict against the registered gates with the binding reason. Values from Chapter 4 Tables 4.2, 4.7, 4.8.
Monochrome fills: white = deployable, hatched = quality-marginal, grey = fails, dark = quality-collapsed, X = does not fit.
Output: figures/fig4-5_depmap.png"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures", "fig4-5_depmap.png")
INK, MID = "#111111", "#555555"
plt.rcParams.update({"font.family": "sans-serif", "text.color": INK})
rows = [("Qwen 1.5B", "F16"), ("Qwen 1.5B", "Q8_0"), ("Qwen 1.5B", "Q4_K_M"), ("Qwen 1.5B", "Q3_K_M"), ("Qwen 1.5B", "Q2_K"),
        ("Phi-3 3.8B", "F16"), ("Phi-3 3.8B", "Q8_0"), ("Phi-3 3.8B", "Q4_K_M"), ("Phi-3 3.8B", "Q3_K_M"), ("Phi-3 3.8B", "Q2_K")]
cols = ["Pi 5 (CPU)", "Jetson Orin Nano (edge GPU)", "MacBook Pro (consumer GPU)"]
# (kind, label): kind in {"ok","marg","fail","collapse","nofit"}
V = {
 ("Qwen 1.5B","F16"):   [("fail","3.8 tok/s: below floor"), ("ok","18 tok/s"), ("ok","78 tok/s")],
 ("Qwen 1.5B","Q8_0"):  [("fail","5.9 tok/s: below floor"), ("ok","31 tok/s"), ("ok","124 tok/s")],
 ("Qwen 1.5B","Q4_K_M"):[("ok","11.0 tok/s: clears floor"), ("ok","40 tok/s"), ("ok","165 tok/s")],
 ("Qwen 1.5B","Q3_K_M"):[("marg","12.7 tok/s; quality marginal"), ("marg","18.6 tok/s (GPU dip); quality marginal"), ("marg","143 tok/s; quality marginal")],
 ("Qwen 1.5B","Q2_K"):  [("collapse","quality collapsed"), ("collapse","quality collapsed"), ("collapse","quality collapsed")],
 ("Phi-3 3.8B","F16"):  [("nofit","does not fit (9.8 GB)"), ("nofit","does not fit (9.8 GB)"), ("ok","36 tok/s")],
 ("Phi-3 3.8B","Q8_0"): [("fail","2.6 tok/s: below floor"), ("ok","14.6 tok/s"), ("ok","61 tok/s")],
 ("Phi-3 3.8B","Q4_K_M"):[("fail","4.5 tok/s; quality marginal"), ("marg","19.7 tok/s; quality marginal"), ("marg","86 tok/s; quality marginal")],
 ("Phi-3 3.8B","Q3_K_M"):[("collapse","quality collapsed"), ("collapse","quality collapsed"), ("collapse","quality collapsed")],
 ("Phi-3 3.8B","Q2_K"): [("collapse","quality collapsed"), ("collapse","quality collapsed"), ("collapse","quality collapsed")],
}
style = {"ok": dict(fc="white", hatch=None), "marg": dict(fc="white", hatch="//"), "fail": dict(fc="#bdbdbd", hatch=None),
         "collapse": dict(fc="#6e6e6e", hatch=None), "nofit": dict(fc="#d9d9d9", hatch="x")}
fig, ax = plt.subplots(figsize=(10.5, 5.6), dpi=300)
ax.set_xlim(0, 3); ax.set_ylim(0, len(rows)); ax.axis("off")
for j, c in enumerate(cols):
    ax.text(j + 0.5, len(rows) + 0.25, c, ha="center", va="bottom", fontsize=10, weight="bold")
for i, (m, r) in enumerate(rows):
    y = len(rows) - 1 - i
    ax.text(-0.04, y + 0.5, f"{m}  {r}", ha="right", va="center", fontsize=9.2, weight="bold" if r == "Q4_K_M" and m.startswith("Qwen") else "normal")
    for j, (kind, label) in enumerate(V[(m, r)]):
        st = style[kind]
        ax.add_patch(Rectangle((j, y), 1, 1, fc=st["fc"], ec="#c8c8c8", lw=0, hatch=st["hatch"])); ax.add_patch(Rectangle((j, y), 1, 1, fc="none", ec=INK, lw=0.8))
        if kind in ("marg", "nofit"): ax.add_patch(Rectangle((j + 0.08, y + 0.3), 0.84, 0.4, fc="white", ec="none"))
        ax.text(j + 0.5, y + 0.5, label, ha="center", va="center", fontsize=7.6,
                color="white" if kind == "collapse" else INK, wrap=True)
    if r == "Q2_K" and i < len(rows) - 1:
        ax.plot([0, 3], [y, y], color=INK, lw=2.2)
fig.text(0.5, 0.02, "white = deployable (all four registered gates pass)   hatched = quality marginal on the interval   grey = fails the throughput floor   "
         "dark = quality collapsed   crossed = does not fit the device memory", ha="center", fontsize=7.4, color=MID)
fig.subplots_adjust(left=0.2, right=0.99, top=0.9, bottom=0.08); fig.savefig(OUT, dpi=300, facecolor="white"); print("wrote", OUT)
