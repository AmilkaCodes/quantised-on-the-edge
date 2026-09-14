#!/usr/bin/env python3
"""E4 stage-0 — build the LoRA training set from Glaive FC v2 (spec: e4-finetuned-toolcalling-spec.md).

Pipeline (deterministic, seed 0; source pinned sha e9b5d671…):
  parse Glaive rows -> keep SINGLE-function examples (calling AND refusal/no-call dialogues — the
  policy signal) -> re-render into the Qwen2.5 chat template with tools (the exact hermes
  <tool_call> wrapper the stock model failed to emit) -> per-assistant-turn (prompt, completion)
  pairs via prefix-subtraction (loss on the assistant turn only) -> sample train/valid.

Run with the ISOLATED e4-venv (transformers >= 5.17 for template tool support). Outputs to
~/pilot-work/e4-data/{train,valid}.jsonl + a manifest here. Data is regenerable (pinned source +
seed) so the jsonl stays local; builder + manifest + sweep report are the committed record."""
import json, re, random, hashlib
from pathlib import Path
from transformers import AutoTokenizer

SRC = Path.home() / "pilot-work/e4-data/glaive-fc-v2.json"
OUTD = Path.home() / "pilot-work/e4-data"
HERE = Path(__file__).resolve().parent
N_TRAIN, N_VALID, SEED = 3000, 300, 0
tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-Coder-1.5B-Instruct")

def find_json(text, start=0):
    i = text.find("{", start)
    while i != -1:
        depth = 0
        for j in range(i, len(text)):
            if text[j] == "{": depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[i:j+1]), j+1
                    except Exception:
                        break
        i = text.find("{", i+1)
    return None, len(text)

def parse_system(s):
    """Return the single tool schema, or None (no-tool or multi-tool rows are skipped)."""
    if "no access to external functions" in s: return None
    fn1, end = find_json(s)
    if not fn1 or "name" not in fn1: return None
    fn2, _ = find_json(s, end)
    if fn2 and "name" in fn2: return None          # multi-tool -> skip
    return {"type": "function", "function": fn1}

def parse_chat(chat):
    """Glaive chat -> messages list (user / assistant[+tool_calls] / tool)."""
    msgs = []
    for turn in re.split(r"\n\n\n+", chat.strip()):
        t = turn.strip()
        if t.startswith("USER: "):
            msgs.append({"role": "user", "content": t[6:].strip()})
        elif t.startswith("FUNCTION RESPONSE: "):
            msgs.append({"role": "tool", "content": t[19:].strip()})
        elif t.startswith("ASSISTANT: "):
            body = t[11:].replace("<|endoftext|>", "").strip()
            if "<functioncall>" in body:
                pre, _, callpart = body.partition("<functioncall>")
                raw = callpart.strip()
                # Glaive quirk: arguments is a single-quoted JSON string
                raw = re.sub(r"\"arguments\":\s*'(.*)'\s*}\s*$",
                             lambda m: '"arguments": ' + json.dumps(m.group(1)), raw, flags=re.S)
                call, _ = find_json(raw)
                if not call or "name" not in call: return None
                args = call.get("arguments", "{}")
                if isinstance(args, str):
                    try: args = json.loads(args)
                    except Exception: return None
                msgs.append({"role": "assistant", "content": pre.strip() or "",
                             "tool_calls": [{"type": "function",
                                             "function": {"name": call["name"], "arguments": args}}]})
            else:
                msgs.append({"role": "assistant", "content": body})
        else:
            return None
    return msgs or None

def pairs_from(tool, msgs):
    """ITERATION-2 FIX (2026-09-14, dated deviation): run 1 used prompt/completion pairs of
    PRE-RENDERED template text — but mlx_lm's CompletionsDataset wraps those fields as user/assistant
    messages and RE-applies the chat template (double templating), embedding literal
    '<|im_start|>assistant' inside a user turn followed by '<|im_end|>' — teaching exactly the
    instant-EOS pathology observed at the gate (root cause verified: base model answers the same
    prompt; adapter EOSes; datasets.py L108-111). Fix: emit NATIVE ChatDataset examples —
    {"messages": msgs[:i+1], "tools": [tool]} per assistant turn — single templating by mlx itself,
    with --mask-prompt so loss lands on the final assistant turn only."""
    out = []
    for i, m in enumerate(msgs):
        if m["role"] != "assistant": continue
        try:
            rendered = tok.apply_chat_template(msgs[:i+1], tools=[tool], tokenize=False)
            if len(rendered) < 8000:
                out.append({"messages": msgs[:i+1], "tools": [tool],
                            "kind": "call" if m.get("tool_calls") else "reply"})
        except Exception:
            continue
    return out

data = json.loads(SRC.read_text())
rng = random.Random(SEED)
rng.shuffle(data)
# Rebalance decision (dated 2026-09-14, pre-training): the deficit under test is CALL EMISSION;
# the natural per-turn call share is ~10% (reply turns dominate multi-turn dialogues), which would
# under-teach the target behaviour. Collect until the call pool is large enough for a ~47% call
# share in train/valid; composition recorded in the manifest.
CALL_TARGET = 1650
pairs, kinds = [], {"call": 0, "reply": 0}
for row in data:
    if kinds["call"] >= CALL_TARGET and kinds["reply"] >= 2 * CALL_TARGET: break
    tool = parse_system(row["system"])
    if not tool: continue
    msgs = parse_chat(row["chat"])
    if not msgs: continue
    for p in pairs_from(tool, msgs):
        pairs.append(p); kinds[p["kind"]] += 1

calls = [p for p in pairs if p["kind"] == "call"]
replies = [p for p in pairs if p["kind"] == "reply"]
rng.shuffle(calls); rng.shuffle(replies)
train = calls[:1400] + replies[:1600]
valid = calls[1400:1550] + replies[1600:1750]
rng.shuffle(train); rng.shuffle(valid)
(OUTD / "train.jsonl").write_text("".join(json.dumps({"messages": p["messages"], "tools": p["tools"]}) + "\n" for p in train))
(OUTD / "valid.jsonl").write_text("".join(json.dumps({"messages": p["messages"], "tools": p["tools"]}) + "\n" for p in valid))
manifest = {"source": "glaiveai/glaive-function-calling-v2 (apache-2.0, verified at source)",
            "source_sha256": "e9b5d671812b5ca2fbd7b625a37d5c99a19576c37252cdc806defe256aea6dad",
            "seed": SEED, "pool_pairs": len(pairs), "train": len(train), "valid": len(valid),
            "kind_mix_pool": kinds,
            "train_call_share": round(sum(p['kind']=='call' for p in train)/len(train), 3),
            "format": "NATIVE ChatDataset examples ({messages, tools}) — iteration-2 fix; single templating by mlx_lm; train with --mask-prompt",
            "train_sha256": hashlib.sha256((OUTD/'train.jsonl').read_bytes()).hexdigest(),
            "valid_sha256": hashlib.sha256((OUTD/'valid.jsonl').read_bytes()).hexdigest()}
(HERE / "e4-data-manifest.json").write_text(json.dumps(manifest, indent=2))
print(json.dumps(manifest, indent=2))
