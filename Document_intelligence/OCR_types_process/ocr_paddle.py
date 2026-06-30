"""
PaddleOCR over scanned pages — strong default for non-English text.
Run: python ocr_paddle.py scanned.pdf
"""
import sys
import pypdfium2 as pdfium
from paddleocr import PaddleOCR

ocr = PaddleOCR(use_angle_cls=True, lang="en")   # 'ch', 'fr', 'german', 'arabic', etc.

def ocr_pdf(pdf_path: str) -> list[dict]:
    pdf = pdfium.PdfDocument(pdf_path)
    pages = []
    for i, page in enumerate(pdf):
        pil_image = page.render(scale=300 / 72).to_pil()
        import numpy as np
        result = ocr.ocr(np.array(pil_image), cls=True)
        # result[0] is a list of [box, (text, confidence)]
        lines = [line[1][0] for line in (result[0] or [])]
        pages.append({"page_number": i + 1, "text": "\n".join(lines)})
        page.close()
    return pages

if __name__ == "__main__":
    for p in ocr_pdf(sys.argv[1]):
        print(f"--- Page {p['page_number']} ---\n{p['text'][:400]}\n")