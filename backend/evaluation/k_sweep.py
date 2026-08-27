# Sweeps k (number of retrieved chunks) over [3, 5, 10] to inspect whether
# retrieval quality — not just the final answer — improves with larger k.
# Focused on debugging the 3 questions that failed at k=3: the Early Buyout
# Option percentage question, and the two synthesis questions.

import sys

sys.path.append("backend/qa")
sys.path.append("backend/vectorstore")
sys.path.append("backend/parsing")
sys.path.append("backend/embeddings")

from rag_answer import rag_answer
from retrieve import retrieve_chunks
from store_chunks import store_chunks
from extract_text import extract_text, find_repeated_lines, remove_repeated_lines, chunk_text
from embed_chunks import embed_chunks

test_questions = [
    {"question": "What is the Base Term length in months?", "category": "factual", "expected": "120 months"},
    {"question": "What percentage of Lessor's Cost must be paid to exercise the Early Buyout Option at the Fifth anniversary?", "category": "factual", "expected": "75%"},
    {"question": "How many days' notice is required to exercise the Renewal Option?", "category": "factual", "expected": "not less than 180, not more than 240 days"},
    {"question": "What is the penalty for late delivery of the Equipment by the Vendor?", "category": "out_of_document", "expected": "not specified (document addresses late rent payments, not late equipment delivery)"},
    {"question": "Does this lease cover real estate rental?", "category": "out_of_document", "expected": "no, this is an equipment lease, not a real estate lease"},
    {"question": "What happens to Lessee's obligations if a Change of Control occurs?", "category": "synthesis", "expected": "spans Section 10.3 (Merger/Change of Control) and cross-references Section 15 (Default)"},
    {"question": "What are Lessee's options at the end of the Base Term, and what does each cost?", "category": "synthesis", "expected": "spans Section 5.1 (Early Buyout), 5.2 (Purchase Option), 5.3 (Renewal) — three separate sections with different percentages and notice periods"},
]

# Questions that failed at k=3 in the original evaluation — call these out
# explicitly in the output so they're easy to find when scanning the sweep.
FOCUS_QUESTIONS = {
    "What percentage of Lessor's Cost must be paid to exercise the Early Buyout Option at the Fifth anniversary?",
    "What happens to Lessee's obligations if a Change of Control occurs?",
    "What are Lessee's options at the end of the Base Term, and what does each cost?",
}

if __name__ == "__main__":
    text, pages = extract_text(r"C:\Users\BRUKER\legal-doc-explainer\backend\data\sample_docs\master_lease_agreement.pdf")
    repeated = find_repeated_lines(pages)
    cleaned_text = remove_repeated_lines(text, repeated)

    chunks = chunk_text(cleaned_text, chunk_size=100, overlap=20)
    print(f"Total chunk count: {len(chunks)}")
    vectors = embed_chunks(chunks)
    collection = store_chunks(chunks, vectors)

    for k in [3, 5, 10]:
        print("\n" + "=" * 100)
        print(f"K = {k}")
        print("=" * 100)

        for item in test_questions:
            question = item["question"]
            flag = "  <<< FOCUS QUESTION (failed at k=3)" if question in FOCUS_QUESTIONS else ""

            retrieved_chunks = retrieve_chunks(question, collection, k=k)
            answer = rag_answer(question, collection, k=k)

            print("\n" + "-" * 100)
            print(f"[k={k}] Category: {item['category']}{flag}")
            print(f"Question: {question}")
            print(f"Expected: {item['expected']}")
            print(f"\nAnswer:\n{answer}")
            print(f"\nRetrieved {len(retrieved_chunks)} chunk(s):")
            for i, chunk in enumerate(retrieved_chunks, start=1):
                print(f"\n  --- Chunk {i} ---")
                print(f"  {chunk}")
