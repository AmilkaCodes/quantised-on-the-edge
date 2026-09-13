# E1 implications — what the negative results mean for the thesis (discussion-chapter feed)

_Learning-mode framing note (2026-09-13), written after the E1 results discussion; the student owns
and adapts this framing in the assessed prose. Companion to `e1-openbook.md`, `e1-agentic.md`, and
`../extensions/e2-proposal.md`. Supervisor-agenda item alongside the E2 note._

## The worry, stated honestly
RAG and agentic loops are how deployed assistants actually work. E1 found that neither survives on a
quantised edge-class model — imposed doc-context *hurts* (worst at the collapse rung) and the native
tool-calling mechanism is inoperable at F16. Does the repatriation case therefore fall apart?

## The answer: no — the boundary moved, and locating boundaries was the job
The pre-registered claims were about the collapse threshold and the cost envelope, and those results
are *pro*-repatriation: a code-specialised 1.5B at Q4_K_M delivers F16-equivalent generation,
interactively, on a £375 CPU device. E1 did not weaken that; it located where local viability **ends**:

> **Generation repatriates; orchestration does not (at this scale).**

This upgrades, not undermines, the deployment story. The synthesis already carries memory-forced and
throughput-forced local↔cloud handoff triggers; E1 adds the third — a **capability-forced handoff**:
generation-shaped requests stay local, orchestration-needing requests route up. "Repatriate the
generation, not the orchestration" is a sharper thesis than an unbounded local-AI claim, and every
edge of it now has pre-registered evidence.

## Key mirror: "add a script that scans the docs for relevance" IS Condition B
The intuitive fix — move the intelligence into deterministic scaffolding — is exactly what Condition B
built: the frozen BM25 pipeline is a script that scans documentation and hands the model the results;
the model only had to read. It still lost quality. So the failure is not the delivery mechanism
(asked-for vs imposed — both ends of that axis were tested); it is **content × task**: HumanEval+
problems are self-contained (context is unnecessary), and lexical retrieval supplies
plausible-looking-but-unhelpful text — which the Tier-1 mechanism check hints is the worst kind of
distractor. The honest, already-logged limit: **a task where documentation is *necessary***
(version-specific APIs, unfamiliar libraries) is the fair test of edge-RAG, and it is E2/future-work
shaped — a named branch, not a debt.

## "Is F16 just too small for tool calls?" — half right, and the half matters
Three explanations for the Condition D gate failure, separated by the evidence:
1. **Instrument/format mismatch** — ruled out (`/apply-template` verified the rendered schema +
   format instruction; the parser channel works).
2. **Capacity (too small)** — plausible but not sufficient: TinyAgent shows ~1B models CAN call
   tools reliably *when fine-tuned for it*.
3. **Training (not tool-trained)** — the operative one. Qwen2.5-**Coder**-1.5B-Instruct is trained
   for code generation, not function-call protocol-binding: unforced it (rationally) ignores the
   tool and solves the task closed-book at 0.90; forced, it cannot hold the `<tool_call>` wrapper
   and degenerates. Taheri adds that even tool-trained small models crater at Q4.

So the gate finding stands as registered — *the stock agentic paradigm is inoperable at this scale* —
and the field's known remedy is **fine-tuning, not scale alone**. A tool-finetuned small model, or a
7–8B on the consumer tier, passing the gate is nameable future work; the two-model design was fixed
at registration.

## Effect on the RQ set: none — effect on the framing: one paragraph
Every RQ is answered and every negative branch was pre-declared reportable (research symmetry).
Candidate discussion-chapter spine:

> Quantisation is not what separates local models from deployed AI practice. Generation survives
> quantisation almost perfectly in a specialised model; retrieval-grounding and tool use fail
> **before** quantisation is applied — the one because the task's context is unnecessary and cheaply
> distracting, the other because the capability is absent at this scale. The edge case for LLMs is
> therefore strongest exactly where the measurements put it: closed-book, specialised, quantised to
> the knee — with orchestration living in the scaffold or the cloud.

Every E1 negative becomes load-bearing under this framing: the Δ≤0 table bounds what context buys;
the collapse-rung spike ties context-fragility to the main-study construct; the gate failure prices
the agentic paradigm at this scale; the perf tie-in shows the edge could not afford context's
latency/memory bill even if it helped.

## For the supervisor meeting (with the E2 note)
1. Does this boundary framing match their reading of the E1 evidence?
2. E2: one arm or straight to write-up? (Our ranking: imatrix > dense retrieval > placement;
   score-gating dropped on Tier-1 evidence.)
3. Future-work naming: docs-necessary benchmark; tool-finetuned small model; 7–8B consumer-tier gate.
