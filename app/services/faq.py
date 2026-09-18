from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import FAQ


async def list_faq(session: AsyncSession, limit: int = 10) -> list[FAQ]:
    return list((await session.scalars(select(FAQ).order_by(FAQ.category, FAQ.id).limit(limit))).all())


async def seed_faq(session: AsyncSession, items: list[dict]) -> None:
    for item in items:
        exists = await session.scalar(select(FAQ.id).where(FAQ.question == item["question"]))
        if not exists:
            session.add(FAQ(question=item["question"], answer=item["answer"], category=item["category"]))
    await session.commit()
