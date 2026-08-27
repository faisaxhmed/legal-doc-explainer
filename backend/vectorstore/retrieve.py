# Finds the chunks most relevant to a question by comparing embedding vectors in the collection.

import chromadb
import sys
sys.path.append("backend/embeddings")
sys.path.append("backend/vectorstore")
from store_chunks import store_chunks
from embed_chunks import embed_chunks

def retrieve_chunks(question, collection, k=3):
    """Embeds the question and returns the k closest matching chunks from the collection."""
    question_vector = embed_chunks(question)
    results = collection.query(
    query_embeddings=[question_vector.tolist()], # a list containing one vector
    n_results=k # how many closest chunks to return ("top-k")
)
    return results["documents"][0]


if __name__ == "__main__":
    import sys
    sys.path.append("backend/parsing")

    from extract_text import extract_text,find_repeated_lines, remove_repeated_lines, chunk_text

    text, pages = extract_text(r"C:\Users\BRUKER\legal-doc-explainer\backend\data\sample_docs\Los_tacos_contract.pdf")
    repeated = find_repeated_lines(pages)
    cleaned_text = remove_repeated_lines(text, repeated)

    from embed_chunks import embed_chunks
    chunks = chunk_text(cleaned_text, chunk_size=100, overlap=20)
    vectors = embed_chunks(chunks)
    
    collection = store_chunks(chunks, vectors)   # from Step 2
    results = retrieve_chunks("What is the notice period?", collection, k=3)

    print(results)
