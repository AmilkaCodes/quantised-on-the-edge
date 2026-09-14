#!/usr/bin/env python3
"""E4 stage-0 — decontamination sweep (spec ethics item 5): drop any training/valid example sharing
a 13-gram with HumanEval+ (prompts + canonical solutions) OR MBPP+ (reserved future benchmark).
Rewrites the jsonl in place minus hits; emits the committed sweep report. Run with the STUDY venv
(evalplus provides both benchmarks)."""
import json, re, hashlib
from pathlib import Path
from evalplus.data import get_human_eval_plus, get_mbpp_plus

D = Path.home() / "pilot-work/e4-data"
HERE = Path(__file__).resolve().parent

def ngrams13(s):
    w = re.findall(r"[a-z0-9]+", s.lower())
    return set(zip(*[w[i:] for i in range(13)])) if len(w) >= 13 else set()

bench = set()
for loader, name in [(get_human_eval_plus, "humaneval+"), (get_mbpp_plus, "mbpp+")]:
    P = loader()
    for t in P:
        bench |= ngrams13(P[t]["prompt"] + P[t].get("canonical_solution", ""))
print(f"benchmark 13-gram set: {len(bench)}")

report = {}
for split in ["train", "valid"]:
    rows = [json.loads(l) for l in (D / f"{split}.jsonl").open()]
    keep, dropped = [], 0
    for r in rows:
        if ngrams13(r["prompt"] + r["completion"]) & bench:
            dropped += 1
        else:
            keep.append(r)
    (D / f"{split}.jsonl").write_text("".join(json.dumps(r) + "\n" for r in keep))
    report[split] = {"before": len(rows), "dropped": dropped, "after": len(keep),
                     "sha256_after": hashlib.sha256((D / f"{split}.jsonl").read_bytes()).hexdigest()}
(HERE / "e4-decontamination-report.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
print("Guard: no surviving example shares a >=13-gram with HumanEval+ or MBPP+.")
