# Runs both answering methods against the employment contract and prints the results for comparison.

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
    {"question": "What is the notice period during the probationary period?", "category": "factual", "expected": "14 days"},
    {"question": "What is the employee's hourly salary?", "category": "factual", "expected": "NOK 199 per hour"},
    {"question": "What percentage is the employee's position (full-time/part-time)?", "category": "factual", "expected": "25%"},
    {"question": "How long is the trial/probationary period?", "category": "factual", "expected": "6 months"},
    {"question": "What is the penalty for breaking a non-compete clause?", "category": "out_of_document", "expected": "not present"},
    {"question": "How many paid sick days does the employee get per year?", "category": "out_of_document", "expected": "not present"},
    {"question": "What is the employee's annual salary?", "category": "out_of_document", "expected": "not directly stated"},
    {"question": "Summarize the employee's total compensation and benefits package.", "category": "synthesis", "expected": "spans salary (Sec 8), pension/insurance (Sec 9), vacation (Sec 6), and Appendix (pension %, injury insurance, disability coverage)"},
    {"question": "What obligations does the employee have both during and after employment ends?", "category": "synthesis", "expected": "spans NDA (Sec 13), IP rights (Sec 14), and asset return on resignation (Sec 7)"},
]

if __name__ == "__main__":
    text, pages = extract_text(r"C:\Users\BRUKER\legal-doc-explainer\backend\data\sample_docs\Los_tacos_contract.pdf")
    repeated = find_repeated_lines(pages)
    cleaned_text = remove_repeated_lines(text, repeated)

    chunks = chunk_text(cleaned_text, chunk_size=100, overlap=20)
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