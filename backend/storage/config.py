"""Storage credentials and endpoints for SpeedRay backend."""

from ..config import get_settings

_settings = get_settings()

CLOUDINARY_CLOUD_NAME = _settings.cloudinary_cloud_name
CLOUDINARY_API_KEY = _settings.cloudinary_api_key
CLOUDINARY_API_SECRET = _settings.cloudinary_api_secret
SOLANA_RPC_URL = _settings.solana_rpc_url
SOLANA_PRIVATE_KEY = _settings.solana_private_key
SOLANA_LOG_PROGRAM_ID = _settings.solana_log_program_id
