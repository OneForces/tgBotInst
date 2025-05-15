import os
from pathlib import Path
from dotenv import load_dotenv

# 🔁 Загрузка .env с перезаписью существующих переменных окружения
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# ✅ Переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./fallback.db")
ADMIN_ID = list(map(int, os.getenv("ADMIN_ID", "").split(",")))

# 🔎 Отладочная печать
print(f"[config] BOT_TOKEN: {BOT_TOKEN}")
print(f"[config] DATABASE_URL: {DATABASE_URL}")
print(f"[config] ADMIN_ID: {ADMIN_ID}")
