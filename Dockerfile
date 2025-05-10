# Используем минимальный Python-образ
FROM python:3.11-slim

# Устанавливаем зависимости системы (нужны для Appium/Android взаимодействия)
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

# Рабочая директория
WORKDIR /app

# Зависимости Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV DATABASE_URL="postgresql+asyncpg://botuser:botpass@postgres:5432/botdb"

# Команда запуска (aiogram бот)
CMD ["python", "-m", "bot.main"]
