# E1 contamination sweep report

Corpus: Python 3.12 series (docs.python.org 3.12 branch; text archive) (sha256 `8173bb9b389063a8…`, retrieved 2026-09-12).
8239 chunks from 348 pages (library+reference+tutorial).
BM25Okapi k1=1.5 b=0.75; top-k=2; query = signature+docstring verbatim.

## 13-gram fails (chunk replaced by next-ranked, protocol §3)
**0 replacements.**

## 8-12-gram overlaps (reported, not failed)
**34 problems** had any 8-12-gram overlap with a reference solution.
- HumanEval/0: 3 overlapping n-grams
- HumanEval/5: 3 overlapping n-grams
- HumanEval/20: 3 overlapping n-grams
- HumanEval/21: 3 overlapping n-grams
- HumanEval/22: 3 overlapping n-grams
- HumanEval/26: 1 overlapping n-grams
- HumanEval/30: 3 overlapping n-grams
- HumanEval/31: 3 overlapping n-grams
- HumanEval/32: 1 overlapping n-grams
- HumanEval/34: 6 overlapping n-grams
- HumanEval/36: 2 overlapping n-grams
- HumanEval/39: 3 overlapping n-grams
- HumanEval/42: 3 overlapping n-grams
- HumanEval/49: 4 overlapping n-grams
- HumanEval/62: 1 overlapping n-grams
- HumanEval/67: 3 overlapping n-grams
- HumanEval/73: 9 overlapping n-grams
- HumanEval/75: 3 overlapping n-grams
- HumanEval/81: 6 overlapping n-grams
- HumanEval/82: 3 overlapping n-grams
- HumanEval/87: 6 overlapping n-grams
- HumanEval/88: 6 overlapping n-grams
- HumanEval/94: 3 overlapping n-grams
- HumanEval/105: 9 overlapping n-grams
- HumanEval/109: 6 overlapping n-grams
- HumanEval/116: 3 overlapping n-grams
- HumanEval/120: 9 overlapping n-grams
- HumanEval/122: 6 overlapping n-grams
- HumanEval/126: 6 overlapping n-grams
- HumanEval/128: 9 overlapping n-grams
- HumanEval/129: 6 overlapping n-grams
- HumanEval/131: 6 overlapping n-grams
- HumanEval/133: 3 overlapping n-grams
- HumanEval/146: 6 overlapping n-grams

## Budget truncations
**0** problems truncated chunk 2.

## Thesis line
> No retrieved chunk shared a ≥13-gram overlap with any canonical HumanEval+ reference solution in the final artefact.
