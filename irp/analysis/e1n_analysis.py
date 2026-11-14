#!/usr/bin/env python3
"""E1-N analysis — neutral context (N) vs closed-book (A) and vs frozen documentation (B), Qwen 1.5B F16.
Same machinery as e1_analysis.py: per-problem plus_status, paired bootstrap 95% CI on the difference
(10,000 resamples, numpy default_rng(0) fresh per comparison, so B−A reproduces Table D.8), exact McNemar.
Exploratory grade, uncorrected (protocol irp/extensions/e1n-neutral-context-control.md).
Run from proposal-dev/pilot (reads results/mac/…)."""
import json
import numpy as np
from statsmodels.stats.contingency_tables import mcnemar

FULL = "qwen2.5-coder-1.5b-instruct"

def load(sfx):
    d = json.load(open(f"results/mac/samples_{FULL}_F16{sfx}-sanitized_eval_results.json"))["eval"]
    items = sorted(d, key=lambda t: int(t.split("/")[1]))
    return items, np.array([1 if d[t][0]["plus_status"] == "pass" else 0 for t in items])

conds = {"A": load(""), "B": load("_open"), "N": load("_neutral")}
assert conds["A"][0] == conds["B"][0] == conds["N"][0], "task-order mismatch"
for k, (_, v) in conds.items():
    print(f"  {k}: pass@1 = {v.mean():.3f}  ({v.sum()}/{len(v)})")

def compare(x, y):
    a, b = conds[y][1], conds[x][1]                    # difference = x − y
    n = len(a)
    idx = np.random.default_rng(0).integers(0, n, size=(10000, n))
    lo, hi = np.percentile(b[idx].mean(axis=1) - a[idx].mean(axis=1), [2.5, 97.5])
    n01 = int(((a == 1) & (b == 0)).sum()); n10 = int(((a == 0) & (b == 1)).sum())
    both = int(((a == 1) & (b == 1)).sum()); neither = int(((a == 0) & (b == 0)).sum())
    p = mcnemar([[both, n01], [n10, neither]], exact=True).pvalue
    print(f"  {x} − {y}: {100 * (b.mean() - a.mean()):+.1f} pp [{100 * lo:+.1f}, {100 * hi:+.1f}]  "
          f"McNemar p = {p:.3g}  ({y}-pass/{x}-fail = {n01}, {y}-fail/{x}-pass = {n10})")

print("\nE1-N, Qwen2.5-Coder-1.5B F16, HumanEval+ (plus), n = 164")
compare("B", "A")                                      # reference: must equal Table D.8's F16 row
compare("N", "A")
compare("N", "B")
