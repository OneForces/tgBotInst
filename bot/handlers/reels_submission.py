from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from db.database import async_session
from db.models import Subscriber
from sqlalchemy import select
from aiogram.fsm.state import State, StatesGroup  

router = Router()

# FSM состояния
class ProfileSubmission(StatesGroup):
    instagram_login = State()
    instagram_password = State()

@router.message(Command("submit_profile"))
async def cmd_submit_profile(message: Message, state: FSMContext):
    await message.answer("Введите ваш Instagram логин:")
    await state.set_state(ProfileSubmission.instagram_login)

@router.message(ProfileSubmission.instagram_login)
async def process_login(message: Message, state: FSMContext):
    await state.update_data(instagram_login=message.text)
    await message.answer("Введите пароль от Instagram:")
    await state.set_state(ProfileSubmission.instagram_password)

@router.message(ProfileSubmission.instagram_password)
async def process_password(message: Message, state: FSMContext):
    data = await state.get_data()
    instagram_login = data["instagram_login"]
    instagram_password = message.text

    async with async_session() as session:
        existing = await session.execute(
            select(Subscriber).where(Subscriber.telegram_id == message.from_user.id)
        )
        sub = existing.scalar_one_or_none()
        if sub:
            sub.instagram_login = instagram_login
            sub.instagram_password = instagram_password
        else:
            sub = Subscriber(
                telegram_id=message.from_user.id,
                instagram_login=instagram_login,
                instagram_password=instagram_password,
            )
            session.add(sub)

        await session.commit()

    await message.answer("✅ Профиль Instagram сохранён.")
    await state.clear()
