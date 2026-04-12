from typing import List, Tuple, Dict, Any


def chunk_text(pages: List[Tuple[int, str]], chunk_size: int = 350, overlap: int = 50) -> List[Dict[str, Any]]:
    chunks: List[Dict[str, Any]] = []

    for page_number, text in pages:
        tokens = text.split()
        if not tokens:
            continue

        start = 0
        while start < len(tokens):
            end = min(start + chunk_size, len(tokens))
            chunk_text = " ".join(tokens[start:end])
            chunks.append({"text": chunk_text, "page": page_number})
            start += chunk_size - overlap

    return chunks
