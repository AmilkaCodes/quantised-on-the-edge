#!/usr/bin/env python3
"""E1-R Probe R2 — build the ORACLE open-book artefact (e1r-protocol.md, committed pre-run).

Oracle selection (measurement instrument, upper bound — NEVER a deployable system): for each problem,
rank ALL corpus chunks by normalised content-token overlap with the problem's canonical reference
solution and take the top-2. Overlap metric (fixed here): score(chunk) =
|U(chunk) ∩ U(solution)| / |U(solution)|, where U(x) = unique lowercase [a-z0-9]+ tokens minus a small
stopword set; ties broken by chunk index (deterministic). The solution is used ONLY for selection —
no solution text enters any prompt, enforced by the SAME contamination guard as E1 (any shared
13-gram chunk↔any-canonical-solution → replaced by next-ranked; 8–12-grams reported).
Output: e1/oracle_prompts.jsonl (same layout as Condition B: chunk1\\n\\nchunk2\\n\\n[closed prompt]),
sweep report, build manifest."""
import json, re, sys, hashlib
from pathlib import Path
from evalplus.data import get_human_eval_plus
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import run_pilot as RP                      # INSTRUCTION
from docs_index import load_chunks

OUT = Path(__file__).resolve().parent
STOP = {"the","a","an","of","to","in","is","are","and","or","for","it","this","that","be","as",
        "if","with","on","by","not","return","returns","def","from","import"}

def U(s):
    return {t for t in re.findall(r"[a-z0-9]+", s.lower()) if t not in STOP and len(t) > 1}

def word_ngrams(s, n):
    w = re.findall(r"[a-z0-9]+", " ".join(s.lower().split()))
    return set(zip(*[w[i:] for i in range(n)])) if len(w) >= n else set()

chunks, src = load_chunks()
chunk_U = [U(c) for c in chunks]
P = get_human_eval_plus()
canon_texts = [P[t]["prompt"] + P[t]["canonical_solution"] for t in P]
canon_ng = {n: set().union(*[word_ngrams(c, n) for c in canon_texts]) for n in range(8, 14)}

records, sweep = [], {"replacements": [], "reports_8_12": 0}
for t in sorted(P, key=lambda x: int(x.split("/")[1])):
    sol_U = U(P[t]["canonical_solution"])
    scores = [(len(chunk_U[i] & sol_U) / max(len(sol_U), 1), -i) for i in range(len(chunks))]
    ranked = sorted(range(len(chunks)), key=lambda i: scores[i], reverse=True)
    picked = []
    for i in ranked:
        if len(picked) == 2:
            break
        if word_ngrams(chunks[i], 13) & canon_ng[13]:
            sweep["replacements"].append({"task_id": t, "rejected": src[i]})
            continue
        picked.append(i)
    sweep["reports_8_12"] += sum(len(word_ngrams(chunks[i], n) & canon_ng[n])
                                 for i in picked for n in range(8, 13))
    closed = RP.INSTRUCTION.format(prompt=P[t]["prompt"])
    content = f"{chunks[picked[0]]}\n\n{chunks[picked[1]]}\n\n{closed}"
    records.append({"task_id": t, "content": content,
                    "chunk_src": [src[i] for i in picked],
                    "oracle_scores": [round(scores[i][0], 4) for i in picked]})

(OUT / "oracle_prompts.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records))
sha = hashlib.sha256((OUT / "oracle_prompts.jsonl").read_bytes()).hexdigest()
(OUT / "e1r-oracle-sweep-report.md").write_text(
    f"# E1-R oracle artefact sweep report\n\n{len(records)} problems; selection = content-token overlap "
    f"with canonical solution (metric fixed in e1r_build_oracle.py).\n\n- 13-gram FAIL replacements: "
    f"**{len(sweep['replacements'])}**\n- total 8-12-gram overlaps (reported): {sweep['reports_8_12']}\n"
    f"- artefact sha256: `{sha}`\n\n"
    + ("\n".join("- {}: rejected `{}`".format(x["task_id"], x["rejected"])
                 for x in sweep["replacements"][:60]) or "(no replacements)")
    + "\n\n> Guard holds: no retrieved chunk in the final artefact shares a >=13-gram overlap with any "
      "canonical solution.\n")
print(f"oracle_prompts.jsonl: {len(records)} problems, sha256 {sha[:16]}…")
print(f"13-gram replacements: {len(sweep['replacements'])} | 8-12-gram overlaps: {sweep['reports_8_12']}")
print("mean top-1 oracle score:", round(sum(r['oracle_scores'][0] for r in records)/len(records), 3))
