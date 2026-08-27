# Temporary test script: checks whether rag_answer's current max_tokens=200
# is truncating answers to synthesis questions, by comparing it against
# max_tokens=500. Does NOT modify rag_answer.py — reimplements the same
# call locally with a configurable max_tokens instead.

import os
import sys

sys.path.append("backend/qa")
sys.path.append("backend/vectorstore")
sys.path.append("backend/parsing")
sys.path.append("backend/embeddings")

from retrieve import retrieve_chunks
from store_chunks import store_chunks
from extract_text import extract_text, find_repeated_lines, remove_repeated_lines, chunk_text
from embed_chunks import embed_chunks

from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# The value currently hardcoded in rag_answer.py's client.messages.create call.
ORIGINAL_MAX_TOKENS = 200

QUESTION = "What happens to Lessee's obligations if a Change of Control occurs?"
K = 10


def rag_answer_with_max_tokens(question, collection, k, max_tokens):
    """Local stand-in for rag_answer, with max_tokens exposed as a parameter."""
    retrieved_chunks = retrieve_chunks(question, collection, k=k)
    context = "\n\n".join(retrieved_chunks)

    message = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=max_tokens,
        system="You are a legal document assistant. Answer only using the document text provided. If the answer is not in the document, say so clearly do not guess or invent and answer.",
        messages=[
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
    )
    answer = message.content[0].text
    truncated = message.stop_reason == "max_tokens"
    return answer, truncated


def looks_complete(answer):
    """Heuristic: does the answer end with sentence-ending punctuation?"""
    return answer.rstrip().endswith((".", "!", "?", '"', "'"))


if __name__ == "__main__":
    text, pages = extract_text(r"C:\Users\BRUKER\legal-doc-explainer\backend\data\sample_docs\master_lease_agreement.pdf")
    repeated = find_repeated_lines(pages)
    cleaned_text = remove_repeated_lines(text, repeated)

    chunks = chunk_text(cleaned_text, chunk_size=100, overlap=20)
    vectors = embed_chunks(chunks)
    collection = store_chunks(chunks, vectors)

    print("=" * 100)
    print(f"Question: {QUESTION}")
    print(f"k = {K}")
    print("=" * 100)

    print(f"\n--- max_tokens = {ORIGINAL_MAX_TOKENS} (current default) ---")
    answer_original, truncated_original = rag_answer_with_max_tokens(
        QUESTION, collection, K, ORIGINAL_MAX_TOKENS
    )
    print(f"\nFull answer:\n{answer_original}")

    print(f"\n--- max_tokens = 500 ---")
    answer_500, truncated_500 = rag_answer_with_max_tokens(QUESTION, collection, K, 500)
    print(f"\nFull answer:\n{answer_500}")

    print("\n" + "=" * 100)
    print("TRUNCATION CHECK")
    print("=" * 100)
    print(f"max_tokens={ORIGINAL_MAX_TOKENS}: stop_reason indicates truncation = {truncated_original}; "
          f"ends mid-sentence = {not looks_complete(answer_original)}")
    print(f"max_tokens=500:               stop_reason indicates truncation = {truncated_500}; "
          f"ends mid-sentence = {not looks_complete(answer_500)}")

    if truncated_original and not truncated_500:
        print("\n=> max_tokens=500 completes the answer; the original max_tokens was truncating it.")
    elif truncated_original == truncated_500:
        print("\n=> No difference in truncation between the two max_tokens values for this question.")
    else:
        print("\n=> Unexpected result — inspect stop_reason / answers above manually.")
