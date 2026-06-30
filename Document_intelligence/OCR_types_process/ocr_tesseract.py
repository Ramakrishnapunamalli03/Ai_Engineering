"""
Render each page to a 300-DPI PNG, then OCR with Tesseract.
Run: python ocr_tesseract.py scanned.pdf
"""
import sys
import pypdfium2 as pdfium
import pytesseract
from PIL import Image

def ocr_pdf(pdf_path: str) -> list[dict]:
    pdf = pdfium.PdfDocument(pdf_path)
    pages = []
    for i, page in enumerate(pdf):
        # Higher scale = higher DPI = better OCR, slower & more RAM
        pil_image: Image.Image = page.render(scale=300 / 72).to_pil()
        text = pytesseract.image_to_string(pil_image, lang="eng")
        pages.append({"page_number": i + 1, "text": text.strip()})
        page.close()
    return pages

if __name__ == "__main__":
    for p in ocr_pdf(sys.argv[1]):
        print(f"--- Page {p['page_number']} ---\n{p['text'][:400]}\n")