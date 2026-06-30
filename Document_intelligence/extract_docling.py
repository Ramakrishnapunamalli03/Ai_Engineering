"""
Extract structure-rich content with Docling, then export to Markdown.
Run: python extract_docling.py report.pdf
"""
import sys
from docling.document_converter import DocumentConverter

def extract_structured(pdf_path: str) -> dict:
    """Return a dict with rendered markdown + a flat list of structural items."""
    converter = DocumentConverter()
    result = converter.convert(pdf_path)
    doc = result.document

    items = []
    for item, _level in doc.iterate_items():
        items.append({
            "type": item.label,                 # 'title' | 'section_header' | 'paragraph' | 'list_item' | 'table' | ...
            "page": item.prov[0].page_no if item.prov else None,
            "text": getattr(item, "text", "")[:200],
        })

    return {
        "markdown": doc.export_to_markdown(),   # Great as direct LLM input
        "items": items,
    }

if __name__ == "__main__":
    data = extract_structured(sys.argv[1])
    print(f"Markdown export: {len(data['markdown'])} chars")
    print(f"Structural items: {len(data['items'])}")
    by_type = {}
    for item in data["items"]:
        by_type[item["type"]] = by_type.get(item["type"], 0) + 1
    print(f"  By type: {by_type}")