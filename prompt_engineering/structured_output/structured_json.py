"""
OpenAI's JSON mode — guaranteed valid JSON output.
Run: python structured_json.py
"""
import json
from openai import OpenAI

from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    response_format={"type": "json_object"},  # Forces JSON output
    messages=[
        {"role": "system", "content": "Extract entities from the text. Return JSON with keys: entities (list of {name, type, context}), language, word_count"},
        {"role": "user", "content": "Apple CEO Tim Cook announced the iPhone 16 at their Cupertino headquarters in September 2024."}
    ],
    temperature=0.0,
)

data = json.loads(response.choices[0].message.content)
print(json.dumps(data, indent=2))

# Output:
# {
#   "entities": [
#     {"name": "Apple", "type": "company", "context": "technology company"},
#     {"name": "Tim Cook", "type": "person", "context": "CEO of Apple"},
#     {"name": "iPhone 16", "type": "product", "context": "new product announcement"},
#     {"name": "Cupertino", "type": "location", "context": "Apple headquarters"}
#   ],
#   "language": "English",
#   "word_count": 15
# }