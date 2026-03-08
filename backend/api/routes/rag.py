"""RAG retrieve endpoint for SpeedRay frontend."""

from fastapi import APIRouter
from ...ai_agents.rag import retrieve

router = APIRouter(prefix="/rag", tags=["rag"])


@router.get("/retrieve")
def rag_retrieve(query: str = "", top_k: int = 5, diseases: str = ""):
    """Retrieve RAG context. Optional comma-separated 'diseases' for disease-conditioned retrieval."""
    detected_diseases = [d.strip() for d in diseases.split(",") if d.strip()] if diseases else None
    return retrieve(query or "chest x-ray findings", top_k=top_k, detected_diseases=detected_diseases)
