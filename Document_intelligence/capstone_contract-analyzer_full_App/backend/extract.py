"""Multi-strategy PDF extraction: born-digital text, OCR fallback, and tables."""
import io
from importlib.metadata import version, PackageNotFoundError

import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes


def _ver(pkg: str) -> str:
    try:
        return version(pkg)
    except PackageNotFoundError:
        return "unknown"


def extract_pages(pdf_bytes: bytes) -> dict:
    """Return {"pages": [...], "audit": [...]}; each page records its strategy."""
    pages, audit = [], []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = (page.extract_text() or "").strip()
            tables = page.extract_tables() or []
            strategy = "born-digital"

            # No text => scanned page => OCR this single page.
            if not text:
                strategy = "ocr"
                images = convert_from_bytes(pdf_bytes, first_page=i, last_page=i)
                if images:
                    text = pytesseract.image_to_string(images[0]).strip()

            pages.append({"page_no": i, "text": text, "tables": tables})
            audit.append({
                "page_no": i,
                "strategy": strategy,
                "has_tables": bool(tables),
                "pdfplumber": _ver("pdfplumber"),
                "pytesseract": _ver("pytesseract"),
            })
    return {"pages": pages, "audit": audit}