import os
import sys
from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from alembic import context

# Добавляем путь к проекту
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Загружаем переменные окружения без BOM (если есть)
from dotenv import load_dotenv

with open(".env", "r", encoding="utf-8-sig") as f:
    content = f.read()
with open(".env", "w", encoding="utf-8") as f:
    f.write(content)

load_dotenv(override=True)

# Импорт базы
from db.models import Base

# Настройка логирования
fileConfig(context.config.config_file_name)
target_metadata = Base.metadata

# Подключение к БД (с заменой asyncpg → psycopg2 для Alembic)
raw_url = os.getenv("DATABASE_URL", "")
if not raw_url:
    raise RuntimeError("DATABASE_URL не задан!")

sync_url = raw_url.replace("+asyncpg", "+psycopg2")

print("⛓ Подключение через URL:", repr(sync_url))
print("⛓ HEX:", sync_url.encode("utf-8").hex())

def run_migrations_offline():
    context.configure(
        url=sync_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    engine = create_engine(sync_url, poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
