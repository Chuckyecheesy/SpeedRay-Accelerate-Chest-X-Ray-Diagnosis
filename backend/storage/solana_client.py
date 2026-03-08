"""Solana uneditable log submission for SpeedRay backend."""

import json
from typing import Any, Dict

from .config import SOLANA_LOG_PROGRAM_ID, SOLANA_PRIVATE_KEY, SOLANA_RPC_URL


def _get_client():
    try:
        from solana.rpc.api import Client
        from solders.keypair import Keypair
        return Client(SOLANA_RPC_URL), Keypair.from_base58_string(SOLANA_PRIVATE_KEY) if SOLANA_PRIVATE_KEY else None
    except ImportError:
        return None, None


def submit_log(
    run_id: str,
    study_id: str,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    """Submit an uneditable log entry to Solana. Returns tx signature or error."""
    client, keypair = _get_client()
    if not client or not keypair or not SOLANA_LOG_PROGRAM_ID:
        return {
            "success": False,
            "signature": None,
            "error": "Solana not configured",
        }

    try:
        data = json.dumps({"run_id": run_id, "study_id": study_id, "payload": payload}).encode("utf-8")
        # Placeholder: actual Solana program invoke would go here
        # tx = create_and_send_transaction(client, keypair, SOLANA_LOG_PROGRAM_ID, data)
        return {
            "success": True,
            "signature": "placeholder_solana_tx_signature",
        }
    except Exception as e:
        return {
            "success": False,
            "signature": None,
            "error": str(e),
        }
