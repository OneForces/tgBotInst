# bot/services/reporting.py

from db.database import async_session
from db.models import ReelsTask, ViewTask, ViewResult

async def get_reels_report(task_id: int) -> str:
    async with async_session() as session:
        task = await session.get(ReelsTask, task_id)
    if not task:
        return f"Задача публикации с ID={task_id} не найдена."
    text = (
        f"📣 Отчёт по публикации Reels ID={task.id}\n"
        f"• Создано: {task.created_at}\n"
        f"• Запланировано: {task.scheduled_time}\n"
        f"• Статус: {task.status}\n"
    )
    if task.status == "error":
        text += f"• Ошибка: {task.error_message}\n"
    return text

async def get_views_report(view_task_id: int) -> str:
    async with async_session() as session:
        vt = await session.get(ViewTask, view_task_id)
        if not vt:
            return f"Задача просмотра с ID={view_task_id} не найдена."
        result = await session.execute(
            select(ViewResult).where(ViewResult.task_id == view_task_id)
        )
        rows = result.scalars().all()
    lines = [f"👁️ Отчёт по просмотру ID={vt.id} (профиль: @{vt.target_profile})"]
    for r in rows:
        status = "✅" if r.success else "❌"
        lines.append(f"• {r.account}: {status} (время {r.timestamp})")
    return "\n".join(lines)
