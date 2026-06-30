"""
Extract text from a born-digital PDF using pypdfium2.
Run: python extract_pypdfium2.py document.pdf
"""
import sys
import pypdfium2 as pdfium

def extract_pdf_text(pdf_path: str) -> list[dict]:
    """Extract text from each page with metadata."""
    pdf = pdfium.PdfDocument(pdf_path)
    pages: list[dict] = []
    for i, page in enumerate(pdf):
        textpage = page.get_textpage()
        text = (textpage.get_text_range() or "").strip()
        if text:
            pages.append({
                "page_number": i + 1,
                "text": text,
                "char_count": len(text),
            })
        textpage.close()
        page.close()
    return pages

if __name__ == "__main__":
    pages = extract_pdf_text(sys.argv[1])
    print(f"Extracted {len(pages)} pages")
    for page in pages[:3]:
        print(f"\n--- Page {page['page_number']} ({page['char_count']} chars) ---")
        print(page['text'][:300] + "...")