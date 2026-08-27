# Legal Document Explainer
 
A backend system that lets you upload a legal document — tenancy agreement, employment contract, T&Cs — and ask questions about it in plain English, grounded strictly in the document's own text, with no legal knowledge outside what's actually written there.
 
This started as a portfolio project with a specific goal: not just to build a RAG pipeline, but to actually test whether RAG was the right architecture for this problem in the first place, rather than assuming it because "RAG" is the expected pattern for document Q&A. That evaluation — not the pipeline itself — is the core result of this project.
 
## Status
 
**Backend complete and evaluated. No frontend yet — a deliberate choice, explained below.**
 
## Key finding
 
Full-context and RAG performed similarly on a short document, but fixed-k=3 retrieval became less reliable on a longer, denser one. Follow-up testing showed the failures weren't one problem: one was caused by retrieval depth, one by an output-token configuration bug in the test harness itself, and one by retrieval relevance. This led to a precise engineering decision: use full-context when a document comfortably fits the context window, and reserve RAG for cases where retrieval is actually necessary — a decision based on tested configurations, not a general claim that one architecture beats the other.
 
Full methodology, both datasets, and the follow-up investigation are in [`EVALUATION.md`](./EVALUATION.md).
 
## The problem
 
Almost everyone has signed a legal document they didn't fully understand. Legal jargon is dense by design, and lawyers are expensive. The goal here is to give anyone a way to understand what they're agreeing to before they sign — grounded in the actual document, not general legal knowledge, and honest about that boundary. This is not a lawyer and every answer should be independently verified.
 
## What's built
 
- **PDF parsing** — extracts clean text from real, messy PDFs, including detecting and stripping repeated headers/footers (with a documented limitation: exact/normalized-match detection only, so a footer repeated in a different language or with genuinely different wording won't be caught)
- **Chunking** — splits cleaned text into overlapping word-based chunks, so a clause split across a chunk boundary still appears whole in at least one chunk
- **Two complete, independently-tested Q&A architectures:**
  - **Baseline A — full-context.** The entire cleaned document is sent to Claude on every question. No chunking, no retrieval, nothing to miss.
  - **Baseline B — RAG.** Chunks are embedded (`sentence-transformers`, `all-MiniLM-L6-v2`), stored in a local Chroma vector database, and the top-k most relevant chunks are retrieved per question and sent to Claude.
- **Grounding** — both architectures use the same system prompt: answer only from the provided text, and explicitly refuse rather than guess if the answer isn't present.
## The evaluation — the actual point of this project
 
Rather than picking one architecture and shipping it, both were built, then compared head-to-head on the same real documents, the same fixed test questions (written before running either baseline, to avoid unconsciously favoring one), and the same grounding rules.
 
**Two documents were tested:**
1. A short, real employment contract (~22 chunks)
2. A long, dense, real SEC-filed commercial lease agreement (31 pages, 257 chunks)
On the short document, the two architectures were essentially accuracy-equivalent — no hallucinations on either, correct refusals on out-of-document questions, and even a case where RAG's retrieval landed *more precisely* on the specific clause a question asked about than full-context did.
 
On the long, dense document, a real accuracy gap appeared. A follow-up investigation — re-running the failing questions at k=3, 5, and 10, and inspecting the retrieved chunks directly — found this wasn't one problem. It was three, at three different layers of the pipeline: a retrieval-depth failure (fixed by increasing k), an output-token truncation bug in the evaluation harness itself (not an architecture problem at all), and a genuine retrieval-relevance failure that persisted even at k=10. Separating these mattered, because one turned out to be a bug in the test setup, not evidence against RAG.
 
**The resulting recommendation:** for the configurations tested, full-context was the more reliable approach when the document fit comfortably within the model's context window. Reserve RAG for documents that genuinely exceed the context window, or future multi-document search — not as the default path for a single document that still fits, and not as a general claim that RAG is worse than full-context in every configuration.
 
## Why there's no frontend yet
 
This is a deliberate sequencing decision, not an unfinished corner. Building a full product on top of an unvalidated architecture choice would have meant building UI on a foundation I hadn't actually tested — exactly the trap this project's evaluation phase exists to avoid.
 
So the backend came first, and it's now genuinely validated: two real architectures, tested on real documents, with a documented, evidence-based decision — including a self-correction when a follow-up investigation revealed part of the original evaluation had been measuring a bug in the test harness rather than a real architectural limitation. The frontend is being built next, on a related project reusing this same pipeline, aimed at getting real users first — see [What's next](#whats-next).
 
## Tech stack
 
| Layer | Tech |
|---|---|
| PDF parsing | PyMuPDF |
| Chunking | Custom word-based chunking with overlap |
| Embeddings | HuggingFace `sentence-transformers` (`all-MiniLM-L6-v2`) |
| Vector DB | Chroma (local) |
| Generation | Claude API (Anthropic) |
| Evaluation | Custom fixed-question test harness, two real documents, follow-up k-sweep |
 
## Repo structure
 
```
backend/
  parsing/          PDF extraction, footer/header cleaning, chunking
  embeddings/        Chunk embedding
  vectorstore/        Chroma storage and retrieval
  qa/                 Baseline A (full-context) and Baseline B (RAG) Q&A
  evaluation/          Fixed-question evaluation scripts, k-sweep, truncation check
  data/sample_docs/    Test documents (one included is a public SEC filing; a private test document is excluded from version control)
EVALUATION.md          Full evaluation writeup: methodology, both datasets, follow-up investigation, recommendation, next steps
```
 
## Limitations, stated plainly
 
- Not legal advice — informational only, always verify with a professional
- Output quality depends on document quality (scanned/low-quality PDFs will perform worse without OCR, which isn't implemented)
- Grounded only in the uploaded document — no external legal knowledge is applied
- Header/footer detection only catches exact or near-exact repeats — a genuinely different-language duplicate footer won't be caught
- The evaluation covers two documents and a small question set — directional evidence, not a statistically robust benchmark. Full details, including what wasn't tested, are in `EVALUATION.md`
  
## What's next
 
- A student-facing PDF teach/quiz tool, reusing this pipeline, built with a real UI and aimed at real users
- Eventually, pointing that same UI at this backend as a second mode, once it exists
