# bot/handlers/report.py

from aiogram import Router
from aiogram.types import Message
from bot.services.reporting import get_reels_report, get_views_report

router = Router()

@router.message(commands=["report_reels"])
async def cmd_report_reels(message: Message):
    try:
        task_id = int(message.get_args())
        text = await get_reels_report(task_id)
    except ValueError:
        text = "Неверный формат: используйте /report_reels <task_id>"
    await message.answer(text)

@router.message(commands=["report_views"])
async def cmd_report_views(message: Message):
    try:
        view_task_id = int(message.get_args())
        text = await get_views_report(view_task_id)
    except ValueError:
        text = "Неверный формат: используйте /report_views <view_task_id>"
    await message.answer(text)
