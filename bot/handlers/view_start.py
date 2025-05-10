from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select
from datetime import datetime

from db.database import async_session
from db.models import Subscriber, ViewTask

router = Router()

# FSM состояния
class ViewFSM(StatesGroup):
    waiting_for_profiles = State()

# 📲 Клавиатура без импорта KeyboardButton
main_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [{"text": "📋 Отправить профиль Instagram"}],
        [{"text": "🎬 Отправить ссылку на Reels"}],
        [{"text": "👁 Запустить автопросмотр"}],
        [{"text": "📊 Мой отчёт"}],
    ]
)

# 👋 Команда /start
@router.message(F.text == "/start")
async def start_command(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "Я помогу тебе разместить Reels и собрать просмотры в Instagram 📈\n\n"
        "Что ты можешь сделать:\n"
        "📋 — указать логин Instagram\n"
        "🎬 — отправить Reels-ссылку и время\n"
        "👁 — запустить автопросмотр сторис\n"
        "📊 — получить отчёт\n\n"
        "Выбери действие на клавиатуре 👇",
        reply_markup=main_keyboard
    )

# 👁 Обработка команды /start_view
@router.message(F.text == "/start_view")
async def start_view_command_command(message: Message, state: FSMContext):
    await start_view_common(message, state)

# 👁 Обработка кнопки
@router.message(F.text == "👁 Запустить автопросмотр")
async def start_view_command_button(message: Message, state: FSMContext):
    await start_view_common(message, state)

# Общая логика запуска FSM
async def start_view_common(message: Message, state: FSMContext):
    await message.answer("📋 Введите список Instagram-профилей (через запятую):")
    await state.set_state(ViewFSM.waiting_for_profiles)

# 🧾 FSM: обработка списка профилей
@router.message(ViewFSM.waiting_for_profiles)
async def process_profiles(message: Message, state: FSMContext):
    raw_input = message.text.strip()
    cleaned = ",".join([p.strip() for p in raw_input.split(",") if p.strip()])

    if not cleaned:
        await message.answer("❌ Список пуст. Введите хотя бы один профиль:")
        return

    async with async_session() as session:
        result = await session.execute(
            select(Subscriber).where(Subscriber.telegram_id == message.from_user.id)
        )
        subscriber = result.scalar_one_or_none()

        if not subscriber:
            await message.answer("⚠️ Сначала зарегистрируйтесь через /submit_profile")
            await state.clear()
            return

        task = ViewTask(
            subscriber_id=subscriber.id,
            target_profiles=cleaned,
            scheduled_time=datetime.utcnow(),
            status="scheduled"
        )
        session.add(task)
        await session.commit()

    await message.answer(f"✅ Задача просмотра сторис сохранена! Профили:\n{cleaned}")
    await state.clear()
