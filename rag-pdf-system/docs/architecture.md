# RAG PDF System Architecture

## System Components

- `app.py`
  - Streamlit user interface for uploading PDFs and asking questions.
- `main.py`
  - Orchestrates the full pipeline from PDF ingestion to answer generation.
- `src/loader.py`
  - Extracts text page-by-page from a PDF file.
- `src/splitter.py`
  - Splits text into smaller chunks with overlap and page metadata.
- `src/embedder.py`
  - Builds a TF-IDF embedding model and converts text chunks into sparse vectors.
- `src/vector_store.py`
  - Computes cosine similarity between query embeddings and stored chunk vectors.
- `src/rag_pipeline.py`
  - Selects the top matching chunks and formats a response.
- `src/utils.py`
  - Supports directory creation and general helper utilities.

## Data Flow

1. **PDF ingestion**
   - The uploaded PDF is saved temporarily and passed to `main.py`.
   - `src/loader.py` reads each page and returns a list of page-text pairs.

2. **Chunking**
   - `src/splitter.py` tokenizes page text and generates overlapping chunks.
   - Each chunk includes the original page number for accurate references.

3. **Embedding**
   - `src/embedder.py` builds vocabulary and IDF from chunks.
   - Chunks are converted into normalized TF-IDF vectors.

4. **Search**
   - `src/vector_store.py` embeds the user query and scores each chunk.
   - The top-ranked chunks are returned with similarity scores.

5. **Answer assembly**
   - `src/rag_pipeline.py` builds a final answer using the top chunks.
   - It also extracts a relevant snippet and includes a page reference.

## Design Goals

- **Modularity**
  - Each component is separated so improvements can be added independently.
- **Clarity**
  - Page-aware chunking preserves document structure and improves retrieval accuracy.
- **Simplicity**
  - The system uses streamlit for fast UI prototyping and a lightweight embedding pipeline.
- **Extensibility**
  - The architecture can be upgraded with external transformers or a more advanced vector store.

## Deployment Notes

- Use `streamlit run app.py` to run locally.
- `requirements.txt` contains the runtime dependencies for this project.
- Add new documents to `data/` or upload them through the web UI.
