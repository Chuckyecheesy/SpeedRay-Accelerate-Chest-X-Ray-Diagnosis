"""RAG index and connection config for SpeedRay."""

from ...config import get_settings

s = get_settings()
RAG_CONNECTION_STRING = s.rag_connection_string
RAG_DATABASE = s.rag_database
KAGGLE_INDEX_NAME = s.kaggle_index_name
NHI_INDEX_NAME = s.nhi_index_name
