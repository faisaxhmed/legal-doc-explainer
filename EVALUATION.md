# Architecture Evaluation: Full-Context vs. RAG

## Why this evaluation exists

For a single short legal document (a lease, an employment contract, a T&Cs page), the entire text often fits inside a modern LLM's context window. That raises a real question: does adding a retrieval-augmented generation (RAG) pipeline — chunking, embedding, vector search — actually improve anything for documents this size, or is it complexity added by default because "RAG" is the expected pattern?

This document compares two architectures head-to-head, across two documents of very different length and density, using the same grounding rules, and reports what actually happened rather than assuming an answer going in.

## Setup

- **Baseline A (full-context):** entire cleaned document text sent to Claude on every query, no chunking or retrieval
- **Baseline B (RAG):** document embedded with `sentence-transformers` (`all-MiniLM-L6-v2`), stored in a local Chroma vector DB, top-3 chunks retrieved per query and sent to Claude
- **Grounding:** identical system prompt on both baselines — answer only from the provided text, explicitly refuse rather than guess if the answer isn't present

Two documents were tested:

1. **Short document** — a real employment contract (Los Tacos AS), ~22 chunks at 100 words/20-word overlap. 9 fixed questions: 4 factual, 3 out-of-document, 2 synthesis.
2. **Long, dense document** — a real SEC-filed Master Lease Agreement (Caterpillar Financial Services / CDM Resource Management), 31 pages, **257 chunks** — roughly 12x the chunk count of the first document. 7 fixed questions, same three categories, written specifically around the lease's actual clauses (Early Buyout, Purchase Option, Renewal, Change of Control).

Test questions were written before running either baseline in both cases, to avoid unconsciously favoring one architecture's output while designing the test.

## Results — Document 1 (short, 22 chunks)

### Accuracy

| Category | Baseline A | Baseline B |
|---|---|---|
| Factual (4 questions) | 4/4 correct | 4/4 correct |
| Out-of-document (3 questions) | 3/3 correctly refused | 3/3 correctly refused |
| Synthesis (2 questions) | Both answered, information-complete | Both answered, information-complete but different emphasis |

No hallucinations observed on either baseline. Both correctly distinguished between related-but-distinct concepts (e.g. a non-compete clause vs. the NDA clause that was actually present) rather than conflating them.

On the synthesis questions, the two baselines surfaced **different but individually accurate slices** of the same information — neither was wrong, each reflected what its architecture had access to. On one synthesis question, Baseline B's retrieval actually landed *more precisely* on the specific clause the question asked about than Baseline A did. On a short, low-complexity document, the two architectures were essentially accuracy-equivalent.

### Latency

Baseline B was consistently faster on factual questions (~1.3-2.6s vs. ~2.7-3.6s for Baseline A), since B sends only ~3 retrieved chunks per query rather than the whole document. The gap narrowed on synthesis questions, where reasoning cost dominates over context size.

## Results — Document 2 (long, dense, 257 chunks)

This is where a real, unambiguous accuracy gap appeared for the first time in the evaluation.

### Accuracy

| Category | Baseline A | Baseline B |
|---|---|---|
| Factual (3 questions) | 3/3 correct | **2/3 correct** - missed the 75% Early Buyout Option percentage entirely, stating it "does not specify a percentage" when the document does |
| Out-of-document (2 questions) | 2/2 correctly refused | 2/2 correctly refused |
| Synthesis (2 questions) | Both answers information-complete, correctly cited relevant sections | **Both answers incomplete** - one was explicitly self-reported as "cut off"; the other surfaced only 1 of 3 relevant sections (Purchase Option) and missed Early Buyout and Renewal entirely |

**This is a genuine retrieval failure, not a close call.** Baseline B's fixed top-3 retrieval simply did not include chunks containing information that was present in the document and that Baseline A found without difficulty.

## Why the result changed between documents

The mechanism is straightforward: **retrieval quality is a function of `k` (chunks retrieved) relative to how much of the document is actually relevant to a given question, not an inherent property of RAG as an architecture.** On the 22-chunk document, top-3 retrieval reliably covered what mattered. On the 257-chunk document, the same fixed k=3 became insufficient once relevant information was spread across more sections than the retrieval step returned.

Full-context has no equivalent failure mode within the context window's limits - it doesn't need to guess how many chunks are "enough," because it doesn't chunk at all.

## Conclusion and recommendation

**For this project's realistic document sizes, full-context should be the default architecture**, not a coin-flip between two equivalent options. The reasoning:

- Both documents tested - including a 257-chunk, 31-page document - still fit comfortably within Claude's actual context window. The 257-chunk document was not "too large for full-context"; it was large enough to expose that RAG's fixed retrieval size was under-tuned for it.
- Full-context produced zero missed facts and zero incomplete synthesis answers across both documents tested. RAG matched it on the short document and measurably underperformed it on the long one.
- The failure mode found is fixable (dynamic `k`, re-ranking, wider chunk overlap - see Future Work below), but fixing it is additional engineering work that full-context simply doesn't require for documents that fit in context.

**Practical routing rule going forward:** default to full-context for any document that fits in the context window (the large majority of real single-document legal uploads, based on both test cases here). Reserve RAG for genuinely oversized documents or, in the future, cross-document search across multiple uploaded files - not as the default path for a single document, however long, as long as it still fits.

## Future Work

If this became a real product rather than a portfolio evaluation, the RAG failure mode found here would be worth fixing properly rather than avoided by defaulting away from it, since real users will eventually upload something too large even for full-context. Concrete next steps, in rough priority order:

1. **Dynamic `k`** - scale the number of retrieved chunks with document size/total chunk count, rather than a fixed value that works for a 22-chunk document and fails a 257-chunk one.
2. **Re-ranking** - retrieve a wider initial candidate set (e.g. top-15) via cheap embedding search, then use a more accurate second pass (a cross-encoder, or Claude itself) to re-rank and select the final top chunks - catches cases where the correct chunk wasn't in the initial shortlist.
3. **Neighbor-chunk retrieval** - return each matched chunk together with its immediate neighbors, so a fact split across a chunk boundary isn't lost.
4. **Query expansion** - for legal documents specifically, the same clause is often referenced by both section number and description; embedding multiple phrasings of the question (or having Claude rephrase it first) would catch more of this.
5. **Answer verification pass** - before returning a numeric fact (a percentage, a date, a dollar figure), verify the cited section actually contains that value, catching retrieval misses before they reach the user.
6. **Production monitoring** - track which questions produce "not found" or hedged answers unexpectedly, and use that signal to keep tuning retrieval parameters over time, rather than treating this evaluation as a one-time exercise.

## Limitations of this evaluation

- Two documents tested, not a large corpus; results are directional evidence, not a statistically robust benchmark
- Small test sets (9 and 7 questions); a larger set per document would give more reliable category-level conclusions
- Output wording varies run-to-run (LLM outputs are not fully deterministic), so conclusions rest on patterns observed across runs rather than any single run's exact phrasing
- Cost was reasoned about structurally rather than measured with exact token counts per query
- Only one value of `k` (3) was tested for RAG; the Future Work section above outlines the tuning this evaluation didn't attempt
