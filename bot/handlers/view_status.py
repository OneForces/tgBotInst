from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select
from db.database import async_session
from db.models import Subscriber, ViewTask, ViewResult

router = Router()

@router.message(F.text == "/view_status")
async def view_status(message: Message):
    async with async_session() as session:
        # Найдём подписчика по Telegram ID
        result = await session.execute(
            select(Subscriber).where(Subscriber.telegram_id == message.from_user.id)
        )
        subscriber = result.scalar_one_or_none()

        if not subscriber:
            await message.answer("⚠️ Вы ещё не зарегистрированы. Используйте /submit_profile")
            return

        # Найдём все его задачи
        result = await session.execute(
            select(ViewTask).where(ViewTask.subscriber_id == subscriber.id)
        )
        tasks = result.scalars().all()

        if not tasks:
            await message.answer("📭 У вас пока нет задач на просмотр.")
            return

        response = "📊 <b>Результаты просмотра:</b>\n\n"
        for task in tasks:
            result = await session.execute(
                select(ViewResult).where(ViewResult.view_task_id == task.id)
            )
            results = result.scalars().all()

            if not results:
                response += f"🕓 Задача от {task.scheduled_time.strftime('%Y-%m-%d %H:%M')} — без результатов\n"
                continue

            response += f"🕓 Задача от {task.scheduled_time.strftime('%Y-%m-%d %H:%M')}:\n"
            for r in results:
                status = "✅" if r.success else "❌"
                response += f"• {r.profile_viewed} ← {r.viewer_account} {status} ({r.timestamp.strftime('%H:%M')})\n"
            response += "\n"

        await message.answer(response or "Нет данных")
