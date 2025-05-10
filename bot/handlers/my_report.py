from aiogram import Router, F, types
from sqlalchemy import select
from db.models import Subscriber
from db.database import async_session
from bot.services.pdf_report import export_user_report_pdf
import os

router = Router()

# Обработка кнопки или команды
@router.message(F.text.in_({"📊 Мой отчёт", "/my_report"}))
async def handle_user_report(message: types.Message):
    async with async_session() as session:
        result = await session.execute(
            select(Subscriber).where(Subscriber.telegram_id == message.from_user.id)
        )
        subscriber = result.scalar_one_or_none()

    if not subscriber:
        return await message.answer("⚠️ Вы ещё не зарегистрированы через /submit_profile")

    await message.answer("📄 Генерирую PDF-отчёт...")

    file_path = await export_user_report_pdf(message.from_user.id)

    if file_path and os.path.exists(file_path):
        await message.answer_document(types.FSInputFile(file_path), caption="📊 Ваш персональный отчёт")
    else:
        await message.answer("❌ Не удалось сформировать отчёт. Возможно, нет данных.")
