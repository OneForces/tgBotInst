import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select, update
from db.database import async_session
from db.models import ViewTask, ViewResult
from scheduler.appium_control import view_stories

scheduler = AsyncIOScheduler()

async def check_and_view_stories():
    print("✅ check_and_view_stories started", flush=True)
    async with async_session() as session:
        try:
            result = await session.execute(
                select(ViewTask).where(ViewTask.status == "scheduled")
            )
            tasks = result.scalars().all()
            print(f"[👀] Найдено задач для просмотра: {len(tasks)}", flush=True)

            for task in tasks:
                profiles = [p.strip() for p in task.target_profiles.split(",") if p.strip()]
                for profile in profiles:
                    try:
                        viewer = "viewer_account_1"
                        success = await view_stories(profile, viewer)
                        session.add(ViewResult(
                            view_task_id=task.id,
                            profile_viewed=profile,
                            viewer_account=viewer,
                            success=success,
                            timestamp=datetime.utcnow()
                        ))
                        print(f"[✅] Просмотрено: {profile} → {success}", flush=True)
                    except Exception as e:
                        print(f"[💥] Ошибка при просмотре {profile}: {e}", flush=True)

                await session.execute(
                    update(ViewTask)
                    .where(ViewTask.id == task.id)
                    .values(status="completed")
                )

            await session.commit()

        except Exception as e:
            print(f"[💥] Ошибка при выполнении задачи: {e}", flush=True)

def start_scheduler():
    print("🕒 Запуск планировщика задач", flush=True)
    scheduler.add_job(check_and_view_stories, "interval", minutes=1)
    scheduler.start()

async def main_loop():
    print("✅ main_loop started", flush=True)
    start_scheduler()
    while True:
        await asyncio.sleep(60)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main_loop())
