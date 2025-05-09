# Используем минимальный Python-образ
FROM python:3.11-slim

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libxss1 \
    libasound2 \
    libxtst6 \
    libxrandr2 \
    libgtk-3-0 \
    && apt-get clean

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости и проект
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Указываем переменные окружения
ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL="postgresql+asyncpg://botuser:botpass@postgres:5432/botdb"
# Стартовая команда — FastAPI или aiogram запуск (пример)
CMD ["python", "-m", "bot.main"]
