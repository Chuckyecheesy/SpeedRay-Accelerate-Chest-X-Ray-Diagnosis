"""NoSQL retriever for RAG (SpeedRay)."""

from typing import Any, Dict, List, Optional

from .datasets import load_kaggle_chunks, load_nhi_chunks
from .medical_knowledge import get_chunks_for_diseases


def retrieve(
    query: str,
    top_k: int = 5,
    use_kaggle: bool = True,
    use_nhi: bool = True,
    detected_diseases: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Retrieve relevant chunks from medical knowledge and/or Kaggle/NHI for RAG context."""
    chunks: List[str] = []
    citations: List[Dict[str, Any]] = []

    if detected_diseases:
        disease_chunks = get_chunks_for_diseases(detected_diseases)
        for i, text in enumerate(disease_chunks):
            chunks.append(text)
            citations.append({
                "source": "medical_knowledge",
                "snippet": text[:200],
                "score": 1.0 - i * 0.05,
            })

    if use_kaggle:
        kaggle = load_kaggle_chunks()
        for i, doc in enumerate(kaggle[:top_k]):
            text = doc.get("text", doc.get("content", str(doc)))
            chunks.append(text)
            citations.append({"source": "kaggle", "snippet": text[:200], "score": 1.0 - i * 0.1})

    if use_nhi:
        nhi = load_nhi_chunks()
        for i, doc in enumerate(nhi[:top_k]):
            text = doc.get("text", doc.get("content", str(doc)))
            chunks.append(text)
            citations.append({"source": "nhi", "snippet": text[:200], "score": 1.0 - i * 0.1})

    return {
        "query": query,
        "chunks": chunks,
        "citations": citations,
    }
