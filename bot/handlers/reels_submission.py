from aiogram import Router, types, F
from db.models import UserSubmission
from db.database import async_session
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

router = Router()

class SubmissionForm(StatesGroup):
    instagram = State()
    telegram = State()
    reels = State()

@router.message(F.text.lower() == "начать")
async def start_submission(msg: types.Message, state: FSMContext):
    await msg.answer("🔗 Пришли ссылку на свой Instagram-профиль:")
    await state.set_state(SubmissionForm.instagram)

@router.message(SubmissionForm.instagram)
async def get_instagram(msg: types.Message, state: FSMContext):
    await state.update_data(instagram_link=msg.text)
    await msg.answer("🔗 Теперь ссылку на свой Telegram-профиль:")
    await state.set_state(SubmissionForm.telegram)

@router.message(SubmissionForm.telegram)
async def get_telegram(msg: types.Message, state: FSMContext):
    await state.update_data(telegram_link=msg.text)
    await msg.answer("🎥 И наконец ссылку на Reels-видео:")
    await state.set_state(SubmissionForm.reels)

@router.message(SubmissionForm.reels)
async def get_reels(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    data["reels_link"] = msg.text

    async with async_session() as session:
        session.add(UserSubmission(
            telegram_id=msg.from_user.id,
            instagram_link=data["instagram_link"],
            telegram_link=data["telegram_link"],
            reels_link=data["reels_link"]
        ))
        await session.commit()

    await msg.answer("✅ Спасибо! Все данные сохранены.")
    await state.clear()
