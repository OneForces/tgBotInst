from aiogram import Router, types, F
from aiogram.filters import Command
from db.engine import async_session
from db.models import InstagramAccount

router = Router()

ADMIN_IDS = [123456789]  # ← замените на свой Telegram ID

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

@router.message(Command("add_account"))
async def add_account(msg: types.Message):
    if not is_admin(msg.from_user.id):
        return await msg.answer("⛔ Доступ запрещён")

    parts = msg.text.split()
    if len(parts) < 3:
        return await msg.answer("⚠️ Формат: /add_account username password [proxy]")

    username, password = parts[1], parts[2]
    proxy = parts[3] if len(parts) > 3 else None

    async with async_session() as session:
        session.add(InstagramAccount(username=username, password=password, proxy=proxy))
        await session.commit()

    await msg.answer(f"✅ Аккаунт @{username} добавлен.")

@router.message(Command("list_accounts"))
async def list_accounts(msg: types.Message):
    if not is_admin(msg.from_user.id):
        return await msg.answer("⛔ Доступ запрещён")

    async with async_session() as session:
        result = await session.execute(
            InstagramAccount.__table__.select()
        )
        accounts = result.fetchall()

    if not accounts:
        return await msg.answer("📭 Нет аккаунтов")

    text = "\n".join([f"{row.username} (proxy: {row.proxy or '—'})" for row in accounts])
    await msg.answer("📋 Аккаунты:\n" + text)

@router.message(Command("delete_account"))
async def delete_account(msg: types.Message):
    if not is_admin(msg.from_user.id):
        return await msg.answer("⛔ Доступ запрещён")

    parts = msg.text.split()
    if len(parts) < 2:
        return await msg.answer("⚠️ Формат: /delete_account username")

    username = parts[1]

    async with async_session() as session:
        result = await session.execute(
            InstagramAccount.__table__.delete().where(InstagramAccount.username == username)
        )
        await session.commit()

    await msg.answer(f"🗑️ Аккаунт @{username} удалён.")
