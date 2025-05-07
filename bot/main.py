import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config.config import BOT_TOKEN
from db.database import Base, engine
from scheduler.cron_jobs import start_scheduler

# Импорт Telegram-роутеров
from bot.handlers import (
    reels_submission,
    admin_accounts,
    view_start,
    logs_admin,
    logs_export,
    report_user,
)


async def init_db():
    """Создание таблиц в базе данных (если не существуют)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def init_bot() -> Dispatcher:
    """Инициализация бота и диспетчера."""
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрация всех роутеров
    routers = [
        reels_submission.router,
        admin_accounts.router,
        view_start.router,
        logs_admin.router,
        logs_export.router,
        report_user.router,
    ]
    for r in routers:
        dp.include_router(r)

    return bot, dp


async def main():
    await init_db()
    bot, dp = await init_bot()

    # Запуск планировщика
    start_scheduler()

    print("🚀 Бот запущен и работает.")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"❌ Ошибка во время polling: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("⏹️ Остановка по запросу пользователя")
    except Exception as e:
        print(f"🔥 Критическая ошибка: {e}")
