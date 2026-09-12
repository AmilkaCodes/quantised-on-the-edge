#!/usr/bin/env python3
"""Cross-device spot-check (PRE-REGISTERED, proposal Methodology: "a cross-device spot-check confirms
outputs match"). Confirms the SAME (model x quant x prompt) yields the SAME extracted solution across
tiers -> the quality axis is hardware-independent (the premise that lets it be measured once on the Mac;
RQ3). Reuses run_pilot.generate() so prompt formatting, temperature (0), seed (0) and max_tokens are
IDENTICAL to the quality run. Any divergence would mean backend floating-point differences (Metal vs
CUDA vs CPU) change greedy decoding.

Usage (from proposal-dev/pilot, server-managing config):
    python cross_device_check.py [config] [model_key] [rung] [K]
    defaults: configs/mac.yaml  qwen2.5-coder-1.5b-instruct  Q4_K_M  8
Run once per device; then diff the per-device results/<device>/xdev_*.json files.
"""
import json, sys
from pathlib import Path
import yaml
from openai import OpenAI
import run_pilot as H

cfg_path  = sys.argv[1] if len(sys.argv) > 1 else "configs/mac.yaml"
model_key = sys.argv[2] if len(sys.argv) > 2 else "qwen2.5-coder-1.5b-instruct"
rung      = sys.argv[3] if len(sys.argv) > 3 else "Q4_K_M"
K         = int(sys.argv[4]) if len(sys.argv) > 4 else 8
condition = sys.argv[5] if len(sys.argv) > 5 else "closed"   # E1: 'open' for the open-book spot-check

cfg = yaml.safe_load(Path(cfg_path).read_text())
device = str(cfg.get("device", "unknown"))
model = next(m for m in cfg["models"] if m["name"] == model_key)
quant = next(q for q in model["quants"] if q["label"] == rung)
problems = dict(list(H.get_human_eval_plus().items())[:K])
openbook = None
if condition == "open":
    art = Path(__file__).resolve().parent / "e1" / "openbook_prompts.jsonl"
    allc = {json.loads(l)["task_id"]: json.loads(l)["content"] for l in art.read_text().splitlines()}
    openbook = {t: allc[t] for t in problems}
print(f"[{device}] {model_key}:{rung}  K={len(problems)}  cond={condition}  tag={cfg.get('llama_cpp_tag')}")

if H.port_in_use(cfg["host"], cfg["port"]):
    sys.exit(f"port {cfg['port']} busy — kill the stale server first")
srv = H.launch_server(cfg, model, quant)
H.wait_ready(cfg, srv)
client = OpenAI(base_url=f"http://{cfg['host']}:{cfg['port']}/v1", api_key="sk-noauth")
try:
    samples, _ = H.generate(client, quant["label"], problems, cfg, openbook)
finally:
    H.stop_server(srv)

out = {s["task_id"]: s["solution"] for s in samples}
csfx = "" if condition == "closed" else f"_{condition}"
dest = H.RESULTS_ROOT / device / f"xdev_{model_key}_{rung}{csfx}.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps(out, indent=2, sort_keys=True))
print(f"[{device}] wrote {dest} ({len(out)} solutions)")
