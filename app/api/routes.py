from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.max_api import MaxBotClient
from app.config import get_settings
from app.database.database import get_session
from app.database.models import StudentQuestion, User
from app.services.notifications import broadcast

router = APIRouter(tags=["service"])


class BroadcastRequest(BaseModel):
    admin_max_user_id: int
    text: str = Field(min_length=1, max_length=4000)


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/questions")
async def questions(admin_max_user_id: int, session: AsyncSession = Depends(get_session)) -> list[dict]:
    admin = await session.scalar(select(User).where(User.max_user_id == admin_max_user_id, User.role.in_(("admin", "curator"))))
    if not admin:
        raise HTTPException(status_code=403, detail="Curator or admin role required")
    rows = list((await session.scalars(select(StudentQuestion).where(StudentQuestion.status == "new").order_by(StudentQuestion.created_at))).all())
    return [{"id": row.id, "user_id": row.user_id, "text": row.text, "created_at": row.created_at} for row in rows]


@router.post("/notifications")
async def create_notification(payload: BroadcastRequest, session: AsyncSession = Depends(get_session)) -> dict:
    admin = await session.scalar(select(User).where(User.max_user_id == payload.admin_max_user_id, User.role == "admin"))
    if not admin:
        raise HTTPException(status_code=403, detail="Admin role required")
    count = await broadcast(session, payload.text, MaxBotClient(get_settings()))
    return {"delivered": count}
