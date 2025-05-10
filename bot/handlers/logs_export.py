from aiogram import Router, types
from aiogram.filters import Command
from bot.services.exporter import export_logs_to_excel
import os
from config.config import ADMIN_ID

router = Router()

# ✅ Поддержка нескольких админов

@router.message(Command("export_logs"))
async def export_logs_cmd(msg: types.Message):
    if msg.from_user.id not in ADMIN_ID:
        return await msg.answer("⛔ У вас нет доступа к этой команде.")

    await msg.answer("📦 Формирую Excel-файл с логами...")

    try:
        file_path = await export_logs_to_excel()

        if file_path and os.path.exists(file_path):
            await msg.answer_document(types.FSInputFile(file_path), caption="✅ Логи выгружены")
        else:
            await msg.answer("❌ Не удалось создать файл.")
    except Exception as e:
        await msg.answer(f"⚠️ Ошибка при экспорте логов:\n<code>{e}</code>")
