"""Small, isolated adapter for the MAX Bot API.

The rest of the application deals only with ``send_text``. If MAX changes its
transport schema, update this module without rewriting business handlers.
"""
import logging

import httpx

from app.config import Settings

logger = logging.getLogger(__name__)


class MaxAPIError(RuntimeError):
    pass


class MaxBotClient:
    def __init__(self, settings: Settings):
        self.base_url = settings.max_api_base_url.rstrip("/")
        self.token = settings.max_token

    @property
    def headers(self) -> dict[str, str]:
        return {"Authorization": self.token, "Content-Type": "application/json"}

    async def send_text(self, chat_id: int, text: str) -> None:
        if not self.token:
            logger.warning("MAX_TOKEN is empty; message to %s is not sent", chat_id)
            return
        payload = {"recipient": {"chat_id": chat_id}, "text": text}
        async with httpx.AsyncClient(base_url=self.base_url, timeout=10.0) as client:
            response = await client.post("/messages", headers=self.headers, json=payload)
        if response.is_error:
            logger.error("MAX send failed: %s %s", response.status_code, response.text[:500])
            raise MaxAPIError(f"MAX API returned {response.status_code}")

    async def register_webhook(self, url: str, secret: str) -> None:
        """Register the public callback using the MAX subscriptions endpoint."""
        if not self.token or not url:
            return
        payload = {"url": url, "secret": secret, "update_types": ["message_created"]}
        async with httpx.AsyncClient(base_url=self.base_url, timeout=10.0) as client:
            response = await client.post("/subscriptions", headers=self.headers, json=payload)
        response.raise_for_status()
