# scheduler/cron_jobs.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select, update
from db.database import async_session
from db.models import ScheduledPost
from bot.services.story_poster import post_reels_to_stories
from datetime import datetime

async def check_and_post_reels():
    now = datetime.utcnow()

    async with async_session() as session:
        result = await session.execute(
            select(ScheduledPost).where(
                ScheduledPost.status == "pending",
                ScheduledPost.post_time <= now
            )
        )
        tasks = result.scalars().all()

    for task in tasks:
        try:
            print(f"[⏳] Запланированная публикация Reels ID {task.id}")
            await post_reels_to_stories(task)

            async with async_session() as session:
                await session.execute(
                    update(ScheduledPost)
                    .where(ScheduledPost.id == task.id)
                    .values(status="done")
                )
                await session.commit()
            print(f"[✅] Reels ID {task.id} успешно опубликован")

        except Exception as e:
            print(f"[❌] Ошибка при публикации Reels ID {task.id}: {e}")

def start_scheduler():
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(check_and_post_reels, "interval", minutes=1)
    scheduler.start()
    print("[🕒] Планировщик Reels-сторий запущен (каждую минуту)")
