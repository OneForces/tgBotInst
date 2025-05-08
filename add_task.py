import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select
from db.database import async_session
from db.models import ScheduledPost

async def add_and_check_task():
    # 1. Добавление задачи
    async with async_session() as session:
        task = ScheduledPost(
            reels_url="https://instagram.com/reel/debug",
            telegram_id=999999,
            instagram_login="debug_login",
            scheduled_time=datetime.utcnow() - timedelta(minutes=1),
            status="pending",
            created_at=datetime.utcnow(),
            is_posted=False
        )
        session.add(task)
        await session.commit()
        print(f"[+] Добавлена задача ID (пока без ID, сессия завершена)")

    # 2. Проверка всех задач
    async with async_session() as session:
        result = await session.execute(select(ScheduledPost))
        tasks = result.scalars().all()
        print(f"\n📋 Все задачи в базе ({len(tasks)}):")
        for t in tasks:
            print(f"  🔹 ID: {t.id} | Status: {t.status} | scheduled_time: {t.scheduled_time.isoformat()} | <= now: {t.scheduled_time <= datetime.utcnow()}")

    # 3. Проверка задач, подходящих под условие
    async with async_session() as session:
        result = await session.execute(
            select(ScheduledPost).where(
                ScheduledPost.status == "pending",
                ScheduledPost.scheduled_time <= datetime.utcnow()
            )
        )
        valid_tasks = result.scalars().all()
        print(f"\n✅ Подходящих задач: {len(valid_tasks)}")
        for t in valid_tasks:
            print(f"  ✅ ID: {t.id} | scheduled_time: {t.scheduled_time.isoformat()}")

asyncio.run(add_and_check_task())
