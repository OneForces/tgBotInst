# run_scheduler.py
import asyncio
from scheduler.cron_jobs import start_scheduler

async def main():
    start_scheduler()
    print("[✅] Планировщик запущен.")
    while True:
        await asyncio.sleep(3600)  # чтобы процесс не завершался

if __name__ == "__main__":
    asyncio.run(main())
