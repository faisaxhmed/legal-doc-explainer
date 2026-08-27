# Answers a question by sending the full document text to Claude in one request (no retrieval).

import os
from dotenv import load_dotenv
from anthropic import Anthropic

# reads .env and loads the environment variables
load_dotenv()

# Get the API key from the environment variable
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def answer_question(document_text, question):
    """Sends the document text and question to Claude and returns the answer text."""

    message = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=200,
    system="You are a legal document assistant. Answer only using the document text provided. If the answer is not in the document, say so clearly do not guess or invent and answer.",
    messages=[
        {"role": "user", "content": f"Document:\n{document_text}\n\nQuestion: {question}"},
    ]
)
    return message.content[0].text

if __name__ == "__main__":
    import sys
    sys.path.append("backend/parsing")
    from extract_text import extract_text
    from extract_text import find_repeated_lines, remove_repeated_lines

    text, pages = extract_text(r"C:\Users\BRUKER\legal-doc-explainer\backend\data\sample_docs\Los_tacos_contract.pdf")
    repeated = find_repeated_lines(pages)
    cleaned_text = remove_repeated_lines(text, repeated)

    answer = answer_question(cleaned_text, "What is the notice period during the probationary period?")
    answer2 = answer_question(cleaned_text, "What is the penalty for breaking a non-compete clause?")
    answer3 = answer_question(cleaned_text, "Summarize the employee's total compensation and benefits in one paragraph.")

    print(answer3)  
    
  