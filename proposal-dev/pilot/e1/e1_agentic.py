#!/usr/bin/env python3
"""E1 Condition D — agentic tool-use probe (protocol §5; RQ1c, exploratory, GATED).

One tool: search_docs(query) -> top-2 chunks from the SAME frozen BM25 index as Condition B
(docs_index.py; in-process, no network). Loop: OpenAI-style chat tool-calling against llama-server
b9951 launched with --jinja (the model's own chat template renders the tool schema); greedy, seed 0;
max 4 assistant turns, then a forced final answer (tools withdrawn).

Per-episode records (transcripts.jsonl = the raw data):
  M1  first assistant turn contains a syntactically valid, schema-correct search_docs call
      (structured tool_calls entry; name == search_docs; arguments parse to {"query": <non-empty str>})
  M2  loop outcome: completed | max_turns_loop | malformed_abandonment | hallucinated_tool_output
      | degeneration  (heuristic labels; transcripts kept for manual re-classification)
  M3  pass@1 (in-process canonical oracle, base+plus inputs) conditional on a well-formed tool phase

GATE (runs first): Qwen F16, first 20 problems — pass iff M1 >= 50%. Fail -> probe stops, the floor
is the finding. Usage:  python e1/e1_agentic.py [config] [model_key] [rung] [K]
"""
import json, re, sys, signal, copy, subprocess, time
from pathlib import Path
from openai import OpenAI
from evalplus.data import get_human_eval_plus
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import run_pilot as H          # cfg conventions, port guard, wait_ready, stop_server, extract_code
from docs_index import DocsIndex
import yaml

cfg_path  = sys.argv[1] if len(sys.argv) > 1 else "configs/mac.yaml"
model_key = sys.argv[2] if len(sys.argv) > 2 else "qwen2.5-coder-1.5b-instruct"
rung      = sys.argv[3] if len(sys.argv) > 3 else "F16"
K         = int(sys.argv[4]) if len(sys.argv) > 4 else 20
MECH      = sys.argv[5] if len(sys.argv) > 5 else "native"   # E2a 4b: 'json' = IFFC-style prompted-JSON
MAX_TURNS = 4

TOOLS = [{"type": "function", "function": {
    "name": "search_docs",
    "description": "Search the official Python documentation. Returns the two most relevant sections.",
    "parameters": {"type": "object",
                   "properties": {"query": {"type": "string", "description": "search query"}},
                   "required": ["query"]}}}]
PREAMBLE = ("You have a tool `search_docs(query)` that searches the official Python documentation. "
            "First call search_docs with a useful query for this problem, then write your final "
            "solution.\n\n")
# E2a Arm 4b — prompted-JSON (IFFC-style) framing: no tools API; the call is a bare JSON object in text.
PREAMBLE_JSON = (
    "You can search the official Python documentation. To search, reply with EXACTLY one JSON object "
    'and nothing else: {"name": "search_docs", "arguments": {"query": "<your search query>"}}\n'
    "I will reply with the search results; then write your final solution. "
    "First search, then solve.\n\n")

def find_json_call(text: str):
    """First balanced JSON object in text that parses to a dict with a 'name' key — the prompted-JSON
    call parser (E2a protocol §1 4b)."""
    for i, ch in enumerate(text):
        if ch != "{":
            continue
        depth = 0
        for j in range(i, min(len(text), i + 2000)):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        obj = json.loads(text[i:j + 1])
                        if isinstance(obj, dict) and "name" in obj:
                            return obj
                    except Exception:
                        pass
                    break
    return None

cfg = yaml.safe_load(Path(cfg_path).read_text())
model = next(m for m in cfg["models"] if m["name"] == model_key)
quant = next(q for q in model["quants"] if q["label"] == rung)
problems = dict(list(get_human_eval_plus().items())[:K])
ix = DocsIndex()
print(f"[{cfg.get('device')}] Condition D  {model_key}:{rung}  K={K}  mech={MECH}  index={len(ix.chunks)} chunks")

# --- server with --jinja (chat-template tool-calling as supported at b9951) ---
gguf = Path(model["gguf_dir"]) / quant["file"]
if H.port_in_use(cfg["host"], cfg["port"]):
    sys.exit(f"port {cfg['port']} busy — kill the stale server first")
cmd = [cfg["server_bin"], "-m", str(gguf), "-c", str(cfg["n_ctx"]), "-ngl", str(model["ngl"]),
       "--host", cfg["host"], "--port", str(cfg["port"]), "--seed", str(cfg["seed"]), "--jinja"]
print("    launching:", " ".join(cmd))
srv = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
H.wait_ready(cfg, srv)
client = OpenAI(base_url=f"http://{cfg['host']}:{cfg['port']}/v1", api_key="sk-noauth")

signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(TimeoutError()))
P = get_human_eval_plus()
def oracle(code, task):
    e = P[task]; canon = e["prompt"] + e["canonical_solution"]; atol = e.get("atol") or 0
    def call(c, inp):
        ns = {}; exec(c, ns); return ns[e["entry_point"]](*copy.deepcopy(inp))
    try:
        for inp in [list(x) for x in e["base_input"]] + [list(x) for x in e["plus_input"]]:
            signal.alarm(8)
            exp, got = call(canon, inp), call(code, inp)
            signal.alarm(0)
            ok = abs(got - exp) <= atol if (atol and isinstance(got, (int, float))) else got == exp
            if not ok: return "fail"
        return "pass"
    except Exception:
        signal.alarm(0); return "fail"

def degenerate(text: str) -> bool:
    if any(t in text for t in ("<|im_start|>", "<|endoftext|>", "<|assistant|>")):
        return True
    for i in range(0, max(0, len(text) - 120), 30):
        if text.count(text[i:i + 30]) >= 4:
            return True
    return False

def valid_call(tc) -> tuple[bool, str]:
    try:
        if tc.function.name != "search_docs":
            return False, f"wrong tool: {tc.function.name}"
        args = json.loads(tc.function.arguments)
        q = args.get("query")
        return (isinstance(q, str) and q.strip() != ""), "ok" if q else "empty/missing query"
    except Exception as e:
        return False, f"unparseable arguments: {e}"

episodes = []
try:
    for n, (task_id, p) in enumerate(problems.items(), 1):
        pre = PREAMBLE_JSON if MECH == "json" else PREAMBLE
        msgs = [{"role": "user", "content": pre + H.INSTRUCTION.format(prompt=p["prompt"])}]
        turns, first_attempted, first_valid, first_note = [], False, False, ""
        outcome, final_text = None, ""
        for turn in range(MAX_TURNS):
            if MECH == "json":
                kw = {}
            elif MECH == "forced" and turn == 0:
                # E2a deviation 2026-09-13: coercion cell — the FIRST turn requires a tool call
                # (measures format capability, "can"); later turns are unforced so the episode
                # can complete naturally and M3 stays meaningful.
                kw = {"tools": TOOLS, "tool_choice": "required"}
            else:
                kw = {"tools": TOOLS}
            m = client.chat.completions.create(model=rung, messages=msgs,
                                               temperature=cfg["temperature"], seed=cfg["seed"],
                                               max_tokens=cfg["max_tokens"], **kw).choices[0].message
            content = m.content or ""
            if MECH == "json":
                call = find_json_call(content)
                ok = bool(call and call.get("name") == "search_docs"
                          and isinstance(call.get("arguments"), dict)
                          and isinstance(call["arguments"].get("query"), str)
                          and call["arguments"]["query"].strip())
                turns.append({"turn": turn, "content": content, "tool_calls": [call] if call else []})
                if turn == 0:
                    first_attempted = call is not None or "search_docs" in content
                    first_valid = ok
                    first_note = ("ok" if ok else
                                  "JSON object present but not a valid search_docs call" if call else
                                  "mention without parseable JSON" if first_attempted else "")
                if ok:
                    result = ix.search_docs(call["arguments"]["query"])
                    msgs.append({"role": "assistant", "content": content})
                    msgs.append({"role": "user", "content": "Search results:\n" + json.dumps(result)
                                 + "\n\nNow write your final solution."})
                    continue
                final_text = content
                outcome = "completed"
                break
            tcs = list(m.tool_calls or [])
            turns.append({"turn": turn, "content": content,
                          "tool_calls": [{"name": t.function.name, "arguments": t.function.arguments}
                                         for t in tcs]})
            if turn == 0:
                first_attempted = bool(tcs) or ("search_docs" in content or "<tool_call>" in content)
                if tcs:
                    first_valid, first_note = valid_call(tcs[0])
                elif first_attempted:
                    first_note = "pseudo-call in plain text (no structured tool_calls)"
            if tcs:
                ok, note = valid_call(tcs[0])
                msgs.append({"role": "assistant", "content": content or None, "tool_calls": [
                    {"id": tcs[0].id, "type": "function",
                     "function": {"name": tcs[0].function.name, "arguments": tcs[0].function.arguments}}]})
                if ok:
                    q = json.loads(tcs[0].function.arguments)["query"]
                    result = ix.search_docs(q)
                    msgs.append({"role": "tool", "tool_call_id": tcs[0].id,
                                 "content": json.dumps(result)})
                else:
                    msgs.append({"role": "tool", "tool_call_id": tcs[0].id,
                                 "content": json.dumps({"error": f"invalid call: {note}"})})
                continue
            final_text = content
            outcome = "completed"
            break
        if outcome is None:   # exhausted turns still tool-calling -> forced final, tools withdrawn
            msgs.append({"role": "user", "content": "Provide your final solution now as a Python code block."})
            m = client.chat.completions.create(model=rung, messages=msgs,
                                               temperature=cfg["temperature"], seed=cfg["seed"],
                                               max_tokens=cfg["max_tokens"]).choices[0].message
            final_text = m.content or ""
            outcome = "max_turns_loop"
        if "<tool_response>" in final_text:
            outcome = "hallucinated_tool_output"
        elif degenerate(final_text):
            outcome = "degeneration"
        elif outcome == "completed" and first_attempted and not first_valid:
            outcome = "malformed_abandonment"
        code = H.extract_code(final_text, p["entry_point"])
        res = oracle(code, task_id)
        episodes.append({"task_id": task_id, "m1_attempted": first_attempted, "m1_valid": first_valid,
                         "m1_note": first_note, "m2_outcome": outcome, "n_turns": len(turns),
                         "pass": res, "turns": turns, "final": final_text})
        print(f"  [{n}/{K}] {task_id}  M1={'valid' if first_valid else ('attempt' if first_attempted else 'none')}"
              f"  M2={outcome}  turns={len(turns)}  {res}")
finally:
    H.stop_server(srv)

out = H.RESULTS_ROOT / str(cfg.get("device")) / (f"agentic_{model_key}_{rung}"
                                                 + ("" if MECH == "native" else f"_{MECH}")
                                                 + ("" if cfg["max_tokens"] == 768 else f"_cap{cfg['max_tokens']}"))
out.mkdir(parents=True, exist_ok=True)
(out / "transcripts.jsonl").write_text("".join(json.dumps(e) + "\n" for e in episodes))
m1 = sum(e["m1_valid"] for e in episodes) / len(episodes)
from collections import Counter
m2 = dict(Counter(e["m2_outcome"] for e in episodes))
wf = [e for e in episodes if e["m1_valid"]]
m3 = (sum(e["pass"] == "pass" for e in wf) / len(wf)) if wf else None
overall = sum(e["pass"] == "pass" for e in episodes) / len(episodes)
summary = {"model": model_key, "rung": rung, "K": K, "mechanism": MECH,
           "gen_cap": cfg["max_tokens"], "m1_valid_rate": round(m1, 3),
           "m2_outcomes": m2, "m3_pass_given_valid_tool": None if m3 is None else round(m3, 3),
           "overall_pass": round(overall, 3),
           "gate": ("PASS" if m1 >= 0.5 else "FAIL") if rung == "F16" else None}
(out / "summary.json").write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
