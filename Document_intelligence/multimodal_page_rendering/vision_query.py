"""
Pass one page image to GPT-4o and ask a question.
Run: python vision_query.py deck.pdf 7 "What does the chart on this page show?"
"""
import sys
from openai import OpenAI
from render_pages import render_pages

client = OpenAI()

def ask_about_page(pdf_path: str, page_index: int, question: str) -> str:
    pages_b64 = render_pages(pdf_path, max_pages=page_index + 1)
    image_b64 = pages_b64[page_index]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": question},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}},
            ],
        }],
        temperature=0.0,
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    pdf, page_idx, question = sys.argv[1], int(sys.argv[2]), " ".join(sys.argv[3:])
    print(ask_about_page(pdf, page_idx, question))