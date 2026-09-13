#!/usr/bin/env python3
"""E1-R Probe R1 — model-chosen retrieval under GBNF grammar constraint (e1r-protocol.md).

Two-stage, single-call structure, per problem, SAME quantised model for both stages:
  Stage 1: model emits ONE search_docs call — decoding constrained by e1/search_call.gbnf, so
           malformed syntax is impossible by construction. Stage-1 cap: 64 tokens.
  Stage 2: top-2 BM25 chunks for the model's OWN query (same frozen index, same runtime 13-gram
           contamination guard as the Condition-B artefact build) injected exactly as Condition B;
           the model answers under the study caps; scoring unchanged.

M1' (gate metric): stage-1 query is non-degenerate iff non-empty AND >=3 tokens AND not a verbatim
substring-repeat of the stage-1 instruction AND shares >=1 content token with the problem's
signature+docstring. M2': degeneration heuristics on stage-2 answers. M3: pass@1 (oracle in-process
for the K=20 gate; EvalPlus via score_with_evalplus for full-164 ladder cells, filenames *_r1 so
nothing clobbers A/B).

Usage: python e1/e1r_grammar.py [config] [rung] [K]   (model fixed: Qwen2.5-Coder-1.5B — protocol)
Gate: F16 K=20, pass iff M1' >= 50%."""
import json, re, sys, signal, copy
from pathlib import Path
import requests, yaml
from evalplus.data import get_human_eval_plus
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import run_pilot as H
from docs_index import DocsIndex, tok

cfg_path = sys.argv[1] if len(sys.argv) > 1 else "configs/mac.yaml"
rung     = sys.argv[2] if len(sys.argv) > 2 else "F16"
K        = int(sys.argv[3]) if len(sys.argv) > 3 else 20
MODEL_KEY = "qwen2.5-coder-1.5b-instruct"
S1_CAP = 64
S1_INSTRUCTION = ("Write ONE search query for the official Python documentation that would help "
                  "solve this problem. Respond with the search_docs call only.\n\n")
GRAMMAR = (Path(__file__).resolve().parent / "search_call.gbnf").read_text()
STOP = {"the","a","an","of","to","in","is","are","and","or","for","it","this","that","be","as",
        "if","with","on","by","not","return","returns","def","from","import"}

cfg = yaml.safe_load(Path(cfg_path).read_text())
model = next(m for m in cfg["models"] if m["name"] == MODEL_KEY)
quant = next(q for q in model["quants"] if q["label"] == rung)
problems = dict(list(get_human_eval_plus().items())[:K])
ix = DocsIndex()
P = get_human_eval_plus()
canon_13 = set().union(*[set(zip(*[re.findall(r"[a-z0-9]+", (P[t]["prompt"]+P[t]["canonical_solution"]).lower())[i:]
                                   for i in range(13)])) if len(re.findall(r"[a-z0-9]+", (P[t]["prompt"]+P[t]["canonical_solution"]).lower())) >= 13 else set()
                         for t in P])

def content_tokens(s):
    return {t for t in re.findall(r"[a-z0-9]+", s.lower()) if t not in STOP and len(t) > 1}

def m1_prime(query, prob_prompt):
    qs = re.findall(r"[a-z0-9]+", (query or "").lower())
    if not query or len(qs) < 3:
        return False, "empty or <3 tokens"
    if query.strip().lower() in S1_INSTRUCTION.lower():
        return False, "verbatim instruction repeat"
    if not (set(qs) & content_tokens(prob_prompt)):
        return False, "no content token from the problem"
    return True, "ok"

def guarded_top2(query):
    scores = ix.bm25.get_scores(tok(query))
    picked = []
    for i in sorted(range(len(ix.chunks)), key=lambda i: scores[i], reverse=True):
        if len(picked) == 2:
            break
        w = re.findall(r"[a-z0-9]+", " ".join(ix.chunks[i].lower().split()))
        g = set(zip(*[w[j:] for j in range(13)])) if len(w) >= 13 else set()
        if g & canon_13:
            continue                                    # runtime 13-gram guard (as artefact build)
        picked.append(i)
    return picked

def degenerate(text):
    if any(t in text for t in ("<|im_start|>", "<|endoftext|>")):
        return True
    return any(text.count(text[i:i+30]) >= 4 for i in range(0, max(0, len(text)-120), 30))

signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(TimeoutError()))
def oracle_score(code, task):
    e = P[task]; canon = e["prompt"] + e["canonical_solution"]; atol = e.get("atol") or 0
    def call(c, inp):
        ns = {}; exec(c, ns); return ns[e["entry_point"]](*copy.deepcopy(inp))
    try:
        for inp in [list(x) for x in e["base_input"]] + [list(x) for x in e["plus_input"]]:
            signal.alarm(8)
            exp, got = call(canon, inp), call(code, inp)
            signal.alarm(0)
            ok = abs(got-exp) <= atol if (atol and isinstance(got, (int, float))) else got == exp
            if not ok: return "fail"
        return "pass"
    except Exception:
        signal.alarm(0); return "fail"

print(f"[R1] {MODEL_KEY}:{rung} K={K} grammar={len(GRAMMAR)}B index={len(ix.chunks)}")
if H.port_in_use(cfg["host"], cfg["port"]):
    sys.exit("port busy")
srv = H.launch_server(cfg, model, quant)
H.wait_ready(cfg, srv)
url = f"http://{cfg['host']}:{cfg['port']}/v1/chat/completions"

rows, samples = [], []
try:
    for n, (task_id, p) in enumerate(problems.items(), 1):
        r1 = requests.post(url, json={"model": rung, "temperature": 0, "seed": 0, "max_tokens": S1_CAP,
                                      "grammar": GRAMMAR,
                                      "messages": [{"role": "user",
                                                    "content": S1_INSTRUCTION + p["prompt"]}]}, timeout=300).json()
        s1 = r1["choices"][0]["message"]["content"] or ""
        try:
            query = json.loads(s1)["arguments"]["query"]
        except Exception:
            query = None                                  # cap-truncated call (grammar prefix only)
        ok1, note = m1_prime(query, p["prompt"])
        picked = guarded_top2(query) if ok1 else []
        if picked:
            content = f"{ix.chunks[picked[0]]}\n\n{ix.chunks[picked[1]]}\n\n" + H.INSTRUCTION.format(prompt=p["prompt"])
        else:                                             # degenerate query -> closed-book fallback, recorded
            content = H.INSTRUCTION.format(prompt=p["prompt"])
        r2 = requests.post(url, json={"model": rung, "temperature": 0, "seed": 0,
                                      "max_tokens": cfg["max_tokens"],
                                      "messages": [{"role": "user", "content": content}]}, timeout=600).json()
        ans = r2["choices"][0]["message"]["content"] or ""
        code = H.extract_code(ans, p["entry_point"])
        rows.append({"task_id": task_id, "query": query, "m1p": ok1, "m1p_note": note,
                     "chunk_src": [ix.src[i] for i in picked], "m2p_degen": degenerate(ans),
                     "gate_pass": oracle_score(code, task_id) if K <= 30 else None})
        samples.append({"task_id": task_id, "solution": code})
        print(f"  [{n}/{K}] {task_id} M1'={'ok' if ok1 else 'DEGEN('+note+')'} "
              f"q={repr((query or '')[:60])} {rows[-1]['gate_pass'] or ''}")
finally:
    H.stop_server(srv)

out = H.RESULTS_ROOT / "mac" / f"r1_{rung}"
out.mkdir(parents=True, exist_ok=True)
(out / "stage1.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
m1p = sum(r["m1p"] for r in rows) / len(rows)
summary = {"probe": "R1", "model": MODEL_KEY, "rung": rung, "K": K,
           "m1_prime_rate": round(m1p, 3),
           "m2_prime_degen": sum(r["m2p_degen"] for r in rows),
           "gate": ("PASS" if m1p >= 0.5 else "FAIL") if (rung == "F16" and K == 20) else None,
           "oracle_pass": (round(sum(r["gate_pass"] == "pass" for r in rows) / len(rows), 3)
                           if rows[0]["gate_pass"] is not None else None)}
(out / "summary.json").write_text(json.dumps(summary, indent=2))
if K == 164:                                             # ladder cell -> EvalPlus like A/B
    sp = H.RESULTS_ROOT / "mac" / f"samples_{MODEL_KEY}_{rung}_r1.jsonl"
    sp.write_text("".join(json.dumps(s) + "\n" for s in samples))
    base, plus = H.score_with_evalplus(sp)
    summary["pass@1_base"], summary["pass@1_plus"] = base, plus
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
