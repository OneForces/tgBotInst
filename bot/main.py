import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from config.config import BOT_TOKEN, ADMIN_ID
from db.database import Base
from db.engine import async_engine
from scheduler.combined_scheduler import main_loop  # Планировщик внутри

# Импорт Telegram-роутеров
from bot.handlers import (
    reels_submission,
    admin_accounts,
    view_start,
    logs_admin,
    logs_export,
    report_user,
    view_status,
    my_report,
    report,
)

# Глобальный диспетчер
dp = Dispatcher(storage=MemoryStorage())


async def init_db():
    """Создание таблиц в базе данных (если не существуют)."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("📦 База данных инициализирована")


async def init_bot() -> Bot:
    """Инициализация бота и регистрация роутеров."""
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    routers = [
        reels_submission.router,
        admin_accounts.router,
        view_start.router,
        logs_admin.router,
        logs_export.router,
        report_user.router,
        view_status.router,
        my_report.router,
        report.router,
    ]
    for r in routers:
        dp.include_router(r)

    print("🤖 Роутеры загружены")
    return bot


async def main():
    await init_db()
    bot = await init_bot()

    # Проверим ID админа
    me = await bot.get_me()
    print(f"🚀 Бот {me.username} запущен | ID: {me.id}")
    print(f"🔐 Админ ID(ы): {ADMIN_ID}")

    # Планировщик — как фоновая задача
    asyncio.create_task(main_loop())

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
        print(f"🔥 Критическая ошибка запуска: {e}")
