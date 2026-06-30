"""Ingest a folder into Chroma: chunk by line-window, embed, store file/line metadata."""
import os
from openai import OpenAI
import chromadb

client = OpenAI()
chroma = chromadb.PersistentClient(path="./chroma")
EMBED_MODEL = "text-embedding-3-small"
CHUNK_LINES = 40
EXTS = {".py", ".js", ".ts", ".tsx", ".md", ".txt", ".java", ".go", ".rs"}


def _embed(texts: list) -> list:
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [d.embedding for d in resp.data]


def _chunks(path: str):
    with open(path, encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    for start in range(0, len(lines), CHUNK_LINES):
        window = lines[start:start + CHUNK_LINES]
        text = "".join(window).strip()
        if text:
            yield {"text": text, "file_path": path,
                   "start_line": start + 1, "end_line": start + len(window)}


def ingest(folder: str, collection_name: str = "docs") -> int:
    coll = chroma.get_or_create_collection(collection_name)
    ids, docs, metas = [], [], []
    for root, _, files in os.walk(folder):
        for name in files:
            if os.path.splitext(name)[1] not in EXTS:
                continue
            path = os.path.join(root, name)
            for ch in _chunks(path):
                ids.append(ch["file_path"] + ":" + str(ch["start_line"]))
                docs.append(ch["text"])
                metas.append({"file_path": ch["file_path"],
                              "start_line": ch["start_line"], "end_line": ch["end_line"]})
    # Embed + upsert in batches (upsert makes re-ingest idempotent).
    for i in range(0, len(docs), 100):
        coll.upsert(ids=ids[i:i + 100], documents=docs[i:i + 100],
                    embeddings=_embed(docs[i:i + 100]), metadatas=metas[i:i + 100])
    return len(docs)