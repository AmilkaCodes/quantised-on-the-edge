# Audit and inference scripts (rescued from the 2026-09-21/28 session scratchpad)

- `final_audit.py` — recomputes all 36 quality cells and the derived deltas from the committed per-problem snapshots (expects PROBLEMS: 0).
- `paired_ci.py` — exact conditional and score-type intervals on the paired drop (data pack item 13).
- `agree_check.py` — bootstrap vs exact-conditional class agreement under the interval-only rule (imports paired_ci.py from this folder).
- `h1b_rule.py` — the H1b between-model difference-of-drops with Holm over all four rungs (data pack item 14).
- `render_pages.ps1` — rasterise PDF pages to PNG via WinRT (no poppler needed): `render_pages.ps1 -Pdf x.pdf -Pages 1,3 -OutDir .`

Run with `py -3`; the Python scripts hold the repo root as an absolute path constant and read the Mac eval snapshots.
