"""
Empathyc ingest client - sends individual messages to empathyc.
Empathyc handles context internally via conversation_id.
We just dumb-pipe each message on arrival.
To use this client, you need to have an empathyc account and obtain your API keys
and follow the integration wizard at https://app.empathyc.co/dashboard/integrations

Proprietary note:
Please mind that Empathyc is a paid service, built by Keido Labs Ltd.
You can learn more about Empathyc monitoring platform at https://www.keidolabs.com/empathyc
or directly at https://empathyc.co
Pricing details can be found at https://empathyc.co/pricing

Rate limit: 120 RPM on empathyc side, we self-limit to 60 RPM (1 req/sec).
"""

import time
from pathlib import Path

import requests
import yaml

PROJECT_DIR = Path(__file__).parent.parent

# 60 RPM = 1 request per second
MIN_REQUEST_INTERVAL = 1.0
_last_request_time = 0.0


def _rate_limit():
    """Block until at least MIN_REQUEST_INTERVAL has passed since last request."""
    global _last_request_time
    now = time.monotonic()
    elapsed = now - _last_request_time
    if elapsed < MIN_REQUEST_INTERVAL:
        time.sleep(MIN_REQUEST_INTERVAL - elapsed)
    _last_request_time = time.monotonic()


def load_empathyc_keys() -> dict:
    """Load empathyc keys yaml."""
    with open(PROJECT_DIR / "empathyc_keys.yaml") as f:
        return yaml.safe_load(f)


def get_api_key(model: str, branch: str) -> str:
    """Get the empathyc API key for a specific model+branch combo."""
    keys = load_empathyc_keys()
    return keys["keys"][model][branch]


def get_ingest_endpoint() -> str:
    """Get the empathyc ingest endpoint URL."""
    keys = load_empathyc_keys()
    return keys["ingest_endpoint"]


def ingest_message(
    api_key: str,
    conv_id: str,
    message_id: str,
    role: str,
    content: str,
) -> dict:
    """
    Send a single message to empathyc ingest.
    Empathyc tracks conversation context internally by conv_id.

    role: "user" or "ai"
    """
    endpoint = get_ingest_endpoint()
    _rate_limit()
    resp = requests.post(
        endpoint,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "external_conversation_id": conv_id,
            "state": "open",
            "is_open": True,
            "messages": [
                {
                    "external_message_id": message_id,
                    "role": role,
                    "content": content,
                }
            ],
        },
    )
    resp.raise_for_status()
    return resp.json()
