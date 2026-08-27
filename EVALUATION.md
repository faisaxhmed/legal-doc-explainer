# Architecture Evaluation: Full-Context vs. RAG

## Key finding

Full-context and RAG performed similarly on a short document, but fixed-k=3 retrieval became less reliable on a longer, denser one. Follow-up testing showed the failures were not one problem: one was caused by retrieval depth, one by an output-token configuration bug in the test harness itself, and one by retrieval relevance. This led to a precise engineering decision: use full-context when a document comfortably fits the context window, and reserve RAG for cases where retrieval is actually necessary — a decision based on tested configurations, not a general claim that one architecture beats the other.

## Why this evaluation exists

For a single short legal document (a lease, an employment contract, a T&Cs page), the entire text often fits inside a modern LLM's context window. That raises a real question: does adding a retrieval-augmented generation (RAG) pipeline — chunking, embedding, vector search — actually improve anything for documents this size, or is it complexity added by default because "RAG" is the expected pattern?

This document compares two architectures head-to-head, across two documents of very different length and density, using the same grounding rules, and reports what happened.

## Setup

- **Baseline A (full-context):** entire cleaned document text sent to Claude on every query, no chunking or retrieval
- **Baseline B (RAG):** document embedded with `sentence-transformers` (`all-MiniLM-L6-v2`), stored in a local Chroma vector DB, top-k chunks retrieved per query and sent to Claude (k=3 unless noted)
- **Grounding:** identical system prompt on both baselines — answer only from the provided text, explicitly refuse rather than guess if the answer isn't present

Two documents were tested:

1. **Short document** — a real employment contract (Los Tacos AS), ~22 chunks. 9 fixed questions: 4 factual, 3 out-of-document, 2 synthesis.
2. **Long, dense document** — a real SEC-filed Master Lease Agreement, 31 pages, 257 chunks. 7 fixed questions, same three categories, written around the lease's actual clauses (Early Buyout, Purchase Option, Renewal, Change of Control).

Test questions were written before running either baseline in both cases.

## Question-level results

| Document | Architecture | Factual | Out-of-document | Synthesis |
|---|---|---:|---:|---:|
| Short (22 chunks) | Full-context | 4/4 | 3/3 | 2/2 |
| Short (22 chunks) | RAG (k=3) | 4/4 | 3/3 | 2/2 |
| Long (257 chunks) | Full-context | 3/3 | 2/2 | 2/2 |
| Long (257 chunks) | RAG (k=3) | 2/3 | 2/2 | 0/2* |

*Reclassified after follow-up investigation — see below. One of these two failures was an output-token configuration bug, not a genuine synthesis failure.

No hallucinations were observed on either baseline, on either document.

### Short document

Both baselines answered every factual and out-of-document question correctly. On the two synthesis questions, the baselines surfaced different but individually accurate slices of the same information — on one, RAG's retrieval actually landed more precisely on the specific clause asked about than full-context did. At this scale, the two architectures were effectively equivalent.

Latency: RAG was consistently faster on factual questions (~1.3–2.6s vs. ~2.7–3.6s for full-context), since it sends far fewer tokens per query. The gap narrowed on synthesis questions, where reasoning cost dominates.

### Long document

This is where a real accuracy gap appeared. RAG (k=3) missed a factual detail present in the document (the 75% Early Buyout Option percentage) and gave incomplete answers to both synthesis questions. Full-context found everything without difficulty.

## Follow-up: decomposing the failures

Re-running the three failing questions at k=3, 5, and 10, and inspecting the retrieved chunks directly, showed the original single-cause explanation ("k=3 was too small") was incomplete. The three failures had three different causes:

| Question | Result at higher k | Actual cause |
|---|---|---|
| Early Buyout Option percentage | **Fixed at k=10** | **Retrieval-depth failure.** The evidence existed and embedding search could find it; k=3 simply wasn't deep enough. |
| Change of Control obligations | Correct chunks retrieved at k=5 and k=10, but the answer still cut off mid-sentence | **Output-token truncation in the test harness.** `rag_answer.py`'s `max_tokens=200` was cutting the response short. Confirmed directly via the API's `stop_reason` field (`max_tokens` at 200, not at 500, same question and context). The model was generating a correct answer and simply hit the output limit. |
| End-of-Base-Term options | Still incomplete at k=10 — two of three relevant sections never appeared in the top 10 retrieved chunks | **Retrieval-relevance failure.** The correct sections remained outside the top-10 results by embedding similarity, despite being necessary to answer the question — not resolved by raising the cutoff from 3 to 10. Whether a much larger k would resolve it wasn't tested. |

One practical implication: the original evaluation's synthesis results were partly measuring a bug in the test harness, not purely an architectural limitation of RAG. That's corrected here rather than left in the reported results. The persistent retrieval-relevance failure motivates re-ranking as a next intervention worth testing — a hypothesis, not a confirmed fix, since re-ranking wasn't implemented or tested in this evaluation.

## Conclusion and recommendation

For the documents and configurations tested, full-context was the more reliable approach whenever the document fit within the model's context window. RAG offered lower latency on straightforward factual queries, but the tested retrieval configuration introduced failure modes that full-context avoided.

Based on these experiments, the current implementation routes documents that fit comfortably within the context window through full-context Q&A, and reserves RAG for documents that exceed that limit, or future multi-document search. This is an engineering decision grounded in the tested configurations — not a general claim that full-context is always superior to RAG.

## What I'd investigate next

1. **Better retrieval** — re-ranking and adaptive k, motivated by the retrieval-relevance failure that persisted even at k=10.
2. **Larger evaluation** — more documents and a wider range of question types, to move from directional evidence toward a more reliable benchmark.
3. **Production evaluation** — exact token/cost measurement per query, and monitoring in a live system to keep tuning retrieval parameters over time rather than treating this as a one-time exercise.

## Limitations

- Two documents tested, not a large corpus; results are directional evidence, not a statistically robust benchmark
- Small question sets (9 and 7); a larger set would give more reliable category-level conclusions
- The main evaluation used k=3; follow-up testing examined k=3, 5, and 10 on the Document 2 failure cases only, not across the full question set or additional documents
- Output wording varies run-to-run (LLM outputs aren't fully deterministic), so conclusions rest on patterns rather than any single run's exact phrasing
- Cost was reasoned about structurally rather than measured with exact token counts per query
- One original result was reclassified after discovering an output-token configuration issue in the test harness itself — a reminder that an evaluation harness needs to be checked as carefully as the systems it's testing