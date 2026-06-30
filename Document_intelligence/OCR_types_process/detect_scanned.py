import pypdfium2 as pdfium

def is_likely_scanned(pdf_path: str, sample_pages: int = 3, char_threshold: int = 100) -> bool:
    """If the first N pages average < char_threshold characters, treat as scanned."""
    pdf = pdfium.PdfDocument(pdf_path)
    pages_to_check = min(sample_pages, len(pdf))
    total = 0
    for i in range(pages_to_check):
        page = pdf[i]
        tp = page.get_textpage()
        total += len(tp.get_text_range() or "")
        tp.close()
        page.close()
    return (total / pages_to_check) < char_threshold