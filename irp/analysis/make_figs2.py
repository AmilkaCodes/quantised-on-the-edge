#!/usr/bin/env python3
"""IRP figures, batch 2 — E1/E1-R conditions, context cost, scale, dose-response,
imatrix, deployment, collapse-rung signature. House style per make_figs.py.
Data authority: per-problem eval_results snapshots (pilot/eval-results/mac) for ALL quality
series, R1 included (Mac re-score 2026-09-14 confirmed the snapshots with zero flips; the
harness summary.json pass@1 parse is the stale variant — see results-audit-20260914.md §1);
perf CSVs pinned per figure (never glob-latest: the newest files are 7B-only)."""
import json, csv, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))            # repo root (irp/analysis -> repo)
PILOT = os.path.join(ROOT, "proposal-dev", "pilot")
ER = os.path.join(PILOT, "eval-results", "mac")
RES = os.path.join(PILOT, "results")
OUT = os.path.join(HERE, "figures"); os.makedirs(OUT, exist_ok=True)

QUANTS = ["F16", "Q8_0", "Q4_K_M", "Q3_K_M", "Q2_K"]
X = list(range(len(QUANTS)))
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
PURPLE, RED, GREY = "#8464c8", "#d43d51", "#9a9891"
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

def p1(model, q, cond=""):
    suf = "" if cond in ("", "closed") else "_" + cond
    f = os.path.join(ER, f"samples_{model}_{q}{suf}-sanitized_eval_results.json")
    d = json.load(open(f, encoding="utf-8"))["eval"]
    return float(np.mean([1 if d[t][0]["plus_status"] == "pass" else 0 for t in d]))

def ladder(model, cond=""):
    return [p1(model, q, cond) for q in QUANTS]

QW, PH, B7 = "qwen2.5-coder-1.5b-instruct", "phi-3-mini-4k-instruct", "qwen2.5-coder-7b-instruct"

def r1_summary(q):
    return json.load(open(os.path.join(RES, "mac", f"r1_{q}", "summary.json"), encoding="utf-8"))

def perf_csv(dev, name):
    rows = list(csv.DictReader(open(os.path.join(RES, dev, name), encoding="utf-8")))
    return {(r["model"], r["quant"]): r for r in rows}

# ======== FIG 6 — context conditions: A / B / O / R1 per rung ========
fig, axes = plt.subplots(1, 2, figsize=(11.6, 4.9), sharey=True)
SPECS = [(QW, "Qwen2.5-Coder-1.5B (code-specialised)", axes[0], 4),
         (PH, "Phi-3-mini-3.8B (general)", axes[1], 2)]
for model, label, ax, cliff in SPECS:
    A, B, O = ladder(model), ladder(model, "open"), ladder(model, "oracle")
    ax.plot(X, A, "-o", color=INK, lw=2.2, ms=6, label="A  closed-book", zorder=4)
    ax.plot(X, B, "-s", color=BLUE, lw=1.8, ms=6, label="B  frozen BM25 docs", zorder=3)
    ax.plot(X, O, "-^", color=AQUA, lw=1.8, ms=6, label="O  oracle docs (instrument)", zorder=3)
    if model == QW:
        R1 = ladder(model, "r1")
        ax.plot(X, R1, "-D", color=PURPLE, lw=1.8, ms=5.5,
                label="R1 model-chosen docs (grammar)", zorder=3)
    ax.axvspan(cliff - 0.45, cliff + 0.45, color=RED, alpha=0.06, zorder=1)
    ax.annotate("collapse rung", (cliff, 0.06), ha="center", color=RED, fontsize=8.5)
    ax.set_xticks(X); ax.set_xticklabels(QUANTS); ax.set_title(label, fontsize=11, loc="left")
    ax.set_xlabel("Quantisation"); ax.set_ylim(0, 0.75)
    ax.legend(loc="lower left", fontsize=8.5)
axes[0].set_ylabel("HumanEval+ pass@1 (plus)")
fig.suptitle("Injected context NEVER helps — closed-book leads every condition at every rung; "
             "the harm is largest at each model's own collapse rung", fontsize=11, x=0.01, ha="left")
fig.text(0.01, 0.005, "Oracle = upper-bound selection instrument (chunks chosen by overlap with the canonical "
         "solution; solution text never enters a prompt). Significant harms (McNemar): Qwen Q2 (B p=.007, O p=.020), "
         "Phi Q4 (B p=.0008, O p=.021); R1 < A at Q4/Q3/Q2 (p=.002/.008/.003).", fontsize=7.5, color=INK2)
fig.tight_layout(rect=(0, 0.045, 1, 0.94)); fig.savefig(f"{OUT}/fig6_conditions.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# ======== FIG 7 — the price of context is a tier property (Qwen Q4, closed vs open) ========
E1P = {("mac", "closed"): "perf_results_20260912_230524.csv",
       ("mac", "open"):   "perf_results_open_20260912_230450.csv",
       ("jetson", "closed"): "perf_results_20260912_221734.csv",
       ("jetson", "open"):   "perf_results_open_20260912_221455.csv",
       ("pi5", "closed"): "perf_results_20260912_222457.csv",
       ("pi5", "open"):   "perf_results_open_20260912_221421.csv"}
tiers = [("mac", "Mac (Metal)"), ("jetson", "Jetson (CUDA)"), ("pi5", "Pi 5 (CPU)")]
ttft, rss = {}, {}
for (dev, cond), fn in E1P.items():
    r = perf_csv(dev, fn)[(QW, "Q4_K_M")]
    ttft[(dev, cond)] = float(r["mean_ttft_ms"])
    rss[(dev, cond)] = float(r["peak_rss_mb"]) / 1024
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4))
w, xs = 0.36, np.arange(3)
for ax, data, ylab, title in ((ax1, ttft, "Mean TTFT (ms, log)", "Time-to-first-token"),
                              (ax2, rss, "Peak RSS (GB)", "Peak memory")):
    c = [data[(d, "closed")] for d, _ in tiers]; o = [data[(d, "open")] for d, _ in tiers]
    ax.bar(xs - w/2, c, w, color=INK, label="closed-book")
    ax.bar(xs + w/2, o, w, color=BLUE, label="open-book (k=2 chunks)")
    for i in range(3):
        ax.annotate(f"×{o[i]/c[i]:.1f}", (xs[i] + w/2, o[i]), ha="center", va="bottom",
                    fontsize=8.5, color=BLUE, fontweight="bold")
    ax.set_xticks(xs); ax.set_xticklabels([t for _, t in tiers])
    ax.set_title(title, fontsize=11, loc="left"); ax.set_ylabel(ylab)
ax1.set_yscale("log"); ax1.axhspan(1000, 2000, color=RED, alpha=0.10)
ax1.annotate("registered TTFT floor 1–2 s", (0.02, 1350), fontsize=8, color=RED)
ax1.legend(fontsize=9)
fig.suptitle("The price of context is a tier property (Qwen 1.5B @ Q4_K_M): prefill + KV cost is trivial on "
             "Metal/CUDA, breaks the interactive floor on the Pi's CPU", fontsize=11, x=0.01, ha="left")
fig.tight_layout(rect=(0, 0, 1, 0.93)); fig.savefig(f"{OUT}/fig7_context_cost.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# ======== FIG 8 — scale: 7B ladder + memory-matched comparison ========
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.4, 4.7), gridspec_kw={"width_ratios": [1.55, 1]})
b7c, b7o, qwc = ladder(B7), ladder(B7, "open"), ladder(QW)
ax1.plot(X, b7c, "-o", color=BLUE, lw=2.2, ms=6.5, label="7B closed", zorder=4)
ax1.plot(X, b7o, "--o", color=BLUE, lw=1.6, ms=5, alpha=0.65, label="7B open (docs) — hurt at EVERY rung", zorder=3)
ax1.plot(X, qwc, "-o", color=ORANGE, lw=2.2, ms=6.5, label="1.5B closed", zorder=4)
ax1.axhspan(b7c[0] - 0.05, b7c[0], color=BLUE, alpha=0.08)
ax1.annotate("7B 5pp margin band — never left: threshold NONE", (0.05, b7c[0] - 0.047),
             fontsize=8, color=BLUE)
ax1.annotate("−22.6 pp\np=1.2×10⁻⁷", (4, qwc[4]), color=ORANGE, fontsize=8.5, ha="center",
             xytext=(0, -34), textcoords="offset points",
             arrowprops=dict(arrowstyle="->", color=ORANGE, lw=1.2))
ax1.set_xticks(X); ax1.set_xticklabels(QUANTS); ax1.set_ylim(0, 0.95)
ax1.set_xlabel("Quantisation"); ax1.set_ylabel("HumanEval+ pass@1 (plus)")
ax1.set_title("Collapse is a small-model phenomenon…", fontsize=11, loc="left")
ax1.legend(loc="lower left", fontsize=9)
bars = ax2.bar([0, 1], [qwc[0], b7c[4]], 0.55, color=[ORANGE, BLUE])
ax2.set_xticks([0, 1]); ax2.set_xticklabels(["1.5B @ F16\n3.1 GB", "7B @ Q2_K\n2.9 GB"])
for b, v in zip(bars, [qwc[0], b7c[4]]):
    ax2.annotate(f"{v:.3f}", (b.get_x() + b.get_width()/2, v), ha="center", va="bottom",
                 fontsize=11, fontweight="bold")
ax2.annotate("+18 pp at\nmatched memory", (0.5, 0.71), ha="center", fontsize=10, color=INK)
ax2.set_ylim(0, 0.95); ax2.set_ylabel("pass@1 (plus)")
ax2.set_title("…and quality-per-byte favours\nthe big-quantised model", fontsize=11, loc="left")
fig.suptitle("Scale rescues quantisation-robustness, not context-robustness (7B open-book harm significant at "
             "all 5 rungs incl. F16, p ≤ .019)", fontsize=11, x=0.01, ha="left")
fig.tight_layout(rect=(0, 0, 1, 0.92)); fig.savefig(f"{OUT}/fig8_scale.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# ======== FIG 9 — invocation is a policy dial (dose-response) ========
fig, ax = plt.subplots(figsize=(7.6, 4.4))
levels = ["nudge\n(prompt suggests)", "mandate\n(system requires)", "force\n(tool_choice)"]
xs = np.arange(3); w = 0.36
b4 = ax.bar(xs - w/2, [0.00, 0.40, 0.80], w, color=BLUE, label="Qwen3-4B (tool-trained)")
b15 = ax.bar(xs + w/2, [0.00, 0.00, 0.00], w, color=ORANGE, label="Qwen 1.5B (not tool-trained)")
for x, v in zip(xs, [0.00, 0.40, 0.80]):
    ax.annotate(f"{v:.2f}", (x - w/2, v), ha="center", va="bottom", fontsize=10, fontweight="bold", color=BLUE)
    ax.annotate("0.00", (x + w/2, 0.004), ha="center", va="bottom", fontsize=10, fontweight="bold", color=ORANGE)
ax.annotate("M3 = 1.0 wherever a tool\nphase completes (overall\npass unchanged at 0.80)",
            (2.42, 0.55), ha="left", va="center", fontsize=9, color=BLUE)
ax.annotate("1.5B forced → degeneration\n20/20 (coercion cannot\ncreate capability)",
            (2.42, 0.16), ha="left", va="center", fontsize=8.5, color=ORANGE)
ax.set_xlim(-0.55, 3.6)
ax.set_xticks(xs); ax.set_xticklabels(levels, fontsize=9.5)
ax.set_ylabel("M1 valid-call rate (K=20, F16)"); ax.set_ylim(0, 1.0)
ax.set_title("Tool invocation is a policy dial, not a capability cliff — for the model that has the capability",
             fontsize=11, loc="left")
ax.legend(loc="upper left", fontsize=9)
fig.text(0.01, 0.005, "Reasoning-trace probe (K=5): in 4/5 episodes the tool never enters deliberation; in the 5th the model "
         "explicitly weighs and dismisses it — a judgement Condition B shows is empirically correct.", fontsize=7.5, color=INK2)
fig.tight_layout(rect=(0, 0.04, 1, 1)); fig.savefig(f"{OUT}/fig9_dose_response.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# ======== FIG 10 — imatrix calibration moves the cliff; the context harm follows it ========
fig, axes = plt.subplots(1, 3, figsize=(12.6, 4.6), gridspec_kw={"width_ratios": [1, 1, 0.85]})
IM = {QW: QW + "-imat", PH: PH + "-imat"}
for ax, model, label, col in ((axes[0], QW, "Qwen2.5-Coder-1.5B", ORANGE),
                              (axes[1], PH, "Phi-3-mini-3.8B", BLUE)):
    N = ladder(model)
    I = [np.nan, np.nan] + [p1(IM[model], q) for q in ("Q4_K_M", "Q3_K_M", "Q2_K")]
    ax.plot(X, N, "-o", color=col, lw=2, ms=6, label="naive ladder", zorder=3)
    ax.plot(X, I, "-o", color=AQUA, lw=2, ms=6, label="imatrix-calibrated", zorder=4)
    ax.axhspan(N[0] - 0.05, N[0], color=GREY, alpha=0.18)
    ax.annotate("F16 − 5 pp margin", (0.05, N[0] - 0.047), fontsize=7.5, color=INK2)
    ax.set_xticks(X); ax.set_xticklabels(QUANTS); ax.set_ylim(0.1, 0.75)
    ax.set_title(label, fontsize=11, loc="left"); ax.set_xlabel("Quantisation")
    ax.legend(loc="lower left", fontsize=8.5)
axes[0].set_ylabel("HumanEval+ pass@1 (plus)")
axes[1].annotate("threshold moves\nTWO rungs (Q4→Q2)", (2.5, 0.66), ha="center", fontsize=9, color=AQUA)
ax = axes[2]
cells = ["Phi @ Q4\n(naive)", "Phi @ Q4\n(calibrated)", "Qwen @ Q2\n(naive)", "Qwen @ Q2\n(calibrated)"]
harm = [-.152, p1(IM[PH], "Q4_K_M", "open") - p1(IM[PH], "Q4_K_M"),
        -.098, p1(IM[QW], "Q2_K", "open") - p1(IM[QW], "Q2_K")]
cols = [RED, AQUA, RED, RED]
bars = ax.bar(range(4), harm, 0.6, color=cols)
for i, (b, v) in enumerate(zip(bars, harm)):
    ax.annotate(f"{v:+.3f}", (b.get_x() + b.get_width()/2, v), ha="center", va="top", fontsize=9, fontweight="bold")
ax.annotate("harm VANISHES where\ncalibration un-broke the rung", (0.5, -0.215), ha="center", fontsize=8, color=AQUA)
ax.annotate("harm PERSISTS where the\nrung stays cliff-adjacent", (2.5, -0.26), ha="center", fontsize=8, color=RED)
ax.set_xticks(range(4)); ax.set_xticklabels(cells, fontsize=8)
ax.set_ylabel("Context harm Δ(open − closed)"); ax.set_ylim(-0.30, 0.03)
ax.axhline(0, color=INK2, lw=1)
ax.set_title("The harm follows the cliff,\nnot the bit-width", fontsize=10.5, loc="left")
fig.suptitle("E2b: stock imatrix calibration moves Phi-3's collapse threshold two rungs and halves Qwen's cliff — "
             "and the context harm co-moves with the residual damage", fontsize=11, x=0.01, ha="left")
fig.tight_layout(rect=(0, 0, 1, 0.92)); fig.savefig(f"{OUT}/fig10_imatrix.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# ======== FIG 11 — 7B deployment map (E2c) ========
P7 = {"mac": perf_csv("mac", "perf_results_20260914_091846.csv"),
      "jetson": perf_csv("jetson", "perf_results_20260914_092435.csv"),
      "pi5": perf_csv("pi5", "perf_results_20260914_092659.csv")}
fig, ax = plt.subplots(figsize=(8.6, 4.8))
for dev, label, col in (("mac", "Mac (Metal)", BLUE), ("jetson", "Jetson (CUDA)", ORANGE), ("pi5", "Pi 5 (CPU)", AQUA)):
    y = [float(P7[dev][(B7, q)]["median_tok_s"]) if (B7, q) in P7[dev] else np.nan for q in QUANTS]
    ax.plot(X, y, "-o", color=col, lw=2, ms=6.5, label=label, zorder=3)
    for i, q in enumerate(QUANTS):
        if not np.isnan(y[i]):
            ax.annotate(f"{y[i]:g}", (i, y[i]), fontsize=7.5, color=col, xytext=(0, 6),
                        textcoords="offset points", ha="center")
ax.axhspan(8, 10, color=RED, alpha=0.10)
ax.annotate("registered SLO floor 8–10 tok/s", (0.02, 8.6), fontsize=8, color=RED)
ax.annotate("does not fit (8 GB):\nF16, Q8_0", (0.5, 13), ha="center", fontsize=8, color=ORANGE)
ax.annotate("F16 FITS on the 16 GB Pi\n(0.8 tok/s — batch only)", (0.55, 0.52), fontsize=8, color=AQUA)
ax.set_yscale("log"); ax.set_xticks(X); ax.set_xticklabels(QUANTS)
ax.set_xlabel("Quantisation"); ax.set_ylabel("Median decode tok/s (log)")
ax.set_title("Where does the memory-matched winner actually run? 7B decode throughput by tier\n"
             "Jetson serves 7B@Q2_K above the floor (11.1 tok/s); the Pi cannot serve the 7B interactively at any rung",
             fontsize=11, loc="left")
ax.legend(loc="upper left", fontsize=9)
fig.tight_layout(); fig.savefig(f"{OUT}/fig11_deployment.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# ======== FIG 12 — the collapse-rung signature (five phenomena, one axis) ========
# Verified per-rung significance/breaks from the committed analyses (locators in results-inventory.md)
ROWS = [
    ("Quality collapse (>5pp + McNemar)", {QW: [4], PH: [2, 3, 4]}),
    ("Imposed-context harm significant (B)", {QW: [4], PH: [2]}),
    ("Oracle-context harm significant (O)", {QW: [4], PH: [2]}),
    ("Query formulation breaks (R1: M1′ ↓, degen ×5)", {QW: [4], PH: None}),
    ("Context harm persists after calibration", {QW: [4], PH: []}),
]
fig, axes = plt.subplots(1, 2, figsize=(11.8, 4.0), sharey=True)
for ax, model, label, cliff in ((axes[0], QW, "Qwen2.5-Coder-1.5B — everything breaks at Q2_K", 4),
                                (axes[1], PH, "Phi-3-mini-3.8B — everything breaks at Q4_K_M", 2)):
    ax.axvspan(cliff - 0.45, cliff + 0.45, color=RED, alpha=0.08, zorder=1)
    for yi, (rname, hits) in enumerate(ROWS):
        h = hits[model]
        if h is None:
            ax.annotate("n/a (no tool template)", (2, yi), fontsize=7.5, color=GREY, ha="center", va="center")
            continue
        ax.scatter(X, [yi]*5, s=90, facecolors="none", edgecolors=GRID, zorder=2)
        if h:
            ax.scatter(h, [yi]*len(h), s=120, color=RED, zorder=3)
        elif rname.startswith("Context harm persists"):
            ax.annotate("harm gone once calibration\nun-broke Q4", (2, yi), fontsize=7.5, color=AQUA,
                        ha="center", va="center")
    ax.set_xticks(X); ax.set_xticklabels(QUANTS)
    ax.set_title(label, fontsize=10.5, loc="left")
    ax.set_ylim(-0.7, len(ROWS) - 0.3); ax.invert_yaxis(); ax.grid(False)
axes[0].set_yticks(range(len(ROWS))); axes[0].set_yticklabels([r for r, _ in ROWS], fontsize=8.5)
fig.suptitle("The collapse-rung signature: independent phenomena align on one rung per model — damage is "
             "rung-synchronised and broad-spectrum, not capability-by-capability", fontsize=11, x=0.01, ha="left")
fig.text(0.01, 0.005, "Filled = significant/broken at that rung (committed analyses; exploratory, uncorrected). Phi-3 quality also "
         "fails the 5pp margin at Q3/Q2 (once broken, stays broken); the SIGNATURE claim is the alignment of first-break rungs.",
         fontsize=7.5, color=INK2)
fig.tight_layout(rect=(0, 0.05, 1, 0.92)); fig.savefig(f"{OUT}/fig12_signature.png", dpi=200, bbox_inches="tight")
plt.close(fig)

print("wrote:", ", ".join(sorted(f for f in os.listdir(OUT) if f.endswith(".png"))))
