"""
Stream from your local Ollama daemon — exactly the same SDK pattern as OpenAI.
Run: python ollama_stream.py
"""
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",  # Ollama's OpenAI-compatible endpoint
    api_key="ollama-local",                # Required by SDK but unused
)

stream = client.chat.completions.create(
    model="llama3.1",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a haiku about local inference."},
    ],
    stream=True,
)

for chunk in stream:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
print()