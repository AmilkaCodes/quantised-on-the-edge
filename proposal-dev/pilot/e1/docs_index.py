#!/usr/bin/env python3
"""Frozen documentation index, shared by Condition B's builder and Condition D's `search_docs` tool.
Chunking/tokenisation/BM25 parameters are IDENTICAL to e1_build.py (protocol §1); the corpus is the
pinned Python 3.12 text archive in ~/pilot-work/e1-corpus. Chunks are cached to JSON on first build so
the agentic harness starts in seconds. Sandboxed by construction: pure in-process lookup, no network."""
import json, re, os
from pathlib import Path
from rank_bm25 import BM25Okapi

CORPUS = Path(os.path.expanduser("~/pilot-work/e1-corpus/python-3.12-docs-text"))
CACHE = Path(os.path.expanduser("~/pilot-work/e1-corpus/chunks_cache.json"))
SCOPE = ["library", "reference", "tutorial"]
MAX_CHARS = 1500

_UNDER = set('=-*^"~\'`#+.')

def _split_sections(text: str):
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

def _chunk_section(sec: str):
    if len(sec) <= MAX_CHARS:
        return [sec]
    out, buf = [], ""
    for para in sec.split("\n\n"):
        if len(para) > MAX_CHARS:
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

def tok(s: str):
    return re.findall(r"[a-z0-9]+", s.lower())

def load_chunks():
    if CACHE.exists():
        d = json.loads(CACHE.read_text())
        return d["chunks"], d["src"]
    chunks, src = [], []
    for sub in SCOPE:
        for p in sorted((CORPUS / sub).rglob("*.txt")):
            text = p.read_text(encoding="utf-8", errors="replace")
            for sec in _split_sections(text):
                for ch in _chunk_section(sec):
                    if ch.strip():
                        chunks.append(ch); src.append(str(p.relative_to(CORPUS)))
    CACHE.write_text(json.dumps({"chunks": chunks, "src": src}))
    return chunks, src

class DocsIndex:
    def __init__(self):
        self.chunks, self.src = load_chunks()
        self.bm25 = BM25Okapi([tok(c) for c in self.chunks], k1=1.5, b=0.75)

    def search_docs(self, query: str, k: int = 2):
        """The Condition D tool: top-k chunks for a free-text query (same index as Condition B)."""
        scores = self.bm25.get_scores(tok(query))
        top = sorted(range(len(self.chunks)), key=lambda i: scores[i], reverse=True)[:k]
        return [{"source": self.src[i], "text": self.chunks[i]} for i in top]

if __name__ == "__main__":
    ix = DocsIndex()
    print(f"{len(ix.chunks)} chunks loaded")
    r = ix.search_docs("list comprehension filter elements")
    print(r[0]["source"], "|", r[0]["text"][:120].replace("\n", " "))
