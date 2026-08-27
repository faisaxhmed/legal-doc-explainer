# Turns text chunks into embedding vectors using a local sentence-transformer model.

from sentence_transformers import SentenceTransformer


model = SentenceTransformer("all-MiniLM-L6-v2")   # downloads once, then cached locally

def embed_chunks(chunks):
    """Embeds a list of text chunks and returns their vectors."""
    return model.encode(chunks)

if __name__ == "__main__":
    import sys
    sys.path.append("backend/parsing")
    from extract_text import extract_text
    from extract_text import find_repeated_lines, remove_repeated_lines, chunk_text

    text, pages = extract_text(r"C:\Users\BRUKER\legal-doc-explainer\backend\data\sample_docs\Los_tacos_contract.pdf")
    repeated = find_repeated_lines(pages)
    cleaned_text = remove_repeated_lines(text, repeated)
    chunks = chunk_text(cleaned_text, chunk_size=100, overlap=20)
    vectors = embed_chunks(chunks)

    
    print(f"Number of chunks: {len(chunks)}")
    print(f"How many vectors came back: {len(vectors)}")