from aiogram import Router, types
from aiogram.filters import Command
from bot.services.pdf_report import export_user_report_pdf
import os
from config.config import ADMIN_ID

router = Router()


@router.message(Command("report"))
async def user_report(msg: types.Message):
    if msg.from_user.id not in ADMIN_ID:
        return await msg.answer("⛔ Доступ запрещён")

    parts = msg.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        return await msg.answer("⚠️ Использование: /report [telegram_id]")

    user_id = int(parts[1])
    await msg.answer(f"📄 Генерирую PDF-отчёт для пользователя {user_id}...")

    file_path = await export_user_report_pdf(user_id)

    if file_path and os.path.exists(file_path):
        await msg.answer_document(types.FSInputFile(file_path), caption=f"📊 Отчёт по пользователю {user_id}")
    else:
        await msg.answer("❌ Логи не найдены или файл не создан.")
