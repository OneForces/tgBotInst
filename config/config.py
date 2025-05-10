import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://botuser:botpass@postgres:5432/botdb")
ADMIN_ID = list(map(int, os.getenv("ADMIN_ID", "").split(",")))
print(f"BOT_TOKEN: {BOT_TOKEN}")
print(f"DATABASE_URL: {DATABASE_URL}")
