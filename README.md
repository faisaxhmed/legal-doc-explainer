# Legal Document Explainer

A web app where you upload a legal document — tenancy agreement, employment contract, T&Cs — and chat with it in plain English. It explains the jargon, answers questions grounded in the actual text, and flags anything unusual or one-sided.

## Problem

Almost everyone has signed a legal document they didn't fully understand. Legal jargon is deliberately dense and lawyers are expensive. This gives anyone a way to understand what they're agreeing to before they sign.

**Disclaimer to bake into the product itself:** this is not a lawyer and answers should be verified. State this clearly in the UI, not just in this README.

## Features

- [ ] PDF upload
- [ ] Chat Q&A grounded in the document (no answers outside the document's content)
- [ ] **Citation grounding** — every answer shows the exact clause and page it came from
- [ ] **Structured summary** — key obligations, deadlines, financial terms, broken out (not just a chat transcript)
- [ ] **Risk/clause flagging** — surfaces unusual terms: early termination penalties, automatic renewals, one-sided indemnity, etc.
- [ ] **Architecture evaluation** (see below) — this is the single most important feature for portfolio credibility. Don't skip it.
- [ ] Clean, simple UI

## Tech Stack

| Layer | Tech |
|---|---|
| Frontend | React |
| Backend | FastAPI (Python) |
| AI | Claude API |
| Embeddings | HuggingFace sentence-transformers |
| Vector DB | Chroma (local) or Pinecone |
| PDF parsing | PyMuPDF or pdfplumber |
| Hosting | Vercel (frontend) + Render (backend) |

## Architecture

### Core pipeline (RAG)

1. User uploads a PDF
2. Backend parses the PDF into raw text
3. Text is split into chunks (e.g. 500 tokens, with overlap)
4. Each chunk is embedded into a vector
5. Embeddings stored in the vector DB
6. User question is embedded
7. Most relevant chunks retrieved
8. Retrieved chunks + question sent to Claude
9. Claude answers grounded only in retrieved content
10. Answer displayed with citation to source clause/page

### Architecture evaluation — full-context vs. RAG

For a single short document (most leases, employment contracts, T&Cs), the whole text often fits inside a model's context window — meaning chunking and retrieval may be unnecessary complexity, not a requirement. RAG earns its place when a document exceeds the context window or you're retrieving across multiple documents, not by default.

Build and run **both** of the following on the same set of test questions, against the same documents:

- **Baseline A:** full document text pasted directly into context → Q&A
- **Baseline B:** chunking + embedding + retrieval → Q&A

Compare:
- Accuracy (does it answer correctly?)
- Hallucination rate (does it ever invent terms not in the document?)
- Latency
- Cost per query

Document the result (even if it's "RAG didn't help here, and here's why"). This single comparison is what turns this from "I built a RAG tutorial" into "I evaluated an architecture decision" — it's the strongest differentiator for a portfolio audience.

## Build order

1. PDF parsing — extract clean text from a real tenancy agreement
2. Chunking — experiment with chunk size and overlap
3. Chroma set up locally — store and retrieve chunks
4. Claude API connected — basic Q&A working in terminal first
5. Full-context baseline built (Baseline A above) — do this before assuming RAG is needed
6. FastAPI backend wrapping the pipeline
7. React frontend — PDF upload + chat interface
8. Citation grounding added
9. Structured summary feature added
10. Risk/clause flagging added
11. Baseline A vs B comparison run and documented
12. Deploy backend (Render) + frontend (Vercel)
13. Test with real documents (tenancy agreement, employment contract, T&Cs)
14. Record demo video

## Limitations to state explicitly in the product

- Not legal advice — informational only, verify with a professional
- Output quality depends on document quality (scanned/low-quality PDFs will perform worse without OCR)
- Grounded in the uploaded document only — no external legal knowledge applied

## Stretch goals

- Highlight the exact clause in the rendered PDF that an answer came from
- Side-by-side view: document on the left, chat on the right

## Status

_Update this section as you go — it's your single source of truth for "where the build is."_

- Current phase: not started
- Last completed step: —
- Next step: —
- Known issues: —
