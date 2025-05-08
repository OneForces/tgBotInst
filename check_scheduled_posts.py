# check_scheduled_posts.py

import asyncio
from db.database import async_session
from db.models import ScheduledPost
from sqlalchemy import select

async def check_tasks():
    async with async_session() as session:
        result = await session.execute(select(ScheduledPost))
        tasks = result.scalars().all()
        print(f"[📋] Всего задач: {len(tasks)}")
        for task in tasks:
            print(f"ID: {task.id} | Статус: {task.status} | Время публикации: {task.scheduled_time} | Создано: {task.created_at}")

asyncio.run(check_tasks())
