from pathlib import Path
from typing import List, Tuple
from PyPDF2 import PdfReader


def load_pdf(file_path: str) -> List[Tuple[int, str]]:
    path = Path(file_path)
    reader = PdfReader(str(path))
    pages: List[Tuple[int, str]] = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append((page_number, text.strip()))

    return pages
