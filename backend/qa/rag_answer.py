# Answers a question using RAG: retrieves the most relevant chunks, then asks Claude with only that context.

import chromadb
import sys


sys.path.append("backend/vectorstore")
from store_chunks import store_chunks
from retrieve import retrieve_chunks

import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def rag_answer(question, collection):
    """Retrieves relevant chunks for the question and asks Claude to answer using only that context."""
    # Retrieve relevant chunks from the collection based on the question
    retrieved_chunks = retrieve_chunks(question, collection, k=3)

    # Joins chunks into one context string to be used as one input for the llm
    context = "\n\n".join(retrieved_chunks)

    # Use the context and question to generate an answer using the LLM
    message = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=200,
    system="You are a legal document assistant. Answer only using the document text provided. If the answer is not in the document, say so clearly do not guess or invent and answer.",
    messages=[
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
    ]
)
    return message.content[0].text


if __name__ == "__main__":
    import sys
    sys.path.append("backend/parsing")
    from extract_text import extract_text, find_repeated_lines, remove_repeated_lines, chunk_text

    text, pages = extract_text(r"C:\Users\BRUKER\legal-doc-explainer\backend\data\sample_docs\Los_tacos_contract.pdf")
    repeated = find_repeated_lines(pages)
    cleaned_text = remove_repeated_lines(text, repeated)
    
    from embed_chunks import embed_chunks
    chunks = chunk_text(cleaned_text, chunk_size=100, overlap=20)
    vectors = embed_chunks(chunks)

    stored = store_chunks(chunks, vectors) 

    answer = rag_answer("What is the notice period during the probationary period?", stored)
    print(answer)