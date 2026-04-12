# RAG PDF System Documentation

## Overview

This documentation provides a quick reference for the `rag-pdf-system` project. The system is built to ingest PDF documents, split content into semantic chunks, compute document embeddings, and answer questions through similarity search.

## Contents

- `docs/architecture.md` — System architecture and pipeline flow.
- `README.md` — Project overview, setup, and usage.

## Getting Started

1. Activate the Python virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the Streamlit interface:

```bash
streamlit run app.py
```

4. Upload a PDF file and enter a question in the app.

## How the pipeline works

1. `src/loader.py` reads the PDF and extracts text from each page.
2. `src/splitter.py` divides the text into overlapping chunks while preserving page numbers.
3. `src/embedder.py` builds a TF-IDF embedding model and converts chunks into vectors.
4. `src/vector_store.py` searches for the most relevant chunks using cosine similarity.
5. `src/rag_pipeline.py` assembles the answer and returns the most relevant passages with page metadata.

## Best Practices

- Use clean PDF files with selectable text for better extraction quality.
- Upload documents with clear section headings to improve chunk relevance.
- Ask focused questions that match topics in the document.
- Add new PDFs to `data/` if you want a persistent local archive for reference.
