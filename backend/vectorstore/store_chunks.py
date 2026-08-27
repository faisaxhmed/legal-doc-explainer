# Stores text chunks and their vectors in a Chromadb collection for later retrieval.

import chromadb

def store_chunks(chunks, vectors):
    "Create a Chromadb collection and store the chunks and their corresponding vectors."
    client = chromadb.Client()
    collection = client.create_collection("chunks")

    collection.add(
    documents=chunks, # The actual chunk text
    embeddings=vectors.tolist(), # the vectors you already made — .tolist() converts from NumPy array to plain list, which Chroma expects
    ids=[str(i) for i in range(len(chunks))]   # a unique ID per chunk — Chroma requires one, just "0", "1", "2"...
)

    return collection





if __name__ == "__main__":
    import sys
    sys.path.append("backend/parsing")
    sys.path.append("backend/embeddings")

    from extract_text import extract_text,find_repeated_lines, remove_repeated_lines, chunk_text

    text, pages = extract_text(r"C:\Users\BRUKER\legal-doc-explainer\backend\data\sample_docs\Los_tacos_contract.pdf")
    repeated = find_repeated_lines(pages)
    cleaned_text = remove_repeated_lines(text, repeated)

    from embed_chunks import embed_chunks
    chunks = chunk_text(cleaned_text, chunk_size=100, overlap=20)
    vectors = embed_chunks(chunks)

    stored = store_chunks(chunks, vectors) 

    print(stored.count())