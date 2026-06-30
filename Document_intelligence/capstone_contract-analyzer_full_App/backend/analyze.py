import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def _context(pages: list, limit: int = 12000) -> str:
    blocks = ["[page " + str(p["page_no"]) + "]\n" + p["text"] for p in pages if p["text"]]
    return "\n\n".join(blocks)[:limit]


def summarize_and_extract(pages: list) -> dict:
    """One structured call -> summary + parties + dates + obligations."""
    prompt = (
        "You are a contract analyst. From the document below, return JSON with keys "
        "summary (string), parties (string[]), key_dates (string[]), obligations (string[]).\n\n"
        + _context(pages)
    )
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0,
    )
    return json.loads(res.choices[0].message.content)


def answer_question(pages: list, question: str) -> dict:
    """Answer using only the document; the model must cite [page N]."""
    prompt = (
        "Answer using ONLY the contract text. Cite the page(s) you used inline as [page N]. "
        "If the answer is not present, say so.\n\n"
        "Question: " + question + "\n\n" + _context(pages)
    )
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return {"answer": res.choices[0].message.content}