#!/usr/bin/env python3
"""Figure 4.4: the deployment map (RQ3) as a grid a lay reader can scan: rows = model x rung, columns = tiers,
cell = verdict against the registered gates of Table 3.2 with the binding number. Values from Tables 4.1 to 4.3.
Drawn at print size (6.6 in wide) so every label is legible on the page without scaling.
Monochrome fills: white = deployable, hatched = quality-marginal, grey = fails the throughput floor,
dark = quality-collapsed, crossed = not run (registered 8 GB edge line). The Jetson Phi-3 Q8_0 cell carries the
short-interactive-use caveat of Section 4.4 as a starred tick.
Output: figures/fig4-5_depmap.png"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures", "fig4-5_depmap.png")
INK, MID = "#111111", "#444444"
plt.rcParams.update({"font.family": "sans-serif", "text.color": INK})
rows = [("Qwen 1.5B", "F16"), ("Qwen 1.5B", "Q8_0"), ("Qwen 1.5B", "Q4_K_M"), ("Qwen 1.5B", "Q3_K_M"), ("Qwen 1.5B", "Q2_K"),
        ("Phi-3 3.8B", "F16"), ("Phi-3 3.8B", "Q8_0"), ("Phi-3 3.8B", "Q4_K_M"), ("Phi-3 3.8B", "Q3_K_M"), ("Phi-3 3.8B", "Q2_K")]
cols = ["Pi 5\n(CPU)", "Jetson Orin Nano\n(edge GPU)", "MacBook Pro\n(consumer GPU)"]
# (kind, label): kind in {"ok", "okc", "marg", "fail", "collapse", "notrun"}; labels are median tokens per second
V = {
 ("Qwen 1.5B", "F16"):    [("fail", "3.8"), ("ok", "18.3"), ("ok", "78")],
 ("Qwen 1.5B", "Q8_0"):   [("fail", "5.9"), ("ok", "31.0"), ("ok", "124")],
 ("Qwen 1.5B", "Q4_K_M"): [("ok", "11.0"), ("ok", "39.8"), ("ok", "165")],
 ("Qwen 1.5B", "Q3_K_M"): [("marg", "12.7"), ("marg", "18.6"), ("marg", "143")],
 ("Qwen 1.5B", "Q2_K"):   [("collapse", ""), ("collapse", ""), ("collapse", "")],
 ("Phi-3 3.8B", "F16"):   [("notrun", ""), ("notrun", ""), ("ok", "35.9")],
 ("Phi-3 3.8B", "Q8_0"):  [("fail", "2.6"), ("okc", "14.6"), ("ok", "61.4")],
 ("Phi-3 3.8B", "Q4_K_M"): [("fail", "4.5"), ("marg", "19.7"), ("marg", "85.8")],
 ("Phi-3 3.8B", "Q3_K_M"): [("collapse", ""), ("collapse", ""), ("collapse", "")],
 ("Phi-3 3.8B", "Q2_K"):  [("collapse", ""), ("collapse", ""), ("collapse", "")],
}
SYM = {"ok": "✓", "okc": "✓*", "marg": "◐", "fail": "✗", "collapse": "■", "notrun": "not run"}
style = {"ok": dict(fc="white", hatch=None), "okc": dict(fc="white", hatch=None), "marg": dict(fc="white", hatch="//"),
         "fail": dict(fc="#bdbdbd", hatch=None), "collapse": dict(fc="#6e6e6e", hatch=None), "notrun": dict(fc="#d9d9d9", hatch="x")}
fig, ax = plt.subplots(figsize=(6.6, 4.6), dpi=300)
ax.set_xlim(0, 3); ax.set_ylim(0, len(rows)); ax.axis("off")
for j, c in enumerate(cols):
    ax.text(j + 0.5, len(rows) + 0.15, c, ha="center", va="bottom", fontsize=8, weight="bold", linespacing=1.2)
for i, (m, r) in enumerate(rows):
    y = len(rows) - 1 - i
    ax.text(-0.04, y + 0.5, f"{m}  {r}", ha="right", va="center", fontsize=8, weight="bold" if r == "Q4_K_M" and m.startswith("Qwen") else "normal")
    for j, (kind, label) in enumerate(V[(m, r)]):
        st = style[kind]
        ax.add_patch(Rectangle((j, y), 1, 1, fc=st["fc"], ec="#c8c8c8", lw=0, hatch=st["hatch"])); ax.add_patch(Rectangle((j, y), 1, 1, fc="none", ec=INK, lw=0.8))
        if kind in ("marg", "notrun"): ax.add_patch(Rectangle((j + 0.1, y + 0.28), 0.8, 0.44, fc="white", ec="none"))
        txt = (SYM[kind] + "  " + label).strip()
        ax.text(j + 0.5, y + 0.5, txt, ha="center", va="center", fontsize=8.5, color="white" if kind == "collapse" else INK)
    if r == "Q2_K" and i < len(rows) - 1:
        ax.plot([0, 3], [y, y], color=INK, lw=2)
fig.text(0.56, 0.06, "✓ deployable (all four gates)    ✓* deployable for short interactive use only (Section 4.4)\n"
         "◐ quality marginal    ✗ below the throughput floor    ■ quality collapsed\n"
         "not run = above the registered 8 GB edge line (Section 3.2); numbers are tokens per second",
         ha="center", va="center", fontsize=7.5, color=MID, linespacing=1.6)
fig.subplots_adjust(left=0.22, right=0.99, top=0.9, bottom=0.15); fig.savefig(OUT, dpi=300, facecolor="white"); print("wrote", OUT)
