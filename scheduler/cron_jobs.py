import traceback
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select, update
from datetime import datetime

from db.engine import async_session
from db.models import ReelsTask
from bot.services.story_poster import post_reels_to_stories  

async def check_and_post_reels():
    try:
        now = datetime.utcnow()
        print(f"[🕒] Время запроса: {now.isoformat()}")

        async with async_session() as session:
            result = await session.execute(
                select(ReelsTask)
                .where(
                    ReelsTask.status == "created",
                    ReelsTask.post_time <= now
                )
                .execution_options(no_cache=True)
            )
            tasks = result.scalars().all()
            print(f"[📋] Найдено задач: {len(tasks)}")

        for task in tasks:
            try:
                print(f"[⏳] Публикация Reels ID {task.id} → {task.reels_url}")
                await post_reels_to_stories(task)

                async with async_session() as session:
                    await session.execute(
                        update(ReelsTask)
                        .where(ReelsTask.id == task.id)
                        .values(status="posted")
                    )
                    await session.commit()

                print(f"[✅] Reels ID {task.id} успешно опубликован")

            except Exception as e:
                print(f"[❌] Ошибка при публикации Reels ID {task.id}: {e}")
                traceback.print_exc()
                # Обновляем статус задачи на "error"
                async with async_session() as session:
                    await session.execute(
                        update(ReelsTask)
                        .where(ReelsTask.id == task.id)
                        .values(status="error")
                    )
                    await session.commit()

    except Exception as e:
        print(f"[💥] Ошибка выборки задач: {e}")
        traceback.print_exc()

def start_scheduler():
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(check_and_post_reels, "interval", minutes=1)
    scheduler.start()
    print("[🕒] Планировщик Reels запущен (каждую минуту)")
