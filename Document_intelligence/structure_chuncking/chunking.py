"""
Three chunking strategies. Run: python chunking.py
"""

def chunk_fixed(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[dict]:
    """Fixed-size chunks with overlap. Simple and reliable."""
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunk_text = text[i:i + chunk_size]
        chunks.append({
            "text": chunk_text,
            "start": i,
            "end": min(i + chunk_size, len(text)),
            "method": "fixed",
        })
    return chunks

# Test
text = "A" * 3000  # 3000 character document
chunks = chunk_fixed(text, chunk_size=1000, overlap=200)
print(f"Fixed chunking: {len(chunks)} chunks from {len(text)} chars")