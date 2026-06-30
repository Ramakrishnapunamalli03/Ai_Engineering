"""Compose an answer with file/line citations from retrieved chunks."""
from openai import OpenAI
from retrieve import search

client = OpenAI()


def ask(question: str, collection_name: str = "docs") -> dict:
    hits = search(question, collection_name)
    if not hits:
        return {"answer": "No documents ingested yet. Run: python cli.py ingest <folder>", "citations": []}

    context = "\n\n".join(
        "[" + h["file_path"] + ":" + str(h["start_line"]) + "-" + str(h["end_line"]) + "]\n" + h["text"]
        for h in hits
    )
    prompt = (
        "Answer the question using only the context. Cite sources inline as "
        "[path:start-end], exactly as labelled.\n\n"
        "Question: " + question + "\n\nContext:\n" + context
    )
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    citations = [{"file_path": h["file_path"], "start_line": h["start_line"], "end_line": h["end_line"]}
                 for h in hits]
    return {"answer": res.choices[0].message.content, "citations": citations}