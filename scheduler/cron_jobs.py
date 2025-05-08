# scheduler/cron_jobs.py

import traceback
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select, update, literal
from db.database import async_session
from db.models import ScheduledPost
from bot.services.story_poster import post_reels_to_stories
from datetime import datetime

async def check_and_post_reels():
    try:
        now = datetime.utcnow()
        print(f"[🕒] Время запроса: {now.isoformat()}")

        async with async_session() as session:
            result = await session.execute(
                select(ScheduledPost)
                .where(
                    ScheduledPost.status == "pending",
                    ScheduledPost.scheduled_time <= literal(now)
                )
                .execution_options(no_cache=True)
            )
            tasks = result.scalars().all()
            print(f"[📋] Найдено задач: {len(tasks)}")

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
                traceback.print_exc()

    except Exception as e:
        print(f"[💥] Ошибка на этапе выборки задач: {e}")
        traceback.print_exc()

def start_scheduler():
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(check_and_post_reels, "interval", minutes=1)
    scheduler.start()
    print("[🕒] Планировщик Reels-сторий запущен (каждую минуту)")
