from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

from db.database import async_session
from db.models import Subscriber, ReelsTask

router = Router()

# Состояния FSM для submit_profile
class ProfileFSM(StatesGroup):
    waiting_for_instagram_login = State()
    waiting_for_instagram_password = State()

# Состояния FSM для submit_reels
class ReelsFSM(StatesGroup):
    waiting_for_reels_url = State()
    waiting_for_post_time = State()

# ========================== /submit_profile и кнопка ==========================

@router.message(F.text.in_({"/submit_profile", "📋 Отправить профиль Instagram"}))
async def submit_profile(message: Message, state: FSMContext):
    await state.clear()
    print("[FSM] submit_profile запущен")
    await message.answer("📋 Введите Instagram логин:")
    await state.set_state(ProfileFSM.waiting_for_instagram_login)

@router.message(ProfileFSM.waiting_for_instagram_login)
async def process_login(message: Message, state: FSMContext):
    login = message.text.strip()
    if not login:
        await message.answer("❗ Логин не может быть пустым. Повторите ввод:")
        return

    await state.update_data(instagram_login=login)
    await message.answer("🔑 Теперь введите пароль от Instagram:")
    await state.set_state(ProfileFSM.waiting_for_instagram_password)

@router.message(ProfileFSM.waiting_for_instagram_password)
async def process_password(message: Message, state: FSMContext):
    password = message.text.strip()
    if not password:
        await message.answer("❗ Пароль не может быть пустым. Повторите ввод:")
        return

    data = await state.get_data()
    instagram_login = data.get("instagram_login")

    async with async_session() as session:
        try:
            result = await session.execute(
                select(Subscriber).where(Subscriber.telegram_id == message.from_user.id)
            )
            if result.scalar_one_or_none():
                await message.answer("⚠️ Вы уже зарегистрированы.")
                await state.clear()
                return

            subscriber = Subscriber(
                telegram_id=message.from_user.id,
                instagram_login=instagram_login,
                instagram_password=password
            )
            session.add(subscriber)
            await session.commit()
            print(f"[✅] Новый подписчик: {instagram_login}")

            await message.answer("✅ Профиль успешно сохранён!")
        except SQLAlchemyError as e:
            print(f"[💥] Ошибка БД: {e}")
            await message.answer("❌ Ошибка при сохранении профиля.")
        finally:
            await state.clear()

# ========================== /submit_reels и кнопка ==========================

@router.message(F.text.in_({"/submit_reels", "🎬 Отправить ссылку на Reels"}))
async def submit_reels(message: Message, state: FSMContext):
    await state.clear()
    print("[FSM] submit_reels запущен")
    await message.answer("🔗 Отправьте ссылку на Reels:")
    await state.set_state(ReelsFSM.waiting_for_reels_url)

@router.message(ReelsFSM.waiting_for_reels_url)
async def process_reels_url(message: Message, state: FSMContext):
    url = message.text.strip()
    if not url.startswith("http"):
        await message.answer("❗ Это не похоже на ссылку. Повторите ввод:")
        return

    await state.update_data(reels_url=url)
    await message.answer("🕒 Введите дату и время публикации (пример: 2025-05-10 14:30):")
    await state.set_state(ReelsFSM.waiting_for_post_time)

@router.message(ReelsFSM.waiting_for_post_time)
async def process_post_time(message: Message, state: FSMContext):
    raw = " ".join(message.text.strip().split())
    try:
        post_time = datetime.strptime(raw, "%Y-%m-%d %H:%M")
    except ValueError:
        await message.answer("❌ Неверный формат. Используйте: 2025-05-10 14:30")
        return

    data = await state.get_data()
    reels_url = data.get("reels_url")

    async with async_session() as session:
        try:
            result = await session.execute(
                select(Subscriber).where(Subscriber.telegram_id == message.from_user.id)
            )
            subscriber = result.scalar_one_or_none()
            if not subscriber:
                await message.answer("⚠️ Сначала зарегистрируйтесь через /submit_profile")
                await state.clear()
                return

            task = ReelsTask(
                subscriber_id=subscriber.id,
                reels_url=reels_url,
                post_time=post_time,
                status="scheduled"
            )
            session.add(task)
            await session.commit()
            print(f"[✅] Задача добавлена: {reels_url}")

            await message.answer("✅ Задача сохранена и будет выполнена по расписанию!")
        except SQLAlchemyError as e:
            print(f"[💥] Ошибка БД: {e}")
            await message.answer("❌ Ошибка при сохранении задачи.")
        finally:
            await state.clear()
