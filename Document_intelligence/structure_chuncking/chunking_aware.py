"""
Split on document structure (headers, sections) — preserves logical boundaries.
Best for: markdown docs, technical manuals, legal documents.
"""

def chunk_by_headers(text: str, max_chunk_size: int = 2000) -> list[dict]:
    """Split on markdown headers, keeping sections intact."""
    import re
    
    # Split on markdown headers (# through ####)
    sections = re.split(r'(?=^#{1,4} )', text, flags=re.MULTILINE)
    
    chunks = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        
        # Extract the header for metadata
        lines = section.split("\n")
        header = lines[0].lstrip("# ").strip() if lines[0].startswith("#") else "Untitled"
        
        # If section is too long, sub-chunk it
        if len(section) > max_chunk_size:
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            splitter = RecursiveCharacterTextSplitter(chunk_size=max_chunk_size, chunk_overlap=100)
            sub_chunks = splitter.split_text(section)
            for j, sub in enumerate(sub_chunks):
                chunks.append({"text": sub, "header": header, "part": j + 1})
        else:
            chunks.append({"text": section, "header": header, "part": 1})
    
    return chunks