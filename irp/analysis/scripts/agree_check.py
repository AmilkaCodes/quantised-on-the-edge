"""Agreement of bootstrap (primary, registered) vs exact-conditional (check) intervals under
the interval-only three-class rule (within / collapsed / inconclusive), all 16 confirmatory
cells. Run from this folder (imports paired_ci.py). Recorded result 2026-09-21: 15/16 agree;
MBPP+ Phi Q4_K_M disagrees (bootstrap upper exactly +5.0, exact +4.9) and resolves to
inconclusive under Ch3 s3.5's primary-interval rule (data pack item 13)."""
import random, io, contextlib, importlib.util, os
here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("pc", os.path.join(here, "paired_ci.py"))
pc = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):
    spec.loader.exec_module(pc)

def cls(lo, hi):
    if hi < 0.05: return "within"
    if lo > 0.05: return "collapsed"
    return "inconclusive"

disagree = 0
for bench, suf in (("HE+", ""), ("MBPP+", "_mbpp")):
    for model, name in ((pc.QW, "Qwen"), (pc.PH, "Phi")):
        base = pc.status(model, "F16", suf); tasks = sorted(base); n = len(tasks)
        for r in pc.Q:
            s = pc.status(model, r, suf)
            d = [int(base[t]) - int(s[t]) for t in tasks]
            b = sum(x == 1 for x in d); c = sum(x == -1 for x in d)
            rng = random.Random(0); B = 10000; boots = []
            for _ in range(B):
                boots.append(sum(d[rng.randrange(n)] for _ in range(n)) / n)
            boots.sort(); blo, bhi = boots[int(0.025 * B)], boots[int(0.975 * B) - 1]
            elo, ehi = pc.exact_conditional(b, c, n)
            cb, ce = cls(blo, bhi), cls(elo, ehi)
            flag = "" if cb == ce else "  <<< DISAGREE"
            if flag: disagree += 1
            print(f"{bench:5s} {name:4s} {r:7s} boot [{blo*100:+5.1f},{bhi*100:+5.1f}] {cb:12s} | "
                  f"exact [{elo*100:+5.1f},{ehi*100:+5.1f}] {ce:12s}{flag}")
print("DISAGREEMENTS:", disagree)
