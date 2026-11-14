#!/usr/bin/env python3
"""E1-N — build the FROZEN neutral-context artefact (implements irp/extensions/e1n-neutral-context-control.md).

For each HumanEval+ problem: two chunks from the SAME frozen Python 3.12 docs index as Condition B,
chosen to be irrelevant (excluded: that problem's top-50 BM25 chunks), drawn from ONE seeded stream
(random.Random(0), problems in task order), redrawn until the pair's estimated token length is within
20% of that problem's Condition-B pair. Same 13-gram contamination rule as e1_build.py; same prompt
format (chunk1\\n\\nchunk2\\n\\n<INSTRUCTION-wrapped closed-book prompt>); same 4,096 budget check.

Outputs (committed): neutral_prompts.jsonl, e1n-build-manifest.json."""
import json, re, sys, random, hashlib
from pathlib import Path
from evalplus.data import get_human_eval_plus
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import run_pilot  # noqa: E402
from docs_index import DocsIndex, tok  # noqa: E402

OUT = Path(__file__).resolve().parent
SEED = 0
EXCLUDE_TOP = 50
LEN_TOL = 0.20
GEN_CAP, CTX_BUDGET = 768, 4096                       # as e1_build.py
OPENBOOK = OUT / "openbook_prompts.jsonl"
OPENBOOK_SHA = "95069f4b461426a48e348065ca110d0a95fb2f2294c637db123d8a472bb5007c"  # e1-build-manifest.json

def est_tokens(s: str) -> int:
    return (len(s) + 3) // 4                          # the e1_build.py proxy, so lengths are comparable

def word_ngrams(s: str, n: int):
    w = re.findall(r"[a-z0-9]+", " ".join(s.lower().split()))
    return set(zip(*[w[i:] for i in range(n)])) if len(w) >= n else set()

assert hashlib.sha256(OPENBOOK.read_bytes()).hexdigest() == OPENBOOK_SHA, "Condition-B artefact changed"
ix = DocsIndex()
assert len(ix.chunks) == 8239, f"chunk count {len(ix.chunks)} != registered 8239"
problems = get_human_eval_plus()
canon13 = set().union(*[word_ngrams(problems[t]["prompt"] + problems[t]["canonical_solution"], 13)
                        for t in problems])
INSTR = run_pilot.INSTRUCTION
openbook = {json.loads(l)["task_id"]: json.loads(l) for l in OPENBOOK.read_text().splitlines()}

rng = random.Random(SEED)
records, draws_log = [], []
for t in sorted(problems, key=lambda x: int(x.split("/")[1])):
    p = problems[t]
    closed = INSTR.format(prompt=p["prompt"])
    b_content = openbook[t]["content"]
    assert b_content.endswith("\n\n" + closed), f"{t}: Condition-B format mismatch"
    b_pair = b_content[: -len("\n\n" + closed)]       # "chunk1\n\nchunk2" exactly as B sent it
    target = est_tokens(b_pair)
    scores = ix.bm25.get_scores(tok(p["prompt"]))     # same query as B: signature + docstring
    excluded = set(sorted(range(len(ix.chunks)), key=lambda i: scores[i], reverse=True)[:EXCLUDE_TOP])
    n_draws = 0
    while True:
        n_draws += 1
        i, j = rng.sample(range(len(ix.chunks)), 2)
        if i in excluded or j in excluded:
            continue
        if word_ngrams(ix.chunks[i], 13) & canon13 or word_ngrams(ix.chunks[j], 13) & canon13:
            continue
        pair = f"{ix.chunks[i]}\n\n{ix.chunks[j]}"
        if abs(est_tokens(pair) - target) <= LEN_TOL * target:
            break
    assert est_tokens(pair) + est_tokens(closed) + GEN_CAP <= CTX_BUDGET, f"{t}: over budget"
    content = f"{pair}\n\n{closed}"
    records.append({"task_id": t, "content": content,
                    "chunk_idx": [i, j], "chunk_src": [ix.src[i], ix.src[j]],
                    "pair_tokens_est": est_tokens(pair), "b_pair_tokens_est": target,
                    "n_tokens_est": est_tokens(content)})
    draws_log.append(n_draws)

(OUT / "neutral_prompts.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records))
sha = hashlib.sha256((OUT / "neutral_prompts.jsonl").read_bytes()).hexdigest()
ratios = sorted(r["pair_tokens_est"] / r["b_pair_tokens_est"] for r in records)
manifest = {
    "protocol": "irp/extensions/e1n-neutral-context-control.md",
    "condition_b_artefact_sha256": OPENBOOK_SHA, "n_chunks": len(ix.chunks),
    "seed": SEED, "exclude_top_bm25": EXCLUDE_TOP, "length_tolerance": LEN_TOL,
    "length_measure": "est_tokens = ceil(chars/4), as e1_build.py",
    "contamination_rule": "13-gram vs union of HumanEval+ prompt+canonical solutions (as e1_build.py)",
    "n_problems": len(records), "neutral_prompts_sha256": sha,
    "pair_len_ratio_N_over_B_min_median_max": [round(ratios[0], 3), round(ratios[len(ratios) // 2], 3),
                                               round(ratios[-1], 3)],
    "draws_per_problem_min_median_max": [min(draws_log), sorted(draws_log)[len(draws_log) // 2], max(draws_log)],
}
(OUT / "e1n-build-manifest.json").write_text(json.dumps(manifest, indent=2))
print(json.dumps(manifest, indent=2))
