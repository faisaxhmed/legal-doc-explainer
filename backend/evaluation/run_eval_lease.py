# Runs both answering methods against the lease agreement and prints the results for comparison.

import time
import sys

sys.path.append("backend/qa")
sys.path.append("backend/vectorstore")
sys.path.append("backend/parsing")
sys.path.append("backend/embeddings")

from rag_answer import rag_answer
from answer_question import answer_question
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

if __name__ == "__main__":
    text, pages = extract_text(r"C:\Users\BRUKER\legal-doc-explainer\backend\data\sample_docs\master_lease_agreement.pdf")
    repeated = find_repeated_lines(pages)
    cleaned_text = remove_repeated_lines(text, repeated)

    chunks = chunk_text(cleaned_text, chunk_size=100, overlap=20)
    print(f"Total chunk count: {len(chunks)}")
    vectors = embed_chunks(chunks)
    collection = store_chunks(chunks, vectors)

    results_a = []
    for item in test_questions:
        start = time.time()
        answer = answer_question(cleaned_text, item["question"])
        end = time.time()
        results_a.append({
            "question": item["question"],
            "category": item["category"],
            "expected": item["expected"],
            "answer": answer,
            "latency": end - start
        })

    results_b = []
    for item in test_questions:
        start = time.time()
        answer = rag_answer(item["question"], collection)
        end = time.time()
        results_b.append({
            "question": item["question"],
            "category": item["category"],
            "expected": item["expected"],
            "answer": answer,
            "latency": end - start
        })

    for r in results_a:
        print(f"[A] {r['category']} | {r['latency']:.2f}s | {r['answer'][:100]}")

    for r in results_b:
        print(f"[B] {r['category']} | {r['latency']:.2f}s | {r['answer'][:100]}")

    print("\n" + "=" * 80)
    print("SYNTHESIS QUESTIONS — FULL ANSWERS (side by side)")
    print("=" * 80)
    for r in results_a:
        if r["category"] == "synthesis":
            print(f"\n[A - Baseline A] Question: {r['question']}")
            print(f"Answer:\n{r['answer']}")
    for r in results_b:
        if r["category"] == "synthesis":
            print(f"\n[B - Baseline B] Question: {r['question']}")
            print(f"Answer:\n{r['answer']}")
