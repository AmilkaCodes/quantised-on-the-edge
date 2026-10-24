#!/usr/bin/env python3
"""Score the full-ladder cross-device replication (registered addendum xdev-full, 2026-10-24) with EvalPlus and compare every
tier with the Mac reference. Run on the Mac only: scoring executes generated code and is device-independent.

    python score_xdev_full.py                      # every model x rung x device that has an xdev_*_full164.json file
    python score_xdev_full.py qwen2.5-coder-1.5b-instruct Q2_K   # one cell

For each (model, rung) it reports, per device: plus-status pass@1 over all 164 problems, the drop from the device's own F16
(where that device holds F16), the output-identity rate against the Mac, and the pass flips against the Mac (plus status),
split into Mac-pass/device-fail (b) and Mac-fail/device-pass (c), with the exact two-sided McNemar p for b against c.
Writes results/xdev_full164_summary.json and results/xdev_full164_summary.md; leaves the registered K=50 files untouched.
"""
import json, subprocess, sys, os, glob, math
from pathlib import Path
from evalplus.data import get_human_eval_plus

TAG = "full164"
ROOT = Path(__file__).resolve().parent / "results"
DEVICES = ["mac", "jetson", "pi5"]
RUNGS = ["F16", "Q8_0", "Q4_K_M", "Q3_K_M", "Q2_K"]
ENV = {**os.environ, "EVALPLUS_MAX_MEMORY_BYTES": "-1"}
ALL_TASKS = list(get_human_eval_plus().keys())


def binom_two_sided(b, c):
    """Exact McNemar: two-sided binomial test of b against c with p = 1/2 (b + c discordant pairs)."""
    n = b + c
    if n == 0: return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def score(dev, model, rung):
    src = ROOT / dev / f"xdev_{model}_{rung}_{TAG}.json"
    if not src.exists(): return None
    sols = json.loads(src.read_text())
    jsonl = ROOT / dev / f"xdev_{model}_{rung}_{TAG}_samples.jsonl"
    with jsonl.open("w") as f:
        for tid in ALL_TASKS:
            f.write(json.dumps({"task_id": tid, "solution": sols.get(tid, "    pass\n")}) + "\n")
    subprocess.run([sys.executable, "-m", "evalplus.sanitize", "--samples", str(jsonl)], check=False, capture_output=True)
    san = jsonl.with_name(jsonl.stem + "-sanitized.jsonl"); target = san if san.exists() else jsonl
    for stale in glob.glob(str(ROOT / dev / f"xdev_{model}_{rung}_{TAG}*eval_results.json")): os.remove(stale)   # EvalPlus reuses caches
    subprocess.run([sys.executable, "-m", "evalplus.evaluate", "--dataset", "humaneval", "--samples", str(target)],
                   check=False, capture_output=True, env=ENV)
    er = target.with_name(target.stem + "_eval_results.json")
    if not er.exists():
        cands = glob.glob(str(ROOT / dev / f"xdev_{model}_{rung}_{TAG}*eval_results.json")); er = Path(sorted(cands)[-1])
    ev = json.loads(er.read_text())["eval"]
    status = {t: ev[t][0]["plus_status"] == "pass" for t in ev}
    return {"solutions": sols, "pass": status, "n": len(sols)}


def main(argv):
    cells = [(argv[0], [argv[1]])] if len(argv) >= 2 else None
    models = sorted({p.name.split("_")[1] for d in DEVICES for p in (ROOT / d).glob(f"xdev_*_{TAG}.json")} ) if cells is None else [argv[0]]
    summary = {}; md = ["# Full-ladder cross-device replication (xdev-full, HumanEval+, n = 164, closed-book, greedy)", "",
                        "| Model | Rung | Device | pass@1 | Drop vs own F16 (pp) | Identical to Mac | Flips vs Mac (b: Mac pass, device fail; c: reverse) | McNemar p |",
                        "|---|---|---|---|---|---|---|---|"]
    for model in models:
        rungs = cells[0][1] if cells else RUNGS
        per = {d: {r: score(d, model, r) for r in rungs} for d in DEVICES}
        for r in rungs:
            ref = per["mac"].get(r)
            for d in DEVICES:
                s = per[d].get(r)
                if s is None: continue
                p1 = sum(s["pass"].values()) / len(ALL_TASKS)
                f16 = per[d].get("F16")
                drop = (sum(f16["pass"].values()) - sum(s["pass"].values())) / len(ALL_TASKS) * 100 if f16 else None
                if ref is not None and d != "mac":
                    ident = sum(1 for t in ALL_TASKS if s["solutions"].get(t) == ref["solutions"].get(t)) / len(ALL_TASKS)
                    b = sum(1 for t in ALL_TASKS if ref["pass"].get(t) and not s["pass"].get(t))
                    c = sum(1 for t in ALL_TASKS if not ref["pass"].get(t) and s["pass"].get(t))
                    pval = binom_two_sided(b, c); ident_s = f"{ident:.3f}"; flips = f"b = {b}, c = {c}"; p_s = f"{pval:.3f}"
                else:
                    ident_s = "reference" if d == "mac" else "no Mac file"; flips = ""; p_s = ""
                summary.setdefault(model, {}).setdefault(r, {})[d] = {"pass_at_1_plus": round(p1, 4), "drop_vs_own_f16_pp": None if drop is None else round(drop, 1),
                    "identity_vs_mac": None if d == "mac" or ref is None else round(ident, 3), "flips_vs_mac": None if d == "mac" or ref is None else {"b": b, "c": c, "mcnemar_p": round(pval, 4)}}
                md.append(f"| {model} | {r} | {d} | {p1:.3f} | {'' if drop is None else f'{drop:+.1f}'} | {ident_s} | {flips} | {p_s} |")
                print(md[-1])
    (ROOT / f"xdev_{TAG}_summary.json").write_text(json.dumps(summary, indent=2))
    (ROOT / f"xdev_{TAG}_summary.md").write_text("\n".join(md) + "\n")
    print(f"\nwrote results/xdev_{TAG}_summary.json and .md")


if __name__ == "__main__":
    main(sys.argv[1:])
