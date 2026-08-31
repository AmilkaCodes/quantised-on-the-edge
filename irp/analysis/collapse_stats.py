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
print("\nDONE")
