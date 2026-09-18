import hmac
import logging

from fastapi import APIRouter, Header, HTTPException, Request, status

from app.bot.handlers import handle_message
from app.bot.max_api import MaxBotClient
from app.config import get_settings
from app.database.database import SessionLocal

router = APIRouter(tags=["max"])
logger = logging.getLogger(__name__)


def _extract_message(update: dict) -> tuple[int, int, str, str] | None:
    """Extract MAX message_created payload, tolerating documented field nesting."""
    if update.get("update_type") not in {"message_created", "message"}:
        return None
    message = update.get("message", update)
    body = message.get("body") or {}
    text = body.get("text") or message.get("text")
    sender = message.get("sender") or {}
    recipient = message.get("recipient") or {}
    user_id = sender.get("user_id") or sender.get("id")
    chat_id = recipient.get("chat_id") or message.get("chat_id")
    if not text or user_id is None or chat_id is None:
        return None
    name = sender.get("name") or sender.get("first_name") or "Студент"
    return int(user_id), int(chat_id), str(name), str(text)


def _verify_secret(value: str | None, configured: str) -> bool:
    if not configured:
        return False
    return value is not None and hmac.compare_digest(value, configured)


@router.post("/max/webhook", status_code=status.HTTP_200_OK)
async def max_webhook(request: Request, x_webhook_secret: str | None = Header(default=None)) -> dict:
    settings = get_settings()
    if not _verify_secret(x_webhook_secret, settings.max_webhook_secret):
        logger.warning("Rejected MAX webhook with invalid secret")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook secret")
    try:
        update = await request.json()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON") from exc
    parsed = _extract_message(update)
    if parsed is None:
        return {"status": "ignored"}
    user_id, chat_id, name, text = parsed
    try:
        async with SessionLocal() as session:
            await handle_message(session, user_id, chat_id, name, text, MaxBotClient(settings), settings.admin_ids)
    except Exception:
        logger.exception("Failed to process MAX update")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Update processing failed")
    return {"status": "ok"}
