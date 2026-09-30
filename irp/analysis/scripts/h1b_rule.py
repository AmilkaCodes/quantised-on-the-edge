"""H1b decision rule (Ch3 s3.5, seventh pass): between-model difference of per-problem drop
indicators on the shared problem set, paired percentile bootstrap (B=10,000, seed 0), tested
only at rungs where the two models' descriptive (point) margin verdicts differ; Holm over
those rungs. Drop indicator per problem = F16 pass - rung pass in {-1,0,1}; model difference
= Phi drop - Qwen drop (positive => Phi loses more at that rung)."""
import json, os, random
ROOT = r"C:\Users\Amilka\OneDrive\University_of_York\Modules\10. Research Proposal in Computer Science"
ER = os.path.join(ROOT, "proposal-dev", "pilot", "eval-results", "mac")
Q = ["Q8_0", "Q4_K_M", "Q3_K_M", "Q2_K"]
QW, PH = "qwen2.5-coder-1.5b-instruct", "phi-3-mini-4k-instruct"

def status(model, rung, suffix=""):
    f = os.path.join(ER, f"samples_{model}_{rung}{suffix}-sanitized_eval_results.json")
    d = json.load(open(f, encoding="utf-8"))["eval"]
    return {t: int(d[t][0]["plus_status"] == "pass") for t in d}

def run(bench, suffix):
    print(f"\n== {bench} ==")
    bq, bp = status(QW, "F16", suffix), status(PH, "F16", suffix)
    tasks = sorted(bq); n = len(tasks)
    rows = []
    for r in Q:
        sq, sp = status(QW, r, suffix), status(PH, r, suffix)
        dq = [bq[t] - sq[t] for t in tasks]; dp = [bp[t] - sp[t] for t in tasks]
        drop_q, drop_p = sum(dq) / n, sum(dp) / n
        vq = "beyond" if drop_q > 0.05 else "within"; vp = "beyond" if drop_p > 0.05 else "within"
        diff = [p - q for p, q in zip(dp, dq)]
        est = sum(diff) / n
        rng = random.Random(0); B = 10000; boots = []
        for _ in range(B):
            s = 0
            for _ in range(n): s += diff[rng.randrange(n)]
            boots.append(s / n)
        boots.sort()
        lo, hi = boots[int(0.025 * B)], boots[int(0.975 * B) - 1]
        p_le = sum(b <= 0 for b in boots) / B; p_ge = sum(b >= 0 for b in boots) / B
        p = min(1.0, 2 * min(p_le, p_ge))
        tested = vq != vp
        rows.append((r, drop_q, vq, drop_p, vp, est, lo, hi, p, tested))
    tested = [x for x in rows if x[-1]]
    # Holm over ALL FOUR rungs (m = 4); interpreted only at rungs whose descriptive verdicts differ
    holm = {}
    order = sorted(rows, key=lambda x: x[8]); m = len(order); prev = 0
    for i, x in enumerate(order):
        adj = min(1.0, max(prev, (m - i) * x[8])); prev = adj; holm[x[0]] = adj
    for r, dq_, vq, dp_, vp, est, lo, hi, p, t in rows:
        h = f"Holm(m=4) p={holm[r]:.4f}" + ("  <- ELIGIBLE (verdicts differ)" if t else "  (verdicts agree: not interpreted)")
        print(f"{r:7s} Qwen drop {dq_*100:+5.1f}pp ({vq:6s}) | Phi drop {dp_*100:+5.1f}pp ({vp:6s}) | "
              f"Phi-Qwen diff {est*100:+5.1f}pp [{lo*100:+5.1f},{hi*100:+5.1f}] p={p:.4f} | {h}")
    if not tested:
        print("H1b: no rung with differing descriptive verdicts -> NOT DISTINGUISHABLE at this resolution")
    else:
        rej = [r for r in holm if holm[r] < 0.05 and any(x[0] == r and x[-1] for x in rows)]
        print("H1b: H0b REJECTED at rung(s) " + ", ".join(rej) if rej else "H1b: H0b NOT rejected")

run("HumanEval+", ""); run("MBPP+", "_mbpp")
