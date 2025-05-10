import asyncio
from scheduler.cron_jobs import start_scheduler
from scheduler.view_scheduler import check_and_view_stories

async def view_scheduler_loop():
    while True:
        print("[⏱] Запуск планировщика просмотров Stories...")
        await check_and_view_stories()
        await asyncio.sleep(60)

async def main():
    # Запуск Reels-планировщика (apscheduler)
    start_scheduler()
    print("[✅] Планировщик Reels запущен.")

    # Запуск цикла автопросмотра Stories
    await view_scheduler_loop()

if __name__ == "__main__":
    asyncio.run(main())
