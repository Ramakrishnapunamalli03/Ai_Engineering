"""Hybrid retrieval: dense (Chroma) + sparse (BM25) merged with Reciprocal Rank Fusion."""
import os
from rank_bm25 import BM25Okapi
import chromadb
from openai import OpenAI

client = OpenAI()
chroma = chromadb.PersistentClient(path="./chroma")
EMBED_MODEL = "text-embedding-3-small"


def _embed(text: str):
    return client.embeddings.create(model=EMBED_MODEL, input=[text]).data[0].embedding


def _rrf(rankings: list, k: int = 60) -> dict:
    """Reciprocal Rank Fusion: combine ranked id-lists into one score map."""
    scores: dict = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
    return scores


def _maybe_rerank(query: str, hits: list) -> list:
    key = os.getenv("COHERE_API_KEY")
    if not key or not hits:
        return hits
    import cohere
    co = cohere.Client(key)
    res = co.rerank(model="rerank-english-v3.0", query=query,
                    documents=[h["text"] for h in hits], top_n=len(hits))
    return [hits[r.index] for r in res.results]


def search(query: str, collection_name: str = "docs", top_k: int = 5) -> list:
    coll = chroma.get_or_create_collection(collection_name)
    data = coll.get()  # all ids, documents, metadatas
    ids, docs, metas = data["ids"], data["documents"], data["metadatas"]
    if not ids:
        return []

    # Dense: nearest neighbours by embedding.
    dense = coll.query(query_embeddings=[_embed(query)], n_results=min(20, len(ids)))
    dense_ids = dense["ids"][0]

    # Sparse: BM25 over the same corpus (scores computed once).
    bm25 = BM25Okapi([d.lower().split() for d in docs])
    bm25_scores = bm25.get_scores(query.lower().split())
    bm25_ids = [ids[i] for i in sorted(range(len(docs)), key=lambda i: bm25_scores[i], reverse=True)[:20]]

    # Fuse, hydrate, rerank.
    fused = _rrf([dense_ids, bm25_ids])
    by_id = {ids[i]: {"text": docs[i], **metas[i]} for i in range(len(ids))}
    ranked = sorted(fused, key=lambda d: fused[d], reverse=True)[:top_k]
    return _maybe_rerank(query, [by_id[i] for i in ranked])