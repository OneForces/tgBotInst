from aiogram import Router, types
from instagram.automation.view_stories import create_viewer_driver, view_stories
from db.database import async_session
from db.models import StoryViewLog
from aiogram import F
from scheduler.cron_jobs import check_and_post_reels
from datetime import datetime

router = Router()
ADMIN_ID = 123456789  # ← замените на свой Telegram ID

@router.message(F.text.lower() == "запустить просмотр")
async def start_view(msg: types.Message):
    await msg.answer("⏳ Запускаем просмотр сторис...")

    usernames = [
        "account_1", "account_2", "account_3"
    ]

    driver = create_viewer_driver()

    # 🔹 Создаём новую ViewSession и сохраняем её ID
    async with async_session() as session:
        from db.models import ViewSession
        from datetime import datetime

        new_session = ViewSession(user_id=msg.from_user.id)
        session.add(new_session)
        await session.flush()
        session_id = new_session.id
        await session.commit()

    # 📲 Запуск просмотра
    report = view_stories(driver, usernames)

    # ✅ Завершаем ViewSession после просмотра
    async with async_session() as session:
        from instagram.manager import complete_session
        await complete_session(session, session_id)

    # 📝 Логируем StoryViewLog
    async with async_session() as session:
        for username, status_text in report:
            status = "viewed" if "✅" in status_text else "failed"
            log = StoryViewLog(
                viewer_telegram_id=msg.from_user.id,
                target_username=username,
                status=status,
                timestamp=datetime.utcnow()
            )
            session.add(log)
        await session.commit()

    # 📊 Отчёт пользователю
    user_report = "\n".join([f"@{u}: {s}" for u, s in report])
    await msg.answer(f"📊 Ваш отчёт:\n{user_report}")

    # 📩 Уведомление админу
    admin_text = (
        f"👤 <b>@{msg.from_user.username or 'Без username'}</b> "
        f"(<code>{msg.from_user.id}</code>) просмотрел сторис:\n{user_report}"
    )
    await msg.bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="HTML")

@router.message(F.text.lower() == "проверить публикации")
async def trigger_manual_check(message: types.Message):
    await message.answer("⏳ Проверяю отложенные публикации...")
    try:
        await check_and_post_reels()
        await message.answer("✅ Проверка завершена.")
    except Exception as e:
        await message.answer(f"❌ Ошибка при проверке: {e}")