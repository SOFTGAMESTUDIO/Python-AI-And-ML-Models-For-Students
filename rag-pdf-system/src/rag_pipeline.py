import re
from typing import List, Dict, Any

class RagPipeline:
    """
    Extractive RAG Pipeline from scratch.
    It returns the directly relevant passages concatenated to form a response.
    """
    def answer(self, query: str, contexts: List[Dict[str, Any]]) -> str:
        return self._simple_answer(query, contexts)

    def _simple_answer(self, query: str, contexts: List[Dict[str, Any]]) -> str:
        if not contexts:
            return "No relevant passages found for your query."
            
        result = [f"Best Found Passages for Query: '{query}'\n"]
        for idx, ctx in enumerate(contexts, 1):
            page_info = f" (page {ctx.get('page')})" if ctx.get('page') else ""
            snippet = self._extract_snippet(query, ctx["text"])
            result.append(f"--- Context {idx}{page_info} ---\n{snippet}")
        return "\n\n".join(result)

    def _extract_snippet(self, query: str, text: str) -> str:
        query_terms = re.findall(r"\w+", query.lower())
        if not query_terms:
            return text.strip()[:400] + ("..." if len(text) > 400 else "")

        lower_text = text.lower()
        for term in query_terms:
            idx = lower_text.find(term)
            if idx != -1:
                start = max(0, idx - 120)
                end = min(len(text), idx + 120)
                snippet = text[start:end].strip()
                if start > 0:
                    snippet = "..." + snippet
                if end < len(text):
                    snippet = snippet + "..."
                return snippet

        return text.strip()[:400] + ("..." if len(text) > 400 else "")
