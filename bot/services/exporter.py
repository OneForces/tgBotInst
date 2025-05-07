import os
import pandas as pd
from sqlalchemy import select, desc
from db.database import async_session
from db.models import StoryViewLog
from datetime import datetime

EXPORT_FOLDER = "exports"
os.makedirs(EXPORT_FOLDER, exist_ok=True)

async def export_logs_to_excel():
    async with async_session() as session:
        query = select(StoryViewLog).order_by(desc(StoryViewLog.timestamp)).limit(1000)
        result = await session.execute(query)
        logs = result.scalars().all()

    if not logs:
        return None

    data = [{
        "Дата": log.timestamp.strftime('%Y-%m-%d %H:%M'),
        "Telegram ID": log.viewer_telegram_id,
        "Username": log.target_username,
        "Статус": "Просмотрено" if log.status == "viewed" else "Не просмотрено"
    } for log in logs]

    df = pd.DataFrame(data)
    file_path = os.path.join(EXPORT_FOLDER, "logs_export.xlsx")
    df.to_excel(file_path, index=False)
    return file_path
