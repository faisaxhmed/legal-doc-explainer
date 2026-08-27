# Quick manual check that the Anthropic API key and connection work.

print("script is running")

import os
from dotenv import load_dotenv
from anthropic import Anthropic

# reads .env and loads the environment variables
load_dotenv()

# Get the API key from the environment variable
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Test the connection by sending a simple message to the API
message = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=200,
    system="You are a legal document assistant. Answer only using the document text provided. If the answer is not in the document, say so clearly do not guess or invent and answer.",
    messages=[
        {"role": "user", "content": f"Document:\n{document_text}\n\nQuestion: {question}"},
    ]
)

