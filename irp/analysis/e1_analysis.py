#!/usr/bin/env python3
"""E1 Condition B analysis (RQ1b / H1c) — open-book (B) vs closed-book (A), per rung, same 164 problems.
Mirrors the closed-book machinery (collapse_stats.py): per-rung pass@1 + bootstrap 95% CIs, paired McNemar
B-vs-A, per-condition 5pp collapse threshold, and the HEADLINE interaction Δ(B−A) per rung with its CI.
Run from proposal-dev/pilot (reads results/mac/…). Requires the closed-book eval_results (quality axis)
and the open-book eval_results (samples_*_open-sanitized_eval_results.json) to both exist."""
import json, glob
import numpy as np
from statsmodels.stats.contingency_tables import mcnemar

QUANTS = ["F16", "Q8_0", "Q4_K_M", "Q3_K_M", "Q2_K"]
MODELS = {"qwen2.5-coder-1.5b": "qwen2.5-coder-1.5b-instruct",
          "phi-3-mini": "phi-3-mini-4k-instruct"}
MARGIN = 0.05
rng = np.random.default_rng(0)

def load(full, q, cond):
    sfx = "" if cond == "A" else "_open"
    hits = glob.glob(f"results/mac/samples_{full}_{q}{sfx}-sanitized_eval_results.json")
    if not hits:
        return None
    d = json.load(open(hits[0]))["eval"]
    items = sorted(d, key=lambda t: int(t.split("/")[1]))
    return items, np.array([1 if d[t][0]["plus_status"] == "pass" else 0 for t in items])

for short, full in MODELS.items():
    print(f"\n================ {short} :  open-book (B) vs closed-book (A) ================")
    print(f"  {'rung':7s} {'A pass@1':>9} {'B pass@1':>9} {'Δ(B−A)':>9}  {'Δ 95% CI':>18}  {'McNemar p':>10}  n01/n10")
    deltas = {}
    passA, passB = {}, {}
    for q in QUANTS:
        ra, rb = load(full, q, "A"), load(full, q, "B")
        if ra is None or rb is None:
            print(f"  {q:7s}  (missing {'A' if ra is None else ''}{'B' if rb is None else ''})")
            continue
        (ia, a), (ib, b) = ra, rb
        assert ia == ib, f"task-order mismatch {q}"
        n = len(a)
        pa, pb = a.mean(), b.mean()
        passA[q], passB[q] = pa, pb
        d = pb - pa
        deltas[q] = d
        idx = rng.integers(0, n, size=(10000, n))
        dbs = b[idx].mean(axis=1) - a[idx].mean(axis=1)
        lo, hi = np.percentile(dbs, [2.5, 97.5])
        n01 = int(((a == 1) & (b == 0)).sum())   # closed-pass, open-fail
        n10 = int(((a == 0) & (b == 1)).sum())   # closed-fail, open-pass (open rescued)
        both = int(((a == 1) & (b == 1)).sum()); neither = int(((a == 0) & (b == 0)).sum())
        p = mcnemar([[both, n01], [n10, neither]], exact=True).pvalue
        star = "*" if p < 0.05 else " "
        print(f"  {q:7s} {pa:9.3f} {pb:9.3f} {d:+9.3f}  [{lo:+.3f},{hi:+.3f}]  {p:10.3e}{star}  {n01}/{n10}")

    # per-condition 5pp collapse threshold (first rung >5pp below that condition's own F16)
    def thr(P):
        f = P.get("F16")
        return next((q for q in QUANTS[1:] if q in P and (f - P[q]) > MARGIN), None) if f is not None else None
    print(f"  5pp collapse threshold: closed(A) = {thr(passA)} · open(B) = {thr(passB)}")

    # headline interaction: does the open-book benefit change down the ladder?
    if deltas:
        seq = [f"{q}:{deltas[q]:+.3f}" for q in QUANTS if q in deltas]
        print(f"  Δ(B−A) by rung: {' '.join(seq)}")
        lad = [deltas[q] for q in QUANTS if q in deltas]
        trend = ("GROWS (help increases as bits drop)" if lad[-1] > lad[0] + 0.02 else
                 "SHRINKS (help fades as bits drop)" if lad[-1] < lad[0] - 0.02 else
                 "≈FLAT (help roughly constant → H0c not clearly rejected)")
        print(f"  interaction (H1c): F16 Δ={lad[0]:+.3f} → Q2 Δ={lad[-1]:+.3f}  ⇒ {trend}")
print("\nDONE")
