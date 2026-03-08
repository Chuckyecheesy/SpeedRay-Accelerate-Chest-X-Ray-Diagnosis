"""Kaggle/NHI dataset loading and index for SpeedRay RAG."""

from typing import Any, Dict, List

from .config import KAGGLE_INDEX_NAME, NHI_INDEX_NAME, RAG_CONNECTION_STRING, RAG_DATABASE

# Placeholder in-memory index when NoSQL not configured
_memory_index: List[Dict[str, Any]] = []


def load_kaggle_chunks() -> List[Dict[str, Any]]:
    """Load or reference Kaggle CXR dataset chunks for RAG."""
    if not RAG_CONNECTION_STRING:
        return _memory_index
    # TODO: connect to NoSQL and load Kaggle index
    return _memory_index


def load_nhi_chunks() -> List[Dict[str, Any]]:
    """Load or reference NHI dataset chunks for RAG."""
    if not RAG_CONNECTION_STRING:
        return _memory_index
    # TODO: connect to NoSQL and load NHI index
    return _memory_index


def get_index_names() -> tuple:
    return KAGGLE_INDEX_NAME, NHI_INDEX_NAME
