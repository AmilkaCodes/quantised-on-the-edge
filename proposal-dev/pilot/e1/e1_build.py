#!/usr/bin/env python3
"""E1 Phase 1 — build the FROZEN open-book artefact (implements e1-protocol.md §1-3).

Pipeline (all deterministic; run ONCE on the Mac, then commit the outputs):
  docs (pinned Python 3.12 text archive) -> section chunks (<=1500 chars, no overlap)
  -> BM25Okapi index (k1=1.5, b=0.75) -> per-problem top-k=2 retrieval (query = signature+docstring)
  -> contamination sweep (13-gram fail -> next chunk; 8-12-gram reported)
  -> openbook_prompts.jsonl (chunk1\\n\\nchunk2\\n\\n<INSTRUCTION-wrapped closed-book prompt>).

Outputs (committed): openbook_prompts.jsonl, e1-sweep-report.md, e1-build-manifest.json.
The BM25 index + raw docs stay in ~/pilot-work/e1-corpus (regenerable from the pinned archive)."""
import json, re, sys, os, hashlib
from pathlib import Path
from collections import Counter
from rank_bm25 import BM25Okapi
from evalplus.data import get_human_eval_plus
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # import run_pilot for INSTRUCTION
import run_pilot  # noqa: E402

CORPUS = Path(os.path.expanduser("~/pilot-work/e1-corpus/python-3.12-docs-text"))
OUT = Path(__file__).resolve().parent
SCOPE = ["library", "reference", "tutorial"]         # protocol §1 scope
MAX_CHARS = 1500                                      # protocol §1
K = 2                                                 # protocol §2
GEN_CAP = 768                                         # configs max_tokens
CTX_BUDGET = 4096                                     # Phi-3 window (protocol §2)
DOCS_SHA256 = "8173bb9b389063a8e8bc6555bedc4688fb7bd07a8878f98eccbd900614c8866f"
DOCS_URL = "https://docs.python.org/3.12/archives/python-3.12-docs-text.zip"
DOCS_RETRIEVED = "2026-09-12"

def est_tokens(s: str) -> int:
    return (len(s) + 3) // 4                          # conservative ~4 chars/token proxy

_UNDER = set('=-*^"~\'`#+.')
def split_sections(text: str):
    """Split a Sphinx text page on section headers (title line followed by an underline of punctuation)."""
    lines = text.split("\n")
    secs, cur = [], []
    for i, line in enumerate(lines):
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        is_header = (line.strip() and nxt.strip() and set(nxt.strip()) <= _UNDER
                     and len(nxt.strip()) >= 3 and abs(len(nxt.strip()) - len(line.strip())) <= 3)
        if is_header and cur:
            secs.append("\n".join(cur).strip()); cur = []
        cur.append(line)
    if cur:
        secs.append("\n".join(cur).strip())
    return [s for s in secs if s]

def chunk_section(sec: str):
    """<=1500 chars kept whole; larger split at paragraph (blank-line) boundaries, no overlap."""
    if len(sec) <= MAX_CHARS:
        return [sec]
    out, buf = [], ""
    for para in sec.split("\n\n"):
        if len(para) > MAX_CHARS:                     # a single huge paragraph: hard-split
            if buf: out.append(buf); buf = ""
            for j in range(0, len(para), MAX_CHARS):
                out.append(para[j:j + MAX_CHARS])
            continue
        if len(buf) + len(para) + 2 <= MAX_CHARS:
            buf = (buf + "\n\n" + para) if buf else para
        else:
            if buf: out.append(buf)
            buf = para
    if buf: out.append(buf)
    return out

# ---- 1. build chunks ----
chunks, chunk_src = [], []
for sub in SCOPE:
    for p in sorted((CORPUS / sub).rglob("*.txt")):
        text = p.read_text(encoding="utf-8", errors="replace")
        for sec in split_sections(text):
            for ch in chunk_section(sec):
                if ch.strip():
                    chunks.append(ch); chunk_src.append(str(p.relative_to(CORPUS)))
sizes = [len(c) for c in chunks]
print(f"chunks: {len(chunks)} from {len(set(chunk_src))} pages | "
      f"chars min/median/max = {min(sizes)}/{sorted(sizes)[len(sizes)//2]}/{max(sizes)}")

# ---- 2. BM25 index ----
def tok(s: str):
    return re.findall(r"[a-z0-9]+", s.lower())
bm25 = BM25Okapi([tok(c) for c in chunks], k1=1.5, b=0.75)

# ---- 3. n-gram contamination helpers ----
def word_ngrams(s: str, n: int):
    w = re.findall(r"[a-z0-9]+", " ".join(s.lower().split()))
    return set(zip(*[w[i:] for i in range(n)])) if len(w) >= n else set()

problems = get_human_eval_plus()
# Contamination = a retrieved chunk sharing an n-gram with ANY canonical solution -> precompute the
# UNION of all reference-solution n-grams once (n=8..13); check each chunk against these sets.
canon_texts = [problems[t]["prompt"] + problems[t]["canonical_solution"] for t in problems]
canon_ng = {n: set().union(*[word_ngrams(c, n) for c in canon_texts]) for n in range(8, 14)}

def shares_13gram(chunk: str) -> bool:
    return bool(word_ngrams(chunk, 13) & canon_ng[13])

def count_8_12(chunk: str) -> int:
    return sum(len(word_ngrams(chunk, n) & canon_ng[n]) for n in range(8, 13))

# ---- 4. retrieve top-k with contamination replacement + budget check ----
records, sweep = [], {"13gram_fail_replacements": [], "8_12gram_reports": [], "truncations": []}
INSTR = run_pilot.INSTRUCTION
order_cache = {}
for t in sorted(problems, key=lambda x: int(x.split("/")[1])):
    p = problems[t]
    q = tok(p["prompt"])                              # query = signature + docstring, verbatim
    scores = bm25.get_scores(q)
    ranked = sorted(range(len(chunks)), key=lambda i: scores[i], reverse=True)
    picked = []
    for idx in ranked:
        if len(picked) == K:
            break
        if shares_13gram(chunks[idx]):
            sweep["13gram_fail_replacements"].append({"task_id": t, "rejected_chunk": chunk_src[idx]})
            continue
        picked.append(idx)
    c8 = sum(count_8_12(chunks[i]) for i in picked)
    if c8:
        sweep["8_12gram_reports"].append({"task_id": t, "count": c8})
    closed = INSTR.format(prompt=p["prompt"])
    ch1, ch2 = chunks[picked[0]], chunks[picked[1]]
    # budget: chunks + prompt + gen cap <= 4096 tokens; truncate chunk2 only if over
    if est_tokens(ch1) + est_tokens(ch2) + est_tokens(closed) + GEN_CAP > CTX_BUDGET:
        allow = (CTX_BUDGET - GEN_CAP - est_tokens(ch1) - est_tokens(closed)) * 4
        ch2 = ch2[:max(0, allow)]
        sweep["truncations"].append({"task_id": t, "kept_chars": len(ch2)})
    content = f"{ch1}\n\n{ch2}\n\n{closed}"
    records.append({"task_id": t, "content": content,
                    "chunk_src": [chunk_src[i] for i in picked],
                    "n_tokens_est": est_tokens(content)})

# ---- 5. write committed artefacts ----
(OUT / "openbook_prompts.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records))
artefact_sha = hashlib.sha256((OUT / "openbook_prompts.jsonl").read_bytes()).hexdigest()

manifest = {
    "docs_version": "Python 3.12 series (docs.python.org 3.12 branch; text archive)",
    "docs_url": DOCS_URL, "docs_sha256": DOCS_SHA256, "docs_retrieved": DOCS_RETRIEVED,
    "scope": SCOPE, "n_chunks": len(chunks), "n_pages": len(set(chunk_src)),
    "chunk_chars_min_median_max": [min(sizes), sorted(sizes)[len(sizes)//2], max(sizes)],
    "bm25": {"impl": "rank_bm25 BM25Okapi", "k1": 1.5, "b": 0.75,
             "tokenisation": "lowercase, [a-z0-9]+"},
    "k": K, "max_chunk_chars": MAX_CHARS, "ctx_budget_tokens": CTX_BUDGET, "gen_cap": GEN_CAP,
    "n_problems": len(records), "openbook_prompts_sha256": artefact_sha,
    "sweep_summary": {"n_13gram_replacements": len(sweep["13gram_fail_replacements"]),
                      "n_problems_with_8_12gram": len(sweep["8_12gram_reports"]),
                      "n_truncations": len(sweep["truncations"])},
}
(OUT / "e1-build-manifest.json").write_text(json.dumps(manifest, indent=2))

report = [
    "# E1 contamination sweep report", "",
    f"Corpus: {manifest['docs_version']} (sha256 `{DOCS_SHA256[:16]}…`, retrieved {DOCS_RETRIEVED}).",
    f"{len(chunks)} chunks from {len(set(chunk_src))} pages (library+reference+tutorial).",
    f"BM25Okapi k1=1.5 b=0.75; top-k={K}; query = signature+docstring verbatim.", "",
    "## 13-gram fails (chunk replaced by next-ranked, protocol §3)",
    f"**{len(sweep['13gram_fail_replacements'])} replacements.**",
]
for x in sweep["13gram_fail_replacements"][:50]:
    report.append(f"- {x['task_id']}: rejected `{x['rejected_chunk']}`")
report += ["", "## 8-12-gram overlaps (reported, not failed)",
           f"**{len(sweep['8_12gram_reports'])} problems** had any 8-12-gram overlap with a reference solution."]
for x in sweep["8_12gram_reports"][:50]:
    report.append(f"- {x['task_id']}: {x['count']} overlapping n-grams")
report += ["", "## Budget truncations", f"**{len(sweep['truncations'])}** problems truncated chunk 2.", "",
           "## Thesis line",
           "> No retrieved chunk shared a ≥13-gram overlap with any canonical HumanEval+ reference "
           "solution in the final artefact." if not sweep["13gram_fail_replacements"] else
           "> All ≥13-gram-overlapping chunks were replaced by the next-ranked clean chunk; the final "
           "artefact contains no chunk sharing a ≥13-gram overlap with any reference solution."]
(OUT / "e1-sweep-report.md").write_text("\n".join(report) + "\n")

print(f"13-gram replacements: {len(sweep['13gram_fail_replacements'])} | "
      f"8-12gram problems: {len(sweep['8_12gram_reports'])} | truncations: {len(sweep['truncations'])}")
print(f"wrote openbook_prompts.jsonl ({len(records)} problems, sha256 {artefact_sha[:16]}…)")
