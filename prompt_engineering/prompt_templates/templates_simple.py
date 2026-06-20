"""
Simple prompt templates using Python f-strings.
Good for small projects. Run: python templates_simple.py
"""


from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)
def summarize(text: str, style: str = "bullet points", max_words: int = 100) -> str:
    """Reusable summarization template."""
    prompt = f"""Summarize the following text in {style} format.
Keep it under {max_words} words. Focus on actionable insights.

Text:
\"\"\"
{text}
\"\"\"
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a concise technical writer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content

# Usage — same template, different inputs
article = """
Artificial intelligence is transforming industries by automating repetitive tasks,
improving decision-making through data analysis, and enabling new products and services.
Companies investing in AI are seeing productivity gains, but successful adoption
requires employee training and strong data governance.
"""

result1 = summarize(article, style="3 bullet points", max_words=50)
print(result1)
result2 = summarize("Long article about AI...", style="3 bullet points", max_words=50)
print(result2)