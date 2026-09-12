# E1 run-book — build & run order on the Mac

_Operational checklist implementing `e1-protocol.md` (the protocol governs; this file is just
the order of work). Tick + annotate as-run, setup-log style. Record the protocol's git commit
hash in every manifest._

## Phase 1 — Corpus + frozen artefact (no measurement yet) — DONE 2026-09-12
- [x] `git pull`; e1-protocol.md commit hash: **8375d3c** (gate 1 satisfied).
- [x] Downloaded Python 3.12 docs **text archive**: URL
      `https://docs.python.org/3.12/archives/python-3.12-docs-text.zip`, retrieved **2026-09-12**,
      **sha256 `8173bb9b389063a8e8bc6555bedc4688fb7bd07a8878f98eccbd900614c8866f`** (3.12 branch; text
      archive carries version strings up to 3.12.9). Raw docs live in `~/pilot-work/e1-corpus/` (regenerable).
- [x] Chunker per §1 (section split; >1,500 chars → paragraph split; no overlap; scope =
      library+reference+tutorial): **8,239 chunks from 348 pages**, chars min/median/max = 7/968/1500.
- [x] BM25 index (rank_bm25 BM25Okapi, k1=1.5 b=0.75, lowercase `[a-z0-9]+` tokenisation). Built in
      `e1_build.py`; regenerable from the pinned archive.
- [x] Built `openbook_prompts.jsonl` per §2 (query = signature+docstring verbatim; k=2; 4,096-token
      budget check): **164 problems, sha256 `95069f4b461426a4…`; 0 truncations.**
- [x] **Contamination sweep per §3:** **13-gram fails (replaced): 0** · 8–12-gram overlaps reported on
      **34/164** problems (not failed) · thesis line holds literally ("no retrieved chunk shared a
      ≥13-gram overlap with any reference solution"). Report: `e1/e1-sweep-report.md`.
- [x] **COMMITTED** the artefact + sweep report + build script + manifest (`proposal-dev/pilot/e1/`).
      From here the prompts are immutable study material.

## Phase 2 — Harness + smoke (instrument validation)
- [ ] Harness: `--condition open` flag consuming the artefact (prompt substitution ONLY —
      decoding, scoring, manifests unchanged; manifest gains `condition` + artefact hash)
- [ ] Plumbing smoke: 2 problems, Qwen Q4_K_M, open condition — server up, prompts match the
      artefact byte-for-byte, CSV row written. (Instrument validation, not a scored run.)

## Phase 3 — Condition B sweeps (RQ1b data)
- [x] Qwen: 5 rungs × 164, open-book, Mac — **DONE 2026-09-12** (caffeinated background run;
      manifest carries condition=open + artefact sha `95069f4b…`)
- [x] Phi-3: 5 rungs × 164, open-book — **DONE 2026-09-12** (same run;
      `pilot_results_open_20260912_144604.csv`)
- [ ] Cross-device spot-check per §0: K=25 open-book generations, one rung (Q4_K_M),
      Pi + Jetson vs Mac — disagreement rate recorded: ______
- [x] Analysis per §4 — **DONE 2026-09-12** (`irp/analysis/e1_analysis.py` →
      `irp/analysis/e1-openbook.md`). Headline: **Δ(B−A) ≤ 0 in all 10 cells** — frozen doc-context
      never helps and hurts most AT each model's collapse rung (Qwen Q2 −0.098 p=.007; Phi Q4 −0.152
      p=.0008); 5pp thresholds condition-invariant (Q2/Q4).
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
