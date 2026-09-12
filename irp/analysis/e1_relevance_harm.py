#!/usr/bin/env python3
"""E1 Tier-1 secondary analysis (exploratory, post-hoc, clearly labelled): does retrieval RELEVANCE
predict per-problem open-book harm? Competing proxy also tested: injected-context LENGTH.

Per problem: relevance proxy = max BM25 score of the two injected chunks (recomputed from the frozen
index — recomputation also re-verifies retrieval determinism against the committed artefact's chunk
sources); harm = closed-pass -> open-fail ("broken"), assessed among closed-book passers.
Stats per model (headline rung + pooled): Mann-Whitney U (scores: broken vs survived) and a
median-split Fisher exact. Run from proposal-dev/pilot."""
import json, glob, sys
from pathlib import Path
import numpy as np
from scipy.stats import mannwhitneyu, fisher_exact

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "proposal-dev" / "pilot" / "e1"))
from docs_index import DocsIndex, tok
from evalplus.data import get_human_eval_plus

QUANTS = ["F16", "Q8_0", "Q4_K_M", "Q3_K_M", "Q2_K"]
MODELS = {"qwen2.5-coder-1.5b-instruct": "Q2_K", "phi-3-mini-4k-instruct": "Q4_K_M"}  # headline rungs

# --- recompute per-problem retrieval scores + verify determinism vs the committed artefact ---
ix = DocsIndex()
P = get_human_eval_plus()
art = {json.loads(l)["task_id"]: json.loads(l)
       for l in open("e1/openbook_prompts.jsonl")}
rel, clen, mismatch = {}, {}, 0
for t, p in P.items():
    scores = ix.bm25.get_scores(tok(p["prompt"]))
    top = sorted(range(len(ix.chunks)), key=lambda i: scores[i], reverse=True)[:2]
    if [ix.src[i] for i in top] != art[t]["chunk_src"]:
        mismatch += 1                      # contamination replacement or drift — count, don't assume
    rel[t] = float(max(scores[i] for i in top))
    clen[t] = art[t]["n_tokens_est"]
print(f"retrieval determinism check: {164 - mismatch}/164 problems' top-2 chunk sources match the artefact"
      f" ({mismatch} differ — expected 0 given the sweep had 0 contamination replacements)")

def load(full, q, sfx):
    f = glob.glob(f"results/mac/samples_{full}_{q}{sfx}-sanitized_eval_results.json")[0]
    d = json.load(open(f))["eval"]
    return {t: d[t][0]["plus_status"] == "pass" for t in d}

for full, head in MODELS.items():
    print(f"\n================ {full} ================")
    rows = []
    for q in QUANTS:
        A, B = load(full, q, ""), load(full, q, "_open")
        for t in A:
            if A[t]:                                   # closed-book passers only
                rows.append({"rung": q, "task": t, "broken": not B[t],
                             "rel": rel[t], "len": clen[t]})
    for scope, sel in [("pooled all rungs", rows),
                       (f"headline rung {head}", [r for r in rows if r["rung"] == head])]:
        broke = [r for r in sel if r["broken"]]; ok = [r for r in sel if not r["broken"]]
        if not broke or not ok:
            print(f"  {scope}: insufficient cells"); continue
        for proxy, lbl in [("rel", "BM25 relevance"), ("len", "context length")]:
            xb, xo = [r[proxy] for r in broke], [r[proxy] for r in ok]
            u = mannwhitneyu(xb, xo, alternative="two-sided")
            med = float(np.median([r[proxy] for r in sel]))
            lo = [r for r in sel if r[proxy] <= med]; hi = [r for r in sel if r[proxy] > med]
            tab = [[sum(r["broken"] for r in lo), sum(not r["broken"] for r in lo)],
                   [sum(r["broken"] for r in hi), sum(not r["broken"] for r in hi)]]
            fe = fisher_exact(tab)
            print(f"  {scope:22s} {lbl:15s}: broken median={np.median(xb):8.2f} vs survived={np.median(xo):8.2f}"
                  f" | MWU p={u.pvalue:.3f} | break-rate low/high split ="
                  f" {tab[0][0]}/{tab[0][0]+tab[0][1]} vs {tab[1][0]}/{tab[1][0]+tab[1][1]}"
                  f" (Fisher p={fe.pvalue:.3f})")
print("\nDONE (exploratory — no pre-registered hypotheses; report descriptively)")
