#!/usr/bin/env python3
"""Collapse-threshold statistics (quality axis, Mac). Same 164 HumanEval+ problems at each quant
rung -> PAIRED tests on per-problem pass/fail:
  - Cochran's Q: does pass rate differ across the 5 rungs at all? (omnibus)
  - McNemar (exact): F16 baseline vs each rung -> where is the significant drop (the threshold)?
Greedy+seed0 => pass@1 is deterministic, so this tests the 164-problem sampling uncertainty, not
run-to-run noise (which is 0)."""
import json
import numpy as np
from statsmodels.stats.contingency_tables import mcnemar, cochrans_q

QUANTS = ["F16", "Q8_0", "Q4_K_M", "Q3_K_M", "Q2_K"]
MODELS = {"qwen2.5-coder-1.5b": "qwen2.5-coder-1.5b-instruct",
          "phi-3-mini": "phi-3-mini-4k-instruct"}
PATH = "results/mac/samples_{full}_{q}-sanitized_eval_results.json"

def load(full, q):
    d = json.load(open(PATH.format(full=full, q=q)))["eval"]
    items = sorted(d.keys(), key=lambda t: int(t.split("/")[1]))
    plus = [1 if d[t][0]["plus_status"] == "pass" else 0 for t in items]
    base = [1 if d[t][0]["base_status"] == "pass" else 0 for t in items]
    return items, np.array(base), np.array(plus)

for short, full in MODELS.items():
    print(f"\n================ {short} ================")
    tasks0, P, B = None, {}, {}
    for q in QUANTS:
        items, b, p = load(full, q)
        tasks0 = tasks0 or items
        assert items == tasks0, "task-order mismatch!"
        P[q], B[q] = p, b
        print(f"  {q:7s} pass@1  plus={p.mean():.3f}  base={b.mean():.3f}  (n={len(p)})")

    arr = np.array([P[q] for q in QUANTS]).T          # 164 x 5 (plus)
    cq = cochrans_q(arr)
    print(f"  --- Cochran's Q (plus, 5 rungs): Q={cq.statistic:.2f}, df={len(QUANTS)-1}, p={cq.pvalue:.3e}")
    f16 = P["F16"]
    print("  --- McNemar (exact), plus, F16 vs rung:")
    for q in QUANTS[1:]:
        r = P[q]
        lost = int(((f16 == 1) & (r == 0)).sum())     # passed@F16, failed@rung
        gain = int(((f16 == 1) & (r == 0)).sum())     # placeholder (fixed below)
        gain = int(((f16 == 0) & (r == 1)).sum())     # failed@F16, passed@rung
        both = int(((f16 == 1) & (r == 1)).sum())
        neither = int(((f16 == 0) & (r == 0)).sum())
        tbl = [[both, lost], [gain, neither]]
        m = mcnemar(tbl, exact=True)
        net = f16.mean() - r.mean()
        frac_broken = lost / max(int(f16.sum()), 1)   # of F16-passing problems, share broken at rung
        print(f"      F16 vs {q:7s}: net_drop={net:+.3f}  lost={lost} gained={gain} "
              f"(of {int(f16.sum())} F16-passes, {frac_broken:.0%} broken)  McNemar p={m.pvalue:.3e}")

    # --- Pre-registered 5pp margin + bootstrap 95% CIs (percentile, B=10000, seed 0) ---
    # Registered (summative final-body.md): quality-acceptable = pass@1 within 5pp of F16;
    # collapse threshold = first rung >5pp below F16; bootstrap 95% CI accompanies each pass@1;
    # margin verdicts reported WITH their intervals (per-pass@1 CI ~±7pp is WIDER than 5pp, but the
    # PAIRED drop CI is tighter -> that is the correct interval for the drop, and why McNemar rejects).
    MARGIN = 0.05
    rng = np.random.default_rng(0)
    Bn, n = 10000, len(f16)
    idx = rng.integers(0, n, size=(Bn, n))            # ONE shared resample per draw -> paired
    f16_bs = f16[idx].mean(axis=1)
    print(f"  --- 5pp margin + bootstrap 95% CI (B={Bn}); drop = F16 - rung (+ve = degradation) ---")
    for q in QUANTS:
        r = P[q]; p1 = r.mean()
        clo, chi = np.percentile(r[idx].mean(axis=1), [2.5, 97.5])       # per-pass@1 CI (as registered)
        drop = f16.mean() - p1
        dlo, dhi = np.percentile(f16_bs - r[idx].mean(axis=1), [2.5, 97.5])  # PAIRED drop CI
        if q == "F16":
            verdict = "baseline"
        elif drop <= MARGIN:
            verdict = "WITHIN 5pp (acceptable)" + ("" if dhi <= MARGIN else "  [CI straddles 5pp]")
        else:
            verdict = "OUTSIDE 5pp (collapse)" + ("" if dlo > MARGIN else "  [CI straddles 5pp]")
        print(f"      {q:7s} pass@1={p1:.3f} 95%CI[{clo:.3f},{chi:.3f}]  "
              f"drop={drop:+.3f} 95%CI[{dlo:+.3f},{dhi:+.3f}]  -> {verdict}")
    thr = next((q for q in QUANTS[1:] if (f16.mean() - P[q].mean()) > MARGIN), None)
    print(f"  --- pre-registered margin threshold (first rung >5pp below F16): {thr}")
print("\nDONE")
