#!/usr/bin/env python3
"""Direct in-process scorer for the cross-device spot-check. EvalPlus's parallel exec sandbox is
unreliable in this environment (Bitdefender throttles the many short-lived exec subprocesses ->
mass spurious timeouts), so instead we score each solution IN-PROCESS against the canonical oracle:
run the model's function and EvalPlus's canonical_solution on every base_input + plus_input and
compare outputs (atol-aware), with a per-call alarm timeout. Reliable and self-consistent (identical
solutions necessarily get identical scores). Companion to cross-device-check.md / D25."""
import json, signal, copy
from evalplus.data import get_human_eval_plus

# xdev-lowrung addendum (2026-09-18): parameterised (mechanical; defaults unchanged) —
#   score_xdev_direct.py [MODEL] [RUNG] [DEV1,DEV2,...]
import sys as _sys
MODEL = _sys.argv[1] if len(_sys.argv) > 1 else "qwen2.5-coder-1.5b-instruct"
RUNG = _sys.argv[2] if len(_sys.argv) > 2 else "Q4_K_M"
DEVICES = _sys.argv[3].split(",") if len(_sys.argv) > 3 else ["mac", "jetson", "pi5"]
P = get_human_eval_plus()
sols = {d: json.load(open(f"results/{d}/xdev_{MODEL}_{RUNG}.json")) for d in DEVICES}
shared = sorted(set.intersection(*[set(sols[d]) for d in DEVICES]), key=lambda t: int(t.split("/")[1]))

class TO(Exception): pass
signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(TO()))

def call(code, entry, inp):
    ns = {}
    exec(code, ns)
    return ns[entry](*copy.deepcopy(inp))

def eq(a, b, atol):
    try:
        if atol and isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return abs(a - b) <= atol
        return a == b
    except Exception:
        return False

def score(code, task):
    e = P[task]; entry = e["entry_point"]; atol = e.get("atol") or 0
    canon = e["prompt"] + e["canonical_solution"]
    inputs = [list(x) for x in e["base_input"]] + [list(x) for x in e["plus_input"]]
    try:
        for inp in inputs:
            signal.alarm(8)
            exp = call(canon, entry, inp)
            got = call(code, entry, inp)
            signal.alarm(0)
            if not eq(got, exp, atol):
                return "fail"
        return "pass"
    except Exception:
        signal.alarm(0)
        return "fail"

status = {d: {t: score(sols[d][t], t) for t in shared} for d in DEVICES}
K = len(shared)
print(f"==== {MODEL}:{RUNG} | K={K} shared | in-process canonical oracle (base+plus inputs) ====")
for d in DEVICES:
    p = sum(v == "pass" for v in status[d].values()) / K
    print(f"  {d:7s} pass@1 = {p:.3f}  ({sum(v=='pass' for v in status[d].values())}/{K})")

ident = [t for t in shared if len({sols[d][t] for d in DEVICES}) == 1]
div   = [t for t in shared if len({sols[d][t] for d in DEVICES}) > 1]
print(f"\noutput identical across tiers: {len(ident)}/{K} ({len(ident)/K:.0%})")
print(f"output differs on >=1 tier   : {len(div)}/{K} ({len(div)/K:.0%})")
# noise gate: identical-solution problems MUST score identically
bad = [t for t in ident if len({status[d][t] for d in DEVICES}) > 1]
print(f"noise gate (identical-solution problems scoring differently): {len(bad)}  {'OK' if not bad else bad}")
flips = [(t, {d: status[d][t] for d in DEVICES}) for t in div if len({status[d][t] for d in DEVICES}) > 1]
print(f"correctness FLIPS among divergent problems: {len(flips)}/{len(div)}")
for t, fl in flips:
    print(f"   {t}: {fl}")
