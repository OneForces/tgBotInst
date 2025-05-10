FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь admin_panel + нужные внешние зависимости
COPY . .
COPY ../scheduler ./scheduler
COPY ../config ./config
COPY ../db ./db
COPY ../bot ./bot

# Запуск Uvicorn
CMD ["uvicorn", "admin_panel.main:app", "--host", "0.0.0.0", "--port", "8000"]
