"""Post-hoc bootstrap (reviewer pass 14, 2026-11-14): does the drop differ between benchmarks
at each model's boundary rung? For each model, resample HumanEval+ (n=164) and MBPP+ (n=378)
per-problem paired outcomes independently (10,000 resamples, fixed seed) and give a percentile
CI on (MBPP+ drop - HumanEval+ drop). POST-HOC: no benchmark-by-rung test was registered.
Also prints base-HumanEval (not plus) F16 pass@1 for the technical-report comparison."""
import json, os, random
ROOT = r"C:\Users\Amilka\OneDrive\University_of_York\Modules\10. Research Proposal in Computer Science"
ER = os.path.join(ROOT, "proposal-dev", "pilot", "eval-results", "mac")
QW, PH = "qwen2.5-coder-1.5b-instruct", "phi-3-mini-4k-instruct"

def status(model, rung, suffix="", key="plus_status"):
    f = os.path.join(ER, f"samples_{model}_{rung}{suffix}-sanitized_eval_results.json")
    d = json.load(open(f, encoding="utf-8"))["eval"]
    return {t: d[t][0][key] == "pass" for t in d}

def paired_diffs(model, rung, suffix):
    base = status(model, "F16", suffix); quant = status(model, rung, suffix)
    assert set(base) == set(quant)
    return [int(base[t]) - int(quant[t]) for t in sorted(base)]  # +1 = lost at rung, -1 = gained

def boot(model, rung, B=10000, seed=0):
    he = paired_diffs(model, rung, "")
    mb = paired_diffs(model, rung, "_mbpp")
    d_he = sum(he) / len(he); d_mb = sum(mb) / len(mb)
    point = d_mb - d_he
    rng = random.Random(seed); diffs = []
    for _ in range(B):
        rhe = sum(rng.choice(he) for _ in he) / len(he)
        rmb = sum(rng.choice(mb) for _ in mb) / len(mb)
        diffs.append(rmb - rhe)
    diffs.sort()
    lo, hi = diffs[int(0.025 * B)], diffs[int(0.975 * B) - 1]
    print(f"{model} {rung}: HE+ drop {d_he*100:+.1f} pp (n={len(he)}), MBPP+ drop {d_mb*100:+.1f} pp (n={len(mb)})")
    print(f"  difference (MBPP+ - HE+) = {point*100:+.1f} pp, 95% percentile CI [{lo*100:+.1f}, {hi*100:+.1f}]")

print("Boundary rungs, naive ladder, MacBook snapshots:")
boot(QW, "Q3_K_M")
boot(PH, "Q4_K_M")
print("\nBase-HumanEval (original tests, not plus) F16 pass@1, for the report comparison:")
for m in (QW, PH):
    s = status(m, "F16", "", key="base_status")
    print(f"  {m}: {sum(s.values())/len(s):.3f} (n={len(s)})")
