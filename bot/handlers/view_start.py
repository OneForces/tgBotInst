from aiogram import Router, types
from instagram.automation.story_viewer import create_viewer_driver, view_stories
from db.database import async_session
from db.models import StoryViewLog
from datetime import datetime

router = Router()
ADMIN_ID = 123456789  # ← замените на свой Telegram ID

@router.message(types.F.text.lower() == "запустить просмотр")
async def start_view(msg: types.Message):
    await msg.answer("⏳ Запускаем просмотр сторис...")

    usernames = [
        "account_1", "account_2", "account_3"  # ← позже можно подгружать из базы
    ]

    driver = create_viewer_driver()
    report = view_stories(driver, usernames)
    driver.quit()

    # Сохраняем логи в базу данных
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

    # Формируем текст для пользователя
    user_report = "\n".join([f"@{u}: {s}" for u, s in report])
    await msg.answer(f"📊 Ваш отчёт:\n{user_report}")

    # Уведомление админу
    admin_text = (
        f"👤 <b>@{msg.from_user.username or 'Без username'}</b> "
        f"(<code>{msg.from_user.id}</code>) просмотрел сторис:\n{user_report}"
    )
    await msg.bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="HTML")
