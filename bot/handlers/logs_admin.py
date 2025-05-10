from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy import select, desc
from db.engine import async_session
from db.models import StoryViewLog
from config.config import ADMIN_ID

router = Router()

@router.message(Command("logs"))
async def get_logs(msg: types.Message):
    if msg.from_user.id not in ADMIN_ID:
        return await msg.answer("⛔ Доступ запрещён")

    args = msg.text.split()
    limit = 10
    filter_by_id = None

    if len(args) >= 2:
        if args[1].isdigit():
            filter_by_id = int(args[1])
        elif args[1] == "all":
            limit = 100
        else:
            return await msg.answer("⚠️ Использование: /logs [user_id | all]")

    async with async_session() as session:
        query = select(StoryViewLog).order_by(desc(StoryViewLog.timestamp)).limit(limit)
        if filter_by_id:
            query = query.where(StoryViewLog.viewer_telegram_id == filter_by_id)

        result = await session.execute(query)
        logs = result.scalars().all()

    if not logs:
        return await msg.answer("📭 Нет логов.")

    text = "🗂 <b>Логи просмотров:</b>\n\n"
    for log in logs:
        status_emoji = "✅" if log.status == "viewed" else "❌"
        text += (
            f"{status_emoji} <code>{log.timestamp.strftime('%Y-%m-%d %H:%M')}</code> — "
            f"<b>{log.target_username}</b> от <code>{log.viewer_telegram_id}</code>\n"
        )

    await msg.answer(text, parse_mode="HTML")
