from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv("../.env")

print(os.getenv("GROQ_API_KEY"))
# Same SDK, two changes: base_url + api key
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY"),
)

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",   # Open-weight model on Groq's hardware
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain what an API is in one sentence."},
    ],
    temperature=0.7,
)

print(response.choices[0].message.content)
print(f"Tokens: {response.usage.total_tokens}")