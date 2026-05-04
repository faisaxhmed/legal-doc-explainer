# Legal Document Explainer

## What I'm Building
A web app where you upload any legal document — tenancy agreement, employment contract, terms and conditions — and chat with it in plain English. Ask it anything, and it tells you exactly what you're agreeing to, explains the jargon, and flags anything that seems unusual or unfair.

## Problem I'm Solving
Almost everyone has signed a legal document they didn't fully understand. Legal jargon is deliberately complex and lawyers are expensive. This gives anyone the ability to understand what they're signing before they sign it.

## Planned Features
- [ ] Upload a PDF (tenancy agreement, contract, T&Cs etc.)
- [ ] Ask questions in plain English ("Can my landlord enter without notice?")
- [ ] Get accurate answers grounded in the actual document
- [ ] Automatic clause flagging — highlights anything suspicious or unusual
- [ ] Plain English summary of the whole document
- [ ] Clean, simple UI — anyone should be able to use it

## Tech Stack I Plan to Use
| Layer | Tech |
|---|---|
| Frontend | React |
| Backend | FastAPI (Python) |
| AI | Claude API |
| Embeddings | HuggingFace sentence-transformers |
| Vector database | Chroma (local) or Pinecone |
| PDF parsing | PyMuPDF or pdfplumber |
| Hosting | Vercel (frontend) + Render (backend) |

## How It Will Work (RAG Pipeline)
1. User uploads a PDF
2. Backend parses the PDF into raw text
3. Text is split into chunks (e.g. 500 tokens with overlap)
4. Each chunk is converted into an embedding (vector)
5. Embeddings stored in a vector database
6. User asks a question → question is also embedded
7. Most relevant chunks retrieved from the vector DB
8. Retrieved chunks + question sent to Claude API
9. Claude answers based only on the document content
10. Answer displayed in the chat UI

## What I Want to Learn From This
- How RAG (Retrieval Augmented Generation) actually works under the hood
- Embeddings and vector databases — the core of modern AI search
- Chunking strategies and why they matter for answer quality
- Prompt engineering for a specific, high-stakes domain
- Building and deploying a full ML pipeline end to end

## Build Order (Step by Step)
1. Get PDF parsing working — extract clean text from a real tenancy agreement
2. Implement chunking — experiment with chunk size and overlap
3. Set up Chroma locally — store and retrieve chunks
4. Connect Claude API — get a basic Q&A working in the terminal first
5. Build FastAPI backend — wrap the pipeline in an API
6. Build React frontend — PDF upload + chat interface
7. Add clause flagging — prompt Claude to identify unusual terms
8. Add full document summary feature
9. Deploy backend to Render, frontend to Vercel
10. Test with real documents (tenancy agreement, employment contract, T&Cs)
11. Record demo video

## Notes
- Test with genuinely complex documents — the harder the doc, the better the demo
- Be honest about limitations: it's not a lawyer, answers should be verified
- Stretch goal: highlight the exact clause in the PDF that the answer came from
- Stretch goal: side-by-side view (document on left, chat on right)

## Why This Is Impressive
- LegalTech is a massive, well-funded industry
- RAG is the most in-demand AI engineering skill right now
- The problem is universally relatable — everyone has signed something they didn't read
- Shows product thinking (clause flagging) not just technical execution
- A working demo sells itself in 30 seconds
