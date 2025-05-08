# scheduler/reels_scheduler.py

import traceback
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select, update
from datetime import datetime

from db.database import async_session
from db.models import ReelsTask
from bot.services.story_poster import post_reels_to_stories

async def check_and_post_reels():
    try:
        now = datetime.utcnow()
        print(f"[🕒] Время проверки: {now.isoformat()}")

        async with async_session() as session:
            result = await session.execute(
                select(ReelsTask)
                .where(
                    ReelsTask.status == "created",            # или "pending", если вы так называете
                    ReelsTask.scheduled_time <= now
                )
                .execution_options(no_cache=True)
            )
            tasks = result.scalars().all()
            print(f"[📋] Найдено задач на публикацию: {len(tasks)}")

        for task in tasks:
            try:
                print(f"[⏳] Публикация Reels ID={task.id}")
                await post_reels_to_stories(task)

                # Обновляем статус задачи
                async with async_session() as session:
                    await session.execute(
                        update(ReelsTask)
                        .where(ReelsTask.id == task.id)
                        .values(status="done")
                    )
                    await session.commit()

                print(f"[✅] Reels ID={task.id} опубликован")

            except Exception as e:
                print(f"[❌] Ошибка при публикации Reels ID={task.id}: {e}")
                traceback.print_exc()
                # Можно также пометить статус "error"
                async with async_session() as session:
                    await session.execute(
                        update(ReelsTask)
                        .where(ReelsTask.id == task.id)
                        .values(status="error")
                    )
                    await session.commit()

    except Exception as e:
        print(f"[💥] Ошибка при выборке задач: {e}")
        traceback.print_exc()

def start_scheduler():
    scheduler = AsyncIOScheduler(timezone="UTC")
    # Запуск check_and_post_reels каждую минуту
    scheduler.add_job(check_and_post_reels, "interval", minutes=1)
    scheduler.start()
    print("[🕒] Планировщик публикации Reels запущен (интервал ‒ 1 минута)")
