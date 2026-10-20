"""Figure 4.1: HumanEval+ pass@1 across the naive ladder for both models, with per-estimate 95% intervals (Table D.1),
each model's five-point margin below its F16 drawn as a dashed line, effective bits per weight beneath each rung
(Table D.2), and the verdict class of Table 4.1 as the marker style. Text kept minimal: it counts toward the limit."""
import os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
rungs = ["F16", "Q8_0", "Q4_K_M", "Q3_K_M", "Q2_K"]
bits = {"Qwen": [16.0, 8.5, 5.1, 4.3, 3.5], "Phi-3": [16.0, 8.5, 5.0, 4.1, 3.2]}
data = {
 "Qwen2.5-Coder-1.5B": dict(c="#1f4e9c", y=[0.610, 0.616, 0.616, 0.585, 0.384], lo=[0.537, 0.543, 0.543, 0.512, 0.311], hi=[0.683, 0.689, 0.689, 0.659, 0.457],
                            cls=["base", "within", "within", "inconclusive", "collapsed"]),
 "Phi-3-mini-3.8B": dict(c="#c8551a", y=[0.646, 0.628, 0.549, 0.427, 0.220], lo=[0.573, 0.555, 0.470, 0.348, 0.159], hi=[0.720, 0.701, 0.628, 0.500, 0.280],
                         cls=["base", "within", "inconclusive", "collapsed", "collapsed"]),
}
fig, ax = plt.subplots(figsize=(8.2, 4.6))
x = list(range(5))
for name, d in data.items():
    ax.plot(x, d["y"], color=d["c"], lw=2, zorder=2, label=name)
    ax.errorbar(x, d["y"], yerr=[[a - b for a, b in zip(d["y"], d["lo"])], [b - a for a, b in zip(d["y"], d["hi"])]], fmt="none", ecolor=d["c"], elinewidth=1.1, capsize=3, zorder=2)
    ax.axhline(d["y"][0] - 0.05, color=d["c"], lw=1, ls="--", alpha=0.7, zorder=1)
    for xi, yi, cl in zip(x, d["y"], d["cls"]):
        if cl in ("base", "within"): ax.plot(xi, yi, "o", color=d["c"], ms=8, zorder=3)
        elif cl == "inconclusive": ax.plot(xi, yi, "o", mfc="white", mec=d["c"], mew=2, ms=8, zorder=3)
        else: ax.plot(xi, yi, "X", color=d["c"], ms=10, zorder=3)
ax.text(4.08, data["Qwen2.5-Coder-1.5B"]["y"][0] - 0.05, "margin", color="#1f4e9c", fontsize=8, va="top")
ax.text(4.08, data["Phi-3-mini-3.8B"]["y"][0] - 0.05, "margin", color="#c8551a", fontsize=8, va="bottom")
ax.set_xticks(x); ax.set_xticklabels([f"{r}\n{bits['Qwen'][i]:.1f} / {bits['Phi-3'][i]:.1f} bits" for i, r in enumerate(rungs)], fontsize=9)
ax.set_ylim(0.1, 0.8); ax.set_ylabel("HumanEval+ pass@1 (n = 164)"); ax.set_xlabel("rung (effective bits per weight: Qwen / Phi-3)")
ax.grid(axis="y", alpha=0.3); ax.legend(frameon=False, loc="lower left", fontsize=9)
for s in ("top", "right"): ax.spines[s].set_visible(False)
plt.tight_layout(); out = os.path.join(HERE, "figures", "fig4-1_collapse.png"); fig.savefig(out, dpi=220); print("wrote", out)
