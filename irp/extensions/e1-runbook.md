# E1 run-book — build & run order on the Mac

_Operational checklist implementing `e1-protocol.md` (the protocol governs; this file is just
the order of work). Tick + annotate as-run, setup-log style. Record the protocol's git commit
hash in every manifest._

## Phase 1 — Corpus + frozen artefact (no measurement yet)
- [ ] `git pull`; note the e1-protocol.md commit hash: ______
- [ ] Download the official Python docs **plain-text archive** for one pinned 3.12.x version
      (docs.python.org publishes `python-3.12.x-docs-text` archives) — record exact version,
      URL, date, sha256: ______
- [ ] Chunker per protocol §1 (section split; >1,500 chars → paragraph split; no overlap).
      Record chunk count + size distribution: ______
- [ ] BM25 index (rank_bm25 BM25Okapi, defaults). Freeze.
- [ ] Build `openbook_prompts.jsonl` per §2 (query = signature+docstring verbatim; k=2;
      4,096-token budget check; truncations logged): ______
- [ ] **Contamination sweep per §3** → committed report. 13-gram fails (replaced): ______ ·
      8–12-gram reports: ______
- [ ] **COMMIT the artefact + sweep report.** From here the prompts are immutable study
      material; artefact commit hash: ______

## Phase 2 — Harness + smoke (instrument validation)
- [ ] Harness: `--condition open` flag consuming the artefact (prompt substitution ONLY —
      decoding, scoring, manifests unchanged; manifest gains `condition` + artefact hash)
- [ ] Plumbing smoke: 2 problems, Qwen Q4_K_M, open condition — server up, prompts match the
      artefact byte-for-byte, CSV row written. (Instrument validation, not a scored run.)

## Phase 3 — Condition B sweeps (RQ1b data)
- [ ] Qwen: 5 rungs × 164, open-book, Mac, tmux; manifests complete
- [ ] Phi-3: 5 rungs × 164, open-book
- [ ] Cross-device spot-check per §0: K=25 open-book generations, one rung (Q4_K_M),
      Pi + Jetson vs Mac — disagreement rate recorded: ______
- [ ] Analysis per §4: per-rung B-vs-A McNemar + bootstrap CIs + 5pp margin per condition +
      the Δ(B−A) interaction; results committed
- [ ] Optional perf cells: Q4_K_M open vs closed TTFT/peak-mem per tier: ______

## Phase 4 — Condition D (RQ1c; timebox clock starts at first harness work)
- [ ] Tool-loop harness per §5 (single `search_docs` tool → same frozen index; max 4 turns;
      sandboxed) — build + validate. Timebox start date: ______
- [ ] **GATE:** Qwen F16, 20 problems → M1 valid-call rate = ______ (pass ≥50%)
- [ ] If pass: ladder probe, Qwen, 30 × 5 rungs → M1/M2/M3 per rung
- [ ] If fail: STOP; write the F16-floor finding
- [ ] Probe write-up either way; escalation only per the binding rule in §5

## Rhythm
Push results after every completed phase; log deviations in e1-protocol.md §6 BEFORE the
affected run where foreseeable; project-log entry per session.
