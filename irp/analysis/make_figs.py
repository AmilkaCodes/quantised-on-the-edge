#!/usr/bin/env python3
"""IRP figures — quality collapse + three-tier performance + trade-off.
Palette: dataviz default categorical (validated). Print-clean, colorblind-safe, direct-labelled."""
import json, csv, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PILOT = os.path.expanduser("~/Documents/UoY/RP/proposal-dev/pilot")
OUT = os.path.expanduser("~/Documents/UoY/RP/irp/analysis/figures"); os.makedirs(OUT, exist_ok=True)
QUANTS = ["F16", "Q8_0", "Q4_K_M", "Q3_K_M", "Q2_K"]
X = list(range(len(QUANTS)))
# dataviz categorical slots (validated default order)
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e7e6e2"

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "font.size": 11, "font.family": "sans-serif",
    "axes.edgecolor": INK2, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": INK2, "ytick.color": INK2, "axes.titlecolor": INK,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "legend.frameon": False,
})

# ---- quality: pass@1 plus from per-problem eval_results (authoritative) ----
def q_pass(full):
    out = {}
    for q in QUANTS:
        d = json.load(open(f"{PILOT}/results/mac/samples_{full}_{q}-sanitized_eval_results.json"))["eval"]
        out[q] = np.mean([1 if d[t][0]["plus_status"] == "pass" else 0 for t in d])
    return [out[q] for q in QUANTS]
QUAL = {"Qwen2.5-Coder-1.5B": q_pass("qwen2.5-coder-1.5b-instruct"),
        "Phi-3-mini-3.8B":    q_pass("phi-3-mini-4k-instruct")}
THRESH = {"Qwen2.5-Coder-1.5B": 4, "Phi-3-mini-3.8B": 2}   # x-index of collapse rung (Q2, Q4)

# ---- performance: read the three perf CSVs ----
def perf(dev):
    import glob
    f = sorted(glob.glob(f"{PILOT}/results/{dev}/perf_results_*.csv"))[-1]
    rows = list(csv.DictReader(open(f)))
    d = {}
    for r in rows:
        d.setdefault(r["model"], {})[r["quant"]] = r
    return d
PERF = {"mac": perf("mac"), "jetson": perf("jetson"), "pi5": perf("pi5")}
MODELS = {"qwen2.5-coder-1.5b-instruct": "Qwen2.5-Coder-1.5B", "phi-3-mini-4k-instruct": "Phi-3-mini-3.8B"}
TIER = [("mac", "Mac (Metal)", BLUE), ("jetson", "Jetson (CUDA)", ORANGE), ("pi5", "Pi 5 (CPU)", AQUA)]

def series(dev, modelkey, field):
    d = PERF[dev].get(modelkey, {})
    return [float(d[q][field]) if q in d and d[q][field] not in ("", "None") else np.nan for q in QUANTS]

# ============ FIG 1 — quality collapse curves ============
fig, ax = plt.subplots(figsize=(7.2, 4.6))
for name, col in zip(QUAL, (BLUE, ORANGE)):
    y = QUAL[name]
    ax.plot(X, y, "-o", color=col, lw=2, ms=7, label=name, zorder=3)
    ax.annotate(name, (X[-1], y[-1]), color=col, fontsize=10, fontweight="bold",
                xytext=(6, 0), textcoords="offset points", va="center")
    ti = THRESH[name]
    ax.annotate("collapse", (ti, QUAL[name][ti]), color=col, fontsize=9,
                xytext=(0, -18), textcoords="offset points", ha="center",
                arrowprops=dict(arrowstyle="->", color=col, lw=1.2))
ax.axhline(0.40, color=INK2, lw=1, ls=":", zorder=1)
ax.annotate("0.40 GO floor", (0, 0.40), color=INK2, fontsize=8, xytext=(0, 4), textcoords="offset points")
ax.set_xticks(X); ax.set_xticklabels(QUANTS)
ax.set_xlabel("Quantisation (high precision → aggressive)"); ax.set_ylabel("HumanEval+ pass@1 (plus)")
ax.set_ylim(0, 0.8); ax.set_xlim(-0.3, len(QUANTS) - 0.3 + 0.9)
ax.set_title("Quality collapse across the quantisation ladder\n(measured once, hardware-independent; ‘collapse’ = McNemar p<0.05 vs F16)",
             fontsize=11, loc="left")
fig.tight_layout(); fig.savefig(f"{OUT}/fig1_collapse.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# ============ FIG 2 — throughput per tier (small multiples) ============
fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True)
for ax, (mk, mlabel) in zip(axes, MODELS.items()):
    for dev, dlabel, col in TIER:
        y = series(dev, mk, "median_tok_s")
        ax.plot(X, y, "-o", color=col, lw=2, ms=6, label=dlabel, zorder=3)
    ax.set_yscale("log"); ax.set_xticks(X); ax.set_xticklabels(QUANTS, rotation=0)
    ax.set_title(mlabel, fontsize=11, loc="left"); ax.set_xlabel("Quantisation")
    ax.grid(True, which="both", axis="y")
axes[0].set_ylabel("Median decode tok/s (log)")
axes[0].legend(loc="lower right", fontsize=9)
fig.suptitle("Throughput vs quantisation, by hardware tier  (note the Q3_K_M dip on GPU backends, absent on CPU)",
             fontsize=11, x=0.01, ha="left")
fig.tight_layout(rect=(0, 0, 1, 0.96)); fig.savefig(f"{OUT}/fig2_throughput.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# ============ FIG 3 — quality vs speed trade-off (Mac tier) ============
fig, ax = plt.subplots(figsize=(7.2, 4.8))
for (mk, mlabel), col in zip(MODELS.items(), (BLUE, ORANGE)):
    qy = QUAL[mlabel]; sp = series("mac", mk, "median_tok_s")
    ax.plot(sp, qy, "-o", color=col, lw=1.8, ms=7, label=mlabel, zorder=3)
    for i, q in enumerate(QUANTS):
        ax.annotate(q, (sp[i], qy[i]), fontsize=7.5, color=INK2,
                    xytext=(4, 4), textcoords="offset points")
ax.set_xlabel("Median decode tok/s (Mac / Metal)"); ax.set_ylabel("HumanEval+ pass@1 (plus)")
ax.set_title("Quality–speed trade-off (Mac tier)\nup-and-right is better; the knee is the deploy sweet-spot",
             fontsize=11, loc="left")
ax.legend(loc="lower right", fontsize=9)
fig.tight_layout(); fig.savefig(f"{OUT}/fig3_tradeoff.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# ============ FIG 4 — peak memory per tier (small multiples) ============
fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True)
for ax, (mk, mlabel) in zip(axes, MODELS.items()):
    for dev, dlabel, col in TIER:
        y = [v/1024 for v in series(dev, mk, "peak_rss_mb")]  # GB
        ax.plot(X, y, "-o", color=col, lw=2, ms=6, label=dlabel, zorder=3)
    ax.axhline(8, color=INK2, lw=1, ls=":")
    ax.annotate("8 GB edge limit", (0, 8), fontsize=8, color=INK2, xytext=(0,3), textcoords="offset points")
    ax.set_xticks(X); ax.set_xticklabels(QUANTS); ax.set_title(mlabel, fontsize=11, loc="left")
    ax.set_xlabel("Quantisation")
axes[0].set_ylabel("Peak RSS (GB)"); axes[0].legend(loc="upper right", fontsize=9)
fig.suptitle("Peak memory vs quantisation, by tier  (Mac real-RSS caveat; Phi-3 F16 exceeds the 8 GB edge devices)",
             fontsize=11, x=0.01, ha="left")
fig.tight_layout(rect=(0, 0, 1, 0.96)); fig.savefig(f"{OUT}/fig4_memory.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# ============ FIG 5 — energy-per-token per edge tier (small multiples) ============
# J/token = mean_power_w / median_tok_s. Edge tiers only (Jetson VDD_IN, Pi 5 PMIC); Mac deferred.
# Boundary caveat: the two power routes measure at different points → compare the WITHIN-tier shape
# along the ladder, NOT absolute levels across tiers.
ETIER = [("mac", "Mac (Metal)", BLUE), ("jetson", "Jetson (CUDA)", ORANGE), ("pi5", "Pi 5 (CPU)", AQUA)]
def jpt(dev, mk):
    pw = series(dev, mk, "mean_power_w"); tk = series(dev, mk, "median_tok_s")
    return [pw[i] / tk[i] if not np.isnan(pw[i]) and not np.isnan(tk[i]) and tk[i] > 0 else np.nan
            for i in range(len(QUANTS))]
fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), sharey=True)
for ax, (mk, mlabel) in zip(axes, MODELS.items()):
    for dev, dlabel, col in ETIER:
        ax.plot(X, jpt(dev, mk), "-o", color=col, lw=2, ms=6, label=dlabel, zorder=3)
    ax.set_yscale("log"); ax.grid(True, which="both", axis="y")
    ax.set_xticks(X); ax.set_xticklabels(QUANTS); ax.set_title(mlabel, fontsize=11, loc="left")
    ax.set_xlabel("Quantisation")
# mark the Q3_K_M GPU energy trap (BOTH GPU backends bump up at Q3; Jetson line starkest on the Qwen panel)
qy = jpt("jetson", "qwen2.5-coder-1.5b-instruct")
axes[0].annotate("Q3 GPU energy trap\n(both GPU backends: fewest W, worst J/tok)", (3, qy[3]), color=ORANGE, fontsize=8.5,
                 xytext=(-4, 34), textcoords="offset points", ha="center",
                 arrowprops=dict(arrowstyle="->", color=ORANGE, lw=1.2))
axes[0].set_ylabel("Energy per token (J/token, log) — lower is better")
axes[0].legend(loc="upper right", fontsize=9)
fig.suptitle("Energy-per-token vs quantisation, all three tiers  (both GPUs penalised at Q3_K_M; Pi CPU monotone)",
             fontsize=11, x=0.01, ha="left")
fig.text(0.01, 0.005, "Three power boundaries (Mac SoC-domains, Jetson board VDD_IN, Pi PMIC rail-sum) — compare "
         "the shape within a tier, not absolute levels across tiers.", fontsize=7.5, color=INK2, ha="left")
fig.tight_layout(rect=(0, 0.03, 1, 0.96)); fig.savefig(f"{OUT}/fig5_energy.png", dpi=200, bbox_inches="tight")
plt.close(fig)

print("wrote:", ", ".join(sorted(os.listdir(OUT))))
