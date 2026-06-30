import re

def clean_ocr(text: str) -> str:
    # 1) Normalize whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 2) De-hyphenate words split across line breaks: "manage-\nment" -> "management"
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

    # 3) Strip obvious page-noise lines
    lines = [ln for ln in text.splitlines() if not re.match(r"^\s*Page \d+\s*$", ln)]
    return "\n".join(lines).strip()