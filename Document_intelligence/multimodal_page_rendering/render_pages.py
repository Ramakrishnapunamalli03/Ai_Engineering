"""
Render PDF pages to base64 PNG strings ready for a vision API.
Run: python render_pages.py deck.pdf
"""
import sys, base64, io
import pypdfium2 as pdfium

def render_pages(pdf_path: str, dpi: int = 144, max_pages: int = 20) -> list[str]:
    """Return one base64-encoded PNG per page (capped at max_pages)."""
    pdf = pdfium.PdfDocument(pdf_path)
    pages_b64: list[str] = []
    for i, page in enumerate(pdf):
        if i >= max_pages: break
        pil_image = page.render(scale=dpi / 72).to_pil()
        buf = io.BytesIO()
        pil_image.save(buf, format="PNG", optimize=True)
        pages_b64.append(base64.b64encode(buf.getvalue()).decode())
        page.close()
    return pages_b64

if __name__ == "__main__":
    pages = render_pages(sys.argv[1])
    print(f"Rendered {len(pages)} pages, total {sum(len(p) for p in pages) // 1024} KB base64")