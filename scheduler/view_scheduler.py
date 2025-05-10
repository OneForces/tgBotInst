import asyncio
from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError

from db.database import async_session
from db.models import ViewTask, ViewResult
from scheduler.appium_control import view_stories


async def check_and_view_stories():
    print("[🔁] Старт check_and_view_stories")
    from scheduler.appium_control import view_stories  # импорт внутрь для отлова ошибок

    async with async_session() as session:
        try:
            result = await session.execute(
                select(ViewTask).where(ViewTask.status == "scheduled")
            )
            tasks = result.scalars().all()
            print(f"[👀] Найдено задач для просмотра: {len(tasks)}")
            if not tasks:
                print("[ℹ️] Нет задач для выполнения.")

            for task in tasks:
                profiles = [p.strip() for p in task.target_profiles.split(",") if p.strip()]
                print(f"[📦] Обработка задачи {task.id}: {profiles}")
                for profile in profiles:
                    try:
                        viewer = "viewer_account_1"
                        # success = await view_stories(profile, viewer)
                        await asyncio.sleep(1)
                        success = True

                        session.add(ViewResult(
                            view_task_id=task.id,
                            profile_viewed=profile,
                            viewer_account=viewer,
                            success=success,
                            timestamp=datetime.utcnow()
                        ))
                        print(f"[✅] Просмотрено: {profile} → {success}")
                    except Exception as e:
                        print(f"[💥] Ошибка при просмотре {profile}: {e}")

                await session.execute(
                    update(ViewTask)
                    .where(ViewTask.id == task.id)
                    .values(status="completed")
                )

            await session.commit()

        except SQLAlchemyError as e:
            print(f"[💥] Ошибка SQLAlchemy: {e}")
            await session.rollback()