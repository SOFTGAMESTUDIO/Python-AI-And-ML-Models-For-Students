import math
import re
from collections import Counter
from typing import List, Dict, Tuple


class Embedder:
    """
    A scratch implementation of a TF-IDF Embedder.
    """
    def __init__(self):
        self.vocab: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}

    def _tokenize(self, text: str) -> List[str]:
        # Simple lowercase and alphanumeric tokenization
        return re.findall(r'\b\w+\b', text.lower())

    def fit(self, texts: List[str]):
        """
        Learns the vocabulary and Inverse Document Frequencies (IDF) from the given texts.
        """
        num_docs = len(texts)
        doc_freqs = Counter()
        
        # Calculate Term Frequencies in documents
        for text in texts:
            tokens = self._tokenize(text)
            unique_tokens = set(tokens)
            for token in unique_tokens:
                doc_freqs[token] += 1
                
        # Calculate IDF and build vocabulary
        for idx, (token, df) in enumerate(doc_freqs.items()):
            self.vocab[token] = idx
            # Standard IDF formula: log(N / (DF + 1))
            self.idf[token] = math.log(num_docs / (float(df) + 1.0))

    def embed(self, texts: List[str]) -> List[Dict[int, float]]:
        """
        Converts texts to sparse TF-IDF vectors.
        Returns a list of dictionaries where keys are vocab indices and values are TF-IDF scores.
        """
        embeddings = []
        for text in texts:
            tokens = self._tokenize(text)
            total_tokens = len(tokens)
            
            if total_tokens == 0:
                embeddings.append({})
                continue
                
            term_counts = Counter(tokens)
            vector = {}
            max_norm = 0.0
            
            for token, count in term_counts.items():
                if token in self.vocab:
                    tf = count / float(total_tokens)
                    tfidf = tf * self.idf[token]
                    idx = self.vocab[token]
                    vector[idx] = tfidf
                    max_norm += tfidf * tfidf
                    
            # Normalize to L2 norm for easier cosine similarity
            max_norm = math.sqrt(max_norm)
            if max_norm > 0:
                for k in vector:
                    vector[k] /= max_norm
                    
            embeddings.append(vector)
            
        return embeddings
