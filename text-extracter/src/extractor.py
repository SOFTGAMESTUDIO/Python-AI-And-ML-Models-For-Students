import fitz  # PyMuPDF

def extract_columns(pdf_path):
    doc = fitz.open(pdf_path)
    pages_data = []

    for page in doc:
        blocks = page.get_text("blocks")
        page_width = page.rect.width
        mid_x = page_width / 2

        left, right = [], []

        for b in blocks:
            x0, y0, x1, y1, text, *_ = b
            text = text.strip()
            if not text:
                continue

            if x0 < mid_x:
                left.append((y0, text))
            else:
                right.append((y0, text))

        left.sort(key=lambda x: x[0])
        right.sort(key=lambda x: x[0])

        pages_data.append({
            "left": [t for _, t in left],
            "right": [t for _, t in right]
        })

    return pages_data