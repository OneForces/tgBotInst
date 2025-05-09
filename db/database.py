from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from config.config import DATABASE_URL  # Импорт из config

# Создание асинхронного движка
async_engine = create_async_engine(DATABASE_URL, echo=False)

# Фабрика сессий
async_session = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

# Базовая модель для всех ORM-классов
Base = declarative_base()
