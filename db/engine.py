import os
from dotenv import load_dotenv

# Явно указать путь к .env в корне проекта
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=env_path)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set!")

async_engine = create_async_engine(DATABASE_URL, echo=True, future=True)
async_session = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)
