"""Compact, print-sized versions of the results figures (6.4 in wide, 300 dpi, fonts 9–10 pt, no in-image titles or
footers; the caption carries the message, the tables carry the p-values):
  fig4-2_throughput.png  median decode tokens/s per tier and rung (log), one panel per model
  fig4-3_energy.png      gross J/token per tier and rung (log), one panel per model
  fig4-5_conditions.png  HumanEval+ pass@1 under the context conditions, panels stacked
  fig4-6_scale.png       7B closed/open ladders beside the 1.5B, and the memory-matched bars
Data: the per-problem eval snapshots and the latest closed-book perf row per cell."""
import os, csv, glob, json
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
PILOT = os.path.join(ROOT, "proposal-dev", "pilot"); ER = os.path.join(PILOT, "eval-results", "mac"); OUT = os.path.join(HERE, "figures")
Q = ["F16", "Q8_0", "Q4_K_M", "Q3_K_M", "Q2_K"]; X = list(range(5))
QW, PH, B7 = "qwen2.5-coder-1.5b-instruct", "phi-3-mini-4k-instruct", "qwen2.5-coder-7b-instruct"
BLUE, ORANGE, GREEN, PURPLE, INK = "#1f4e9c", "#c8551a", "#1b8a5a", "#6f4ca8", "#111111"
plt.rcParams.update({"font.size": 9, "axes.labelsize": 9, "xtick.labelsize": 8.5, "ytick.labelsize": 8.5, "legend.fontsize": 8.5,
                     "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False})

def p1(model, q, cond=""):
    suf = "" if cond in ("", "closed") else "_" + cond
    d = json.load(open(os.path.join(ER, f"samples_{model}_{q}{suf}-sanitized_eval_results.json"), encoding="utf-8"))["eval"]
    return float(np.mean([1 if d[t][0]["plus_status"] == "pass" else 0 for t in d]))
def ladder(model, cond=""): return [p1(model, q, cond) for q in Q]

def perf(dev):
    rows = []
    for f in sorted(glob.glob(os.path.join(PILOT, "results", dev, "perf_results_2026*.csv"))):
        if "open" in os.path.basename(f): continue
        rows += list(csv.DictReader(open(f, encoding="utf-8")))
    d = {}
    for r in rows:   # latest row per (model, quant) wins (files sorted by timestamp)
        if "imat" in r["model"]: continue
        d[(r["model"], r["quant"])] = r
    return d
PERF = {dev: perf(dev) for dev in ("mac", "jetson", "pi5")}
TIERS = [("mac", "MacBook (Metal)", BLUE), ("jetson", "Jetson (CUDA)", ORANGE), ("pi5", "Pi 5 (CPU)", GREEN)]
def series(dev, model, field):
    out = []
    for q in Q:
        r = PERF[dev].get((model, q))
        v = float(r[field]) if r and r[field] not in ("", "None") else np.nan
        out.append(v)
    return out

# ---- Figure 4.2: throughput
fig, axes = plt.subplots(1, 2, figsize=(6.4, 3.3), sharey=True)
for ax, (m, lab) in zip(axes, ((QW, "Qwen2.5-Coder-1.5B"), (PH, "Phi-3-mini-3.8B"))):
    for dev, dl, c in TIERS: ax.plot(X, series(dev, m, "median_tok_s"), "-o", color=c, lw=1.8, ms=5, label=dl)
    ax.set_yscale("log"); ax.set_xticks(X); ax.set_xticklabels(Q, fontsize=8); ax.grid(True, which="both", axis="y", alpha=0.3)
    ax.text(0.02, 0.97, lab, transform=ax.transAxes, va="top", fontsize=9, weight="bold")
    ax.axhspan(8, 10, color="0.85", alpha=0.6, lw=0)
axes[0].set_ylabel("median decode tokens/s"); fig.legend(*axes[0].get_legend_handles_labels(), loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.01))
plt.tight_layout(rect=(0, 0.07, 1, 1)); fig.savefig(os.path.join(OUT, "fig4-2_throughput.png"), dpi=300); plt.close(fig)

# ---- Figure 4.3: energy per token
fig, axes = plt.subplots(1, 2, figsize=(6.4, 3.3), sharey=True)
for ax, (m, lab) in zip(axes, ((QW, "Qwen2.5-Coder-1.5B"), (PH, "Phi-3-mini-3.8B"))):
    for dev, dl, c in TIERS:
        pw, tk = series(dev, m, "mean_power_w"), series(dev, m, "median_tok_s")
        ax.plot(X, [p / t if (not np.isnan(p) and not np.isnan(t) and t > 0) else np.nan for p, t in zip(pw, tk)], "-o", color=c, lw=1.8, ms=5, label=dl)
    ax.set_yscale("log"); ax.set_xticks(X); ax.set_xticklabels(Q, fontsize=8); ax.grid(True, which="both", axis="y", alpha=0.3)
    ax.text(0.02, 0.97, lab, transform=ax.transAxes, va="top", fontsize=9, weight="bold")
axes[0].set_ylabel("energy per token (J, log)"); fig.legend(*axes[0].get_legend_handles_labels(), loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.01))
plt.tight_layout(rect=(0, 0.07, 1, 1)); fig.savefig(os.path.join(OUT, "fig4-3_energy.png"), dpi=300); plt.close(fig)

# ---- Figure 4.5: context conditions, stacked
fig, axes = plt.subplots(2, 1, figsize=(6.4, 5.4), sharex=True)
for ax, (m, lab, cliff) in zip(axes, ((QW, "Qwen2.5-Coder-1.5B", 4), (PH, "Phi-3-mini-3.8B", 2))):
    ax.axvspan(cliff - 0.45, cliff + 0.45, color="#d43d51", alpha=0.07, lw=0)
    ax.plot(X, ladder(m), "-o", color=INK, lw=2, ms=5.5, label="closed-book (A)", zorder=4)
    ax.plot(X, ladder(m, "open"), "-s", color=BLUE, lw=1.6, ms=5.5, label="frozen BM25 documentation (B)")
    ax.plot(X, ladder(m, "oracle"), "-^", color=GREEN, lw=1.6, ms=5.5, label="oracle-selected documentation (O)")
    if m == QW: ax.plot(X, ladder(m, "r1"), "-D", color=PURPLE, lw=1.6, ms=5, label="model-chosen documentation, grammar (R1)")
    ax.set_ylim(0.1, 0.75); ax.set_ylabel("HumanEval+ pass@1"); ax.grid(axis="y", alpha=0.3)
    ax.text(0.02, 0.93, lab, transform=ax.transAxes, fontsize=9, weight="bold")
    ax.text(cliff, 0.72, "collapse rung", ha="center", fontsize=8, color="#d43d51")
axes[0].legend(loc="lower left", ncol=1); axes[1].set_xticks(X); axes[1].set_xticklabels(Q)
plt.tight_layout(); fig.savefig(os.path.join(OUT, "fig4-5_conditions.png"), dpi=300); plt.close(fig)

# ---- Figure 4.6: scale
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.4, 3.4), gridspec_kw={"width_ratios": [1.7, 1]})
b7c, b7o, qwc = ladder(B7), ladder(B7, "open"), ladder(QW)
a1.plot(X, b7c, "-o", color=BLUE, lw=2, ms=5.5, label="7B closed-book"); a1.plot(X, b7o, "--o", color=BLUE, lw=1.4, ms=4.5, alpha=0.7, label="7B open-book")
a1.plot(X, qwc, "-o", color=ORANGE, lw=2, ms=5.5, label="1.5B closed-book")
a1.axhline(b7c[0] - 0.05, color=BLUE, lw=1, ls=":"); a1.set_xticks(X); a1.set_xticklabels(Q, fontsize=8); a1.set_ylim(0.3, 0.9)
a1.set_ylabel("HumanEval+ pass@1"); a1.grid(axis="y", alpha=0.3); a1.legend(loc="lower left")
bars = a2.bar([0, 1], [qwc[0], b7c[4]], 0.6, color=[ORANGE, BLUE])
for b, v in zip(bars, [qwc[0], b7c[4]]): a2.text(b.get_x() + b.get_width() / 2, v + 0.01, f"{v:.3f}", ha="center", fontsize=9)
a2.set_xticks([0, 1]); a2.set_xticklabels(["1.5B F16\n3.1 GB", "7B Q2_K\n2.9 GB"], fontsize=8); a2.set_ylim(0.3, 0.9); a2.grid(axis="y", alpha=0.3)
plt.tight_layout(); fig.savefig(os.path.join(OUT, "fig4-6_scale.png"), dpi=300); plt.close(fig)
print("wrote 4 figures")
