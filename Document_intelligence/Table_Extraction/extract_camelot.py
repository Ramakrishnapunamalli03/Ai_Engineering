"""
Extract tables from a PDF with Camelot — try both flavors, keep the highest-accuracy result.
Run: python extract_camelot.py report.pdf
"""
import sys
import camelot
import pandas as pd

def extract_tables(pdf_path: str, pages: str = "all") -> list[pd.DataFrame]:
    """Return one DataFrame per detected table; pages='1,3-5' or 'all'."""
    best: list[pd.DataFrame] = []
    for flavor in ("lattice", "stream"):
        tables = camelot.read_pdf(pdf_path, pages=pages, flavor=flavor)
        for t in tables:
            # Accuracy score is 0..100. 90+ is reliable; 60–80 is often usable; <60 is garbage.
            if t.accuracy >= 80:
                df = t.df
                df.attrs["page"] = t.page
                df.attrs["flavor"] = flavor
                df.attrs["accuracy"] = round(t.accuracy, 1)
                best.append(df)
    return best

if __name__ == "__main__":
    tables = extract_tables(sys.argv[1])
    print(f"Found {len(tables)} high-accuracy tables")
    for df in tables[:3]:
        print(f"\nPage {df.attrs['page']} ({df.attrs['flavor']}, acc={df.attrs['accuracy']})")
        print(df.head().to_string(index=False))