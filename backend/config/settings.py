"""Pydantic/env settings for SpeedRay backend."""

import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve .env from project root (parent of backend/) so it works regardless of cwd
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_ENV_FILE = os.path.join(_ROOT, ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SPEEDRAY_",
        env_file=_ENV_FILE,
        extra="ignore",  # ignore VITE_* and other non-SPEEDRAY_ vars from .env
    )

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False

    # Cloudinary
    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""

    # Gemini
    gemini_api_key: str = ""

    # OpenAI (fallback for report when Gemini quota/404)
    openai_api_key: str = ""

    # ElevenLabs
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = ""

    # Presage
    presage_base_url: str = ""
    presage_api_key: Optional[str] = None

    # Backboard.io
    backboard_base_url: str = ""
    backboard_api_key: Optional[str] = None

    # Solana
    solana_rpc_url: str = "https://api.mainnet-beta.solana.com"
    solana_private_key: Optional[str] = None
    solana_log_program_id: Optional[str] = None

    # Auth0
    auth0_domain: str = ""
    auth0_audience: Optional[str] = None
    auth0_issuer: Optional[str] = None

    # RAG / NoSQL
    rag_connection_string: str = ""
    rag_database: str = "speedray_rag"
    kaggle_index_name: str = "kaggle_cxr"
    nhi_index_name: str = "nhi_cxr"


@lru_cache
def get_settings() -> Settings:
    return Settings()
