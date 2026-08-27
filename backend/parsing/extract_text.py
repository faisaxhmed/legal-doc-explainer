# Extract text from a PDF file

# PyMuPDF library is used to extract text from PDF files
from unittest import result

import fitz 


def extract_text(pdf_path):
    """Extracts and returns the full text and a list of per-page text from a PDF."""
    doc = fitz.open(pdf_path)
    text = "" 
    pages = []
    
    for page in doc:
        page_text = page.get_text()
        text = text + page_text + "\n"
        pages.append(page_text)

    doc.close()
    return text, pages

    
def find_repeated_lines(pages):
    """Returns the set of normalized lines that repeat across a majority of pages (likely headers/footers)."""
    counts = {}

    for page in pages:
        unique_lines = {line.strip().lower() for line in page.split("\n")}
        for line in unique_lines:
            if line in counts:
                counts[line] = counts[line] + 1
            else:
                counts[line] = 1
    return {line for line in counts if counts[line] > len(pages) / 2}

def remove_repeated_lines(text, repeated_lines):
    """Removes any line matching repeated_lines from text and returns the cleaned result."""
    repeated_lines = set(repeated_lines)

    lines = text.split("\n")
    filtered_lines = [line for line in lines if line.strip().lower() not in repeated_lines]
    cleaned =  "\n".join(filtered_lines)

    return cleaned

def chunk_text(text, chunk_size, overlap):
    """Splits text into chunks of chunk_size with overlap between chunks."""
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = words[start:end]
        chunks.append(" ".join(chunk))

        start = end - overlap  # Move back by overlap for the next chunk

    return chunks



if __name__ == "__main__":   
    text, pages = extract_text(r"C:\Users\BRUKER\legal-doc-explainer\backend\data\sample_docs\master_lease_agreement.pdf")
    print(len(pages))
    print(text[:1000])
    
   
    
    