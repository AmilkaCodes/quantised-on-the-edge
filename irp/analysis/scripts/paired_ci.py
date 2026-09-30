"""Exact-conditional and score (Tango-type) 95% intervals for the paired drop in pass@1
(F16 minus rung), from the committed per-problem snapshots. Companion to the percentile
bootstrap already reported. drop = (b - c)/n with b = F16 pass & rung fail, c = rung pass &
F16 fail."""
import json, os, math
ROOT = r"C:\Users\Amilka\OneDrive\University_of_York\Modules\10. Research Proposal in Computer Science"
ER = os.path.join(ROOT, "proposal-dev", "pilot", "eval-results", "mac")
Q = ["Q8_0", "Q4_K_M", "Q3_K_M", "Q2_K"]
QW, PH = "qwen2.5-coder-1.5b-instruct", "phi-3-mini-4k-instruct"

def status(model, rung, suffix=""):
    f = os.path.join(ER, f"samples_{model}_{rung}{suffix}-sanitized_eval_results.json")
    d = json.load(open(f, encoding="utf-8"))["eval"]
    return {t: d[t][0]["plus_status"] == "pass" for t in d}

# ---- exact conditional interval: c | (b+c)=m ~ Bin(m, pi); drop = (m - 2c)/n = m(1-2pi)/n
def beta_inv(p, a, b):
    # inverse regularised incomplete beta by bisection on the CDF (a,b > 0)
    from math import lgamma, exp, log
    def betacf(x, a, b):
        MAXIT, EPS, FPMIN = 400, 3e-14, 1e-300
        qab, qap, qam = a + b, a + 1, a - 1
        c, d = 1.0, 1 - qab * x / qap
        d = 1 / (d if abs(d) > FPMIN else FPMIN); h = d
        for m in range(1, MAXIT + 1):
            m2 = 2 * m
            aa = m * (b - m) * x / ((qam + m2) * (a + m2))
            d = 1 + aa * d; d = 1 / (d if abs(d) > FPMIN else FPMIN)
            c = 1 + aa / c; c = c if abs(c) > FPMIN else FPMIN
            h *= d * c
            aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
            d = 1 + aa * d; d = 1 / (d if abs(d) > FPMIN else FPMIN)
            c = 1 + aa / c; c = c if abs(c) > FPMIN else FPMIN
            de = d * c; h *= de
            if abs(de - 1) < EPS: break
        return h
    def ibeta(x, a, b):
        if x <= 0: return 0.0
        if x >= 1: return 1.0
        bt = exp(lgamma(a + b) - lgamma(a) - lgamma(b) + a * log(x) + b * log(1 - x))
        if x < (a + 1) / (a + b + 2): return bt * betacf(x, a, b) / a
        return 1 - bt * betacf(1 - x, b, a) / b
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if ibeta(mid, a, b) < p: lo = mid
        else: hi = mid
    return (lo + hi) / 2

def clopper_pearson(c, m, alpha=0.05):
    lo = 0.0 if c == 0 else beta_inv(alpha / 2, c, m - c + 1)
    hi = 1.0 if c == m else beta_inv(1 - alpha / 2, c + 1, m - c)
    return lo, hi

def exact_conditional(b, c, n):
    m = b + c
    if m == 0: return 0.0, 0.0
    plo, phi = clopper_pearson(c, m)          # pi = P(rung pass | discordant)
    return m * (1 - 2 * phi) / n, m * (1 - 2 * plo) / n   # drop = m(1-2pi)/n, decreasing in pi

# ---- score interval: invert Z(delta) = (b - c - n*delta)/sqrt(n(2*p21 + delta - delta^2)),
# with p21 (prob of the c-type discordant cell) at its restricted MLE for that delta.
def restricted_p21(b, c, n, delta):
    # maximise b*log(p21+delta) + c*log(p21) + (n-b-c)*log(1-2*p21-delta) over feasible p21
    lo = max(0.0, -delta) + 1e-12; hi = (1 - delta) / 2 - 1e-12
    if hi <= lo: return max(lo, 0.0)
    def ll(p):
        t = [(b, p + delta), (c, p), (n - b - c, 1 - 2 * p - delta)]
        return sum(k * math.log(v) for k, v in t if k > 0) if all(v > 0 for k, v in t if k > 0) else -1e300
    g = (math.sqrt(5) - 1) / 2
    x1, x2 = hi - g * (hi - lo), lo + g * (hi - lo)
    f1, f2 = ll(x1), ll(x2)
    for _ in range(300):
        if f1 < f2: lo, x1, f1 = x1, x2, f2; x2 = lo + g * (hi - lo); f2 = ll(x2)
        else: hi, x2, f2 = x2, x1, f1; x1 = hi - g * (hi - lo); f1 = ll(x1)
    return (lo + hi) / 2

def score_z(b, c, n, delta):
    p21 = restricted_p21(b, c, n, delta)
    var = n * (2 * p21 + delta - delta * delta)
    if var <= 0: return float("inf") if (b - c - n * delta) > 0 else float("-inf")
    return (b - c - n * delta) / math.sqrt(var)

def score_ci(b, c, n, z=1.959964):
    est = (b - c) / n
    def solve(target, lo, hi):
        for _ in range(200):
            mid = (lo + hi) / 2
            if score_z(b, c, n, mid) > target: lo = mid
            else: hi = mid
        return (lo + hi) / 2
    return solve(z, -0.999, est), solve(-z, est, 0.999)

def run(bench, suffix):
    print(f"\n== {bench} (drop = F16 - rung, positive = degradation; margin 5pp) ==")
    for model, name in ((QW, "Qwen-1.5B"), (PH, "Phi-3")):
        base = status(model, "F16", suffix); n = len(base)
        for r in Q:
            s = status(model, r, suffix)
            b = sum(base[t] and not s[t] for t in base); c = sum(s[t] and not base[t] for t in base)
            est = (b - c) / n
            elo, ehi = exact_conditional(b, c, n); slo, shi = score_ci(b, c, n)
            def verdict(lo, hi):
                if lo > 0.05: return "beyond margin"
                if hi < 0.05: return "within margin"
                return "straddles (inconclusive)"
            print(f"{name:10s} {r:7s} n={n} b={b:3d} c={c:3d} drop={est*100:+5.1f}pp | "
                  f"exact-cond [{elo*100:+5.1f},{ehi*100:+5.1f}] {verdict(elo,ehi):26s} | "
                  f"score [{slo*100:+5.1f},{shi*100:+5.1f}] {verdict(slo,shi)}")

run("HumanEval+", ""); run("MBPP+", "_mbpp")
