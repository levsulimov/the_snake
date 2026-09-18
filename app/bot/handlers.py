import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.commands import HELP, MAP, WELCOME
from app.database.models import StudentQuestion, User
from app.services.documents import list_documents
from app.services.faq import list_faq
from app.services.search import search_knowledge

ROOT = Path(__file__).resolve().parents[2]


async def ensure_user(session: AsyncSession, max_user_id: int, name: str, admin_ids: set[int]) -> User:
    user = await session.scalar(select(User).where(User.max_user_id == max_user_id))
    if user is None:
        user = User(max_user_id=max_user_id, name=name or "Студент", role="admin" if max_user_id in admin_ids else "student")
        session.add(user)
        await session.commit()
    return user


def contacts_text() -> str:
    contacts = json.loads((ROOT / "knowledge_base" / "contacts.json").read_text(encoding="utf-8"))
    return "📞 Контакты университета\n\n" + "\n\n".join(f"{x['name']}\n{x['phone']} · {x['email']}\n{x['address']}" for x in contacts)


async def handle_message(session: AsyncSession, max_user_id: int, chat_id: int, name: str, text: str, sender, admin_ids: set[int]) -> None:
    user = await ensure_user(session, max_user_id, name, admin_ids)
    command, _, argument = text.strip().partition(" ")
    command = command.lower()
    if command == "/start":
        await sender.send_text(chat_id, WELCOME)
    elif command == "/help":
        await sender.send_text(chat_id, HELP)
    elif command == "/contacts":
        await sender.send_text(chat_id, contacts_text())
    elif command == "/map":
        await sender.send_text(chat_id, MAP)
    elif command == "/faq":
        items = await list_faq(session)
        await sender.send_text(chat_id, "❓ Частые вопросы\n\n" + "\n\n".join(f"{x.question}\n{x.answer}\nКатегория: {x.category}" for x in items))
    elif command == "/documents":
        items = await list_documents(session)
        await sender.send_text(chat_id, "📄 Документы\n\n" + "\n".join(f"• {x.title} ({x.category})\n{x.url}" for x in items))
    elif command == "/ask" and argument:
        session.add(StudentQuestion(user_id=user.id, text=argument))
        await session.commit()
        await sender.send_text(chat_id, "✅ Вопрос передан куратору. Мы ответим, как только сможем.")
    elif command == "/search" and argument:
        await _send_search(session, chat_id, argument, sender)
    elif text and not text.startswith("/"):
        await _send_search(session, chat_id, text, sender)
    else:
        await sender.send_text(chat_id, "Не понял команду. Введите /help.")


async def _send_search(session: AsyncSession, chat_id: int, query: str, sender) -> None:
    results = await search_knowledge(session, query)
    answer = "\n\n".join(results) if results else "По этому запросу ничего не найдено. Передайте вопрос куратору: /ask <ваш вопрос>."
    await sender.send_text(chat_id, answer)
