import asyncio
from scheduler.cron_jobs import start_scheduler  # если используешь отдельную логику

async def main():
    start_scheduler()
    print("[✅] Планировщик просмотров запущен.")
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
