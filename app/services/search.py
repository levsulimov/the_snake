from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Document, FAQ


async def search_knowledge(session: AsyncSession, query: str) -> list[str]:
    pattern = f"%{query.strip()}%"
    faq = list((await session.scalars(select(FAQ).where(or_(FAQ.question.ilike(pattern), FAQ.answer.ilike(pattern))).limit(3))).all())
    docs = list((await session.scalars(select(Document).where(or_(Document.title.ilike(pattern), Document.category.ilike(pattern))).limit(3))).all())
    return [f"❓ {item.question}\n{item.answer}" for item in faq] + [f"📄 {item.title}: {item.url}" for item in docs]
