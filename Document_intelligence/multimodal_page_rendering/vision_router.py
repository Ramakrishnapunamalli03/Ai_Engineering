import pypdfium2 as pdfium

def pages_needing_vision(pdf_path: str, char_threshold: int = 200) -> list[int]:
    """Return 0-indexed page numbers whose extractable text is below threshold."""
    pdf = pdfium.PdfDocument(pdf_path)
    needs_vision: list[int] = []
    for i, page in enumerate(pdf):
        tp = page.get_textpage()
        text_len = len(tp.get_text_range() or "")
        if text_len < char_threshold:
            needs_vision.append(i)
        tp.close()
        page.close()
    return needs_vision

# Usage:
# for page_idx in pages_needing_vision("deck.pdf"):
#     print(ask_about_page("deck.pdf", page_idx, "Describe this page in detail"))