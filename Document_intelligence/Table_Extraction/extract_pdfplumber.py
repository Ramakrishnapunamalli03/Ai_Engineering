"""
Extract tables with pdfplumber — pure-Python, no Ghostscript.
Run: python extract_pdfplumber.py report.pdf
"""
import sys
import pdfplumber
import pandas as pd

def extract_tables(pdf_path: str) -> list[pd.DataFrame]:
    out: list[pd.DataFrame] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            for table in page.extract_tables() or []:
                if not table or len(table) < 2:
                    continue
                headers = [h or f"col_{i}" for i, h in enumerate(table[0])]
                df = pd.DataFrame(table[1:], columns=headers)
                df.attrs["page"] = page_num
                out.append(df)
    return out

if __name__ == "__main__":
    for df in extract_tables(sys.argv[1])[:3]:
        print(f"\nPage {df.attrs['page']}:")
        print(df.head().to_string(index=False))