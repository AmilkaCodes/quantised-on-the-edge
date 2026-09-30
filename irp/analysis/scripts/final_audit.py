"""Final pre-formative audit: recompute every quality-axis number the chapters, spine and
data-pack rely on, from the committed per-problem snapshots; flag any mismatch > 0.004."""
import json, os
ROOT = r"C:\Users\Amilka\OneDrive\University_of_York\Modules\10. Research Proposal in Computer Science"
ER = os.path.join(ROOT, "proposal-dev", "pilot", "eval-results", "mac")
Q = ["F16", "Q8_0", "Q4_K_M", "Q3_K_M", "Q2_K"]

def p1(model, rung, suffix=""):
    f = os.path.join(ER, f"samples_{model}_{rung}{suffix}-sanitized_eval_results.json")
    if not os.path.exists(f): return None
    d = json.load(open(f, encoding="utf-8"))["eval"]
    return sum(d[t][0]["plus_status"] == "pass" for t in d) / len(d), len(d)

QW, PH, B7 = "qwen2.5-coder-1.5b-instruct", "phi-3-mini-4k-instruct", "qwen2.5-coder-7b-instruct"
# expected values as quoted in spine / data-pack / chapters (plus-status)
EXP = {
 ("HE+", QW): [.610,.616,.616,.585,.384], ("HE+", PH): [.646,.628,.549,.427,.220],
 ("HE+", B7): [.841,.848,.854,.835,.793],
 ("HE+", QW+"-imat"): [None,None,.616,.628,.530], ("HE+", PH+"-imat"): [None,None,.628,.628,.360],
 ("MBPP+", QW): [.638,.627,.630,.571,.423], ("MBPP+", PH): [.661,.664,.640,.474,.262],
 ("MBPP+", B7): [.735,None,None,None,.646], ("MBPP+", QW+"-imat"): [None,None,.630,.595,.479],
}
bad = 0; checked = 0
for (bench, model), exp in EXP.items():
    suf = "_mbpp" if bench == "MBPP+" else ""
    for r, e in zip(Q, exp):
        if e is None: continue
        got = p1(model, r, suf)
        if got is None: print(f"MISSING {bench} {model} {r}"); bad += 1; continue
        v, n = got; checked += 1
        flag = "" if abs(v - e) <= 0.004 else "  <<< MISMATCH"
        if flag: bad += 1
        print(f"{bench:5s} {model:34s} {r:7s} n={n} expected={e:.3f} recomputed={v:.3f}{flag}")
# derived deltas quoted in the spine
d = lambda b, m, i, j: p1(m, Q[j], "_mbpp" if b=="MBPP+" else "")[0] - p1(m, Q[i], "_mbpp" if b=="MBPP+" else "")[0]
print("\nDerived deltas (spine quotes):")
print(f"HE+  Qwen Q2-F16   = {d('HE+',QW,0,4):+.3f}  (quoted -0.226)")
print(f"HE+  Phi  Q2-F16   = {d('HE+',PH,0,4):+.3f}  (quoted -0.427)")
print(f"HE+  Phi  Q4-F16   = {d('HE+',PH,0,2):+.3f}  (quoted -0.098)")
print(f"HE+  7B   Q2-F16   = {d('HE+',B7,0,4):+.3f}  (quoted -0.049)")
print(f"MBPP Qwen Q2-F16   = {d('MBPP+',QW,0,4):+.3f}  (quoted -0.214)")
print(f"MBPP Qwen Q3-F16   = {d('MBPP+',QW,0,3):+.3f}  (quoted -0.066)")
print(f"MBPP Phi  Q3-F16   = {d('MBPP+',PH,0,3):+.3f}  (quoted -0.188)")
print(f"MBPP Phi  Q2-F16   = {d('MBPP+',PH,0,4):+.3f}  (quoted -0.399)")
print(f"MBPP 7B   Q2-F16   = {d('MBPP+',B7,0,4):+.3f}  (quoted -0.089)")
mm_he = p1(B7,"Q2_K")[0] - p1(QW,"F16")[0]; mm_mb = p1(B7,"Q2_K","_mbpp")[0] - p1(QW,"F16","_mbpp")[0]
print(f"memory-matched HE+ = {mm_he:+.3f} (quoted +0.183); MBPP+ = {mm_mb:+.3f} (quoted +0.008)")
im = p1(QW+"-imat","Q2_K","_mbpp")[0] - p1(QW,"Q2_K","_mbpp")[0]
print(f"MBPP imat rescue Q2 = {im:+.3f} (quoted +0.056); recovered fraction = {im/abs(d('MBPP+',QW,0,4)):.0%} (quoted 26%)")
print(f"\nCELLS CHECKED: {checked}; PROBLEMS: {bad}")
