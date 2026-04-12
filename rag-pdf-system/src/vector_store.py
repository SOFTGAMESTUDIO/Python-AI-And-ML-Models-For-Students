import json
from pathlib import Path
from typing import List, Dict, Any
from src.embedder import Embedder

class SimpleVectorStore:
    def __init__(self, texts: List[Dict[str, Any]], embeddings: List[Dict[int, float]], embedder: Embedder):
        self.texts = texts
        self.embeddings = embeddings
        self.embedder = embedder

    @classmethod
    def create(cls, path: Path, texts: List[Dict[str, Any]], embeddings: List[Dict[int, float]], embedder: Embedder):
        store = cls(texts, embeddings, embedder)
        store._save_metadata(path)
        return store

    def _save_metadata(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.with_suffix('.txt').write_text("\n\n---\n\n".join(chunk["text"] for chunk in self.texts), encoding='utf-8')
        
    def _cosine_similarity(self, v1: Dict[int, float], v2: Dict[int, float]) -> float:
        # Since v1 and v2 are L2 normalized in the embedder, dot product == cosine similarity.
        score = 0.0
        # Iterate over the smaller vector for efficiency
        if len(v1) > len(v2):
            v1, v2 = v2, v1
            
        for k, v in v1.items():
            if k in v2:
                score += v * v2[k]
        return score

    def search(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        # Need to embed the query using the fitted embedder
        query_vector = self.embedder.embed([query])[0]
        
        # Calculate similarities against all cached sparse vectors
        scored_chunks = []
        for idx, doc_vector in enumerate(self.embeddings):
            score = self._cosine_similarity(query_vector, doc_vector)
            scored_chunks.append({
                "text": self.texts[idx]["text"],
                "page": self.texts[idx].get("page"),
                "score": score,
            })
            
        # Sort by highest score
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        
        # Return top K
        return scored_chunks[:top_k]
