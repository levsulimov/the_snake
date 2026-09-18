from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Document


async def list_documents(session: AsyncSession) -> list[Document]:
    return list((await session.scalars(select(Document).order_by(Document.category, Document.title))).all())


async def seed_documents(session: AsyncSession, items: list[dict]) -> None:
    for item in items:
        exists = await session.scalar(select(Document.id).where(Document.url == item["url"]))
        if not exists:
            session.add(Document(title=item["title"], url=item["url"], category=item["category"]))
    await session.commit()
