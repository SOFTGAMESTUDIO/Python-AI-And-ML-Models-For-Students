from pathlib import Path
from src.loader import load_pdf
from src.splitter import chunk_text
from src.embedder import Embedder
from src.vector_store import SimpleVectorStore
from src.rag_pipeline import RagPipeline
from src.utils import ensure_directory

EMBEDDINGS_DIR = Path("embeddings")


def run_pipeline(pdf_path: str, query: str):
    ensure_directory(EMBEDDINGS_DIR)

    pages = load_pdf(pdf_path)
    chunks = chunk_text(pages)

    # Need to instantiate and fit the embedder from scratch
    embedder = Embedder()
    if chunks:
        embedder.fit([chunk["text"] for chunk in chunks])
    
    embeddings = embedder.embed([chunk["text"] for chunk in chunks])

    # Simple dict-based vector store for cosine similarity
    store = SimpleVectorStore.create(EMBEDDINGS_DIR / "pdf_vectors", chunks, embeddings, embedder)
    results = store.search(query, top_k=4)

    # Simplified extraction RAG architecture
    rag = RagPipeline()
    answer = rag.answer(query, results)

    return answer, results
