from typing import BinaryIO

import pdfplumber


def extract_cv_text(file: str | BinaryIO) -> str:
    """Extract text from a PDF path or file-like object. Size limits / scan detection: Phase 2."""
    with pdfplumber.open(file) as pdf:
        return "\n\n".join(text for page in pdf.pages if (text := page.extract_text()))
