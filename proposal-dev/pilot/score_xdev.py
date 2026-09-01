#!/usr/bin/env python3
"""Score the cross-device spot-check solutions with EvalPlus (run on ONE machine — scoring executes
code and is device-independent). Reports, over the problems shared by all tiers: per-tier pass@1
(base + plus), the cross-device OUTPUT-divergence rate, and the CORRECTNESS-flip rate (where pass/fail
differs across tiers). Companion to cross-device-check.md / decisions D25."""
import json, subprocess, sys, os, glob
from pathlib import Path
from evalplus.data import get_human_eval_plus

MODEL = sys.argv[1] if len(sys.argv) > 1 else "qwen2.5-coder-1.5b-instruct"
RUNG  = sys.argv[2] if len(sys.argv) > 2 else "Q4_K_M"
DEVICES = ["mac", "jetson", "pi5"]
ROOT = Path("results")
ENV = {**os.environ, "EVALPLUS_MAX_MEMORY_BYTES": "-1"}
# EvalPlus asserts ALL problems are present, so pad the K-subset up to the full set with stubs
# (stubs score as fail and are ignored — we only read back the real K solutions).
ALL_TASKS = list(get_human_eval_plus().keys())

def score(dev):
    src = ROOT / dev / f"xdev_{MODEL}_{RUNG}.json"
    sols = json.loads(src.read_text())
    jsonl = ROOT / dev / f"xdev_{MODEL}_{RUNG}_samples.jsonl"
    with jsonl.open("w") as f:
        for tid in ALL_TASKS:
            f.write(json.dumps({"task_id": tid, "solution": sols.get(tid, "    pass\n")}) + "\n")
    subprocess.run([sys.executable, "-m", "evalplus.sanitize", "--samples", str(jsonl)],
                   check=False, capture_output=True)
    san = jsonl.with_name(jsonl.stem + "-sanitized.jsonl")
    target = san if san.exists() else jsonl
    subprocess.run([sys.executable, "-m", "evalplus.evaluate", "--dataset", "humaneval",
                    "--samples", str(target)], check=False, capture_output=True, env=ENV)
    er = target.with_name(target.stem + "_eval_results.json")
    if not er.exists():
        cands = glob.glob(str(ROOT / dev / "xdev_*eval_results.json"))
        er = Path(sorted(cands)[-1]) if cands else er
    ev = json.loads(er.read_text())["eval"]
    status = {t: (ev[t][0]["base_status"], ev[t][0]["plus_status"]) for t in ev}
    return sols, status

data = {d: score(d) for d in DEVICES}
shared = sorted(set.intersection(*[set(data[d][0]) for d in DEVICES]),
                key=lambda t: int(t.split("/")[1]))
K = len(shared)
print(f"\n==== {MODEL}:{RUNG}  |  shared problems K={K} ====")
print("per-tier pass@1 over the SAME K problems:")
for d in DEVICES:
    st = data[d][1]
    p = sum(st[t][1] == "pass" for t in shared) / K
    b = sum(st[t][0] == "pass" for t in shared) / K
    print(f"  {d:7s} base={b:.3f}  plus={p:.3f}")

diff_out = flip_base = flip_plus = 0
flips = []
for t in shared:
    sols = [data[d][0][t] for d in DEVICES]
    base = [data[d][1][t][0] for d in DEVICES]
    plus = [data[d][1][t][1] for d in DEVICES]
    if len(set(sols)) > 1: diff_out += 1
    if len(set(base)) > 1: flip_base += 1
    if len(set(plus)) > 1:
        flip_plus += 1
        flips.append((t, dict(zip(DEVICES, plus))))
print(f"\noutput differs across tiers : {diff_out}/{K} ({diff_out/K:.0%})")
print(f"pass/fail flips (base tests): {flip_base}/{K} ({flip_base/K:.0%})")
print(f"pass/fail flips (plus tests): {flip_plus}/{K} ({flip_plus/K:.0%})")
for t, fl in flips:
    print(f"   {t}: {fl}")
