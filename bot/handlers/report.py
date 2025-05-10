from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from bot.services.reporting import get_reels_report, get_views_report
from config.config import ADMIN_ID

router = Router()

@router.message(Command("report_reels"))
async def cmd_report_reels(message: Message):
    if message.from_user.id not in ADMIN_ID:
        return await message.answer("⛔ Доступ запрещён")

    args = message.text.strip().split()
    if len(args) != 2 or not args[1].isdigit():
        return await message.answer("⚠️ Использование: /report_reels <code>task_id</code>")

    task_id = int(args[1])
    text = await get_reels_report(task_id)
    await message.answer(text)

@router.message(Command("report_views"))
async def cmd_report_views(message: Message):
    if message.from_user.id not in ADMIN_ID:
        return await message.answer("⛔ Доступ запрещён")

    args = message.text.strip().split()
    if len(args) != 2 or not args[1].isdigit():
        return await message.answer("⚠️ Использование: /report_views <code>view_task_id</code>")

    view_task_id = int(args[1])
    text = await get_views_report(view_task_id)
    await message.answer(text)
