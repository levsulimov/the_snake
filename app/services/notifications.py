import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Notification, User

logger = logging.getLogger(__name__)


async def broadcast(session: AsyncSession, text: str, sender) -> int:
    session.add(Notification(text=text))
    await session.commit()
    users = list((await session.scalars(select(User.max_user_id))).all())
    delivered = 0
    for user_id in users:
        try:
            await sender.send_text(user_id, text)
            delivered += 1
        except Exception:
            logger.exception("Notification delivery failed for MAX user %s", user_id)
    return delivered
