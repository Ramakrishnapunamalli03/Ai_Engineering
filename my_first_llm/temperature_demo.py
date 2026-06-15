"""
Run this to see how temperature affects output.
Try changing the temperature to see the difference.
"""
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",  # Ollama's OpenAI-compatible endpoint
    api_key="ollama-local",                # Required by SDK but unused
)

def ask_with_temperature(prompt: str, temp: float) -> str:
    response = client.chat.completions.create(
        model="phi3",
        messages=[{"role": "user", "content": prompt}],
        temperature=temp,
        max_tokens=100,
    )
    return response.choices[0].message.content

prompt = "Give me a name for a coffee shop"

# Run 3 times at temperature 0 — you'll get the SAME answer
print("=== Temperature 0 (deterministic) ===")
for i in range(3):
    print(f"  Run {i+1}: {ask_with_temperature(prompt, 0.0)}")

# Run 3 times at temperature 1.2 — you'll get DIFFERENT answers
print("\n=== Temperature 1.2 (creative) ===")
for i in range(3):
    print(f"  Run {i+1}: {ask_with_temperature(prompt, 1.2)}")