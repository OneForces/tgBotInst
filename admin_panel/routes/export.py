from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse, FileResponse
from sqlalchemy import select, desc, and_
from datetime import datetime
from typing import Optional
import pandas as pd
from fpdf import FPDF
import os

from db.database import async_session
from db.models import StoryViewLog

router = APIRouter(prefix="/export")

EXPORT_FOLDER = "admin_panel/exports"
os.makedirs(EXPORT_FOLDER, exist_ok=True)

@router.get("/excel")
async def export_excel(
    telegram_id: Optional[str] = Query(default=None),
    date: Optional[str] = Query(default=None)
):
    logs = await get_filtered_logs(telegram_id, date)
    if not logs:
        return HTMLResponse("<h3>Нет данных для экспорта</h3>", status_code=404)

    data = [{
        "Дата": log.timestamp.strftime('%Y-%m-%d %H:%M'),
        "Telegram ID": log.viewer_telegram_id,
        "Username": log.target_username,
        "Статус": "Просмотрено" if log.status == "viewed" else "Не просмотрено"
    } for log in logs]

    df = pd.DataFrame(data)
    file_path = os.path.join(EXPORT_FOLDER, "logs_export.xlsx")
    df.to_excel(file_path, index=False)

    return FileResponse(
        file_path,
        filename="logs_export.xlsx",
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@router.get("/pdf")
async def export_pdf(
    telegram_id: Optional[str] = Query(default=None),
    date: Optional[str] = Query(default=None)
):
    logs = await get_filtered_logs(telegram_id, date)
    if not logs:
        return HTMLResponse("<h3>Нет данных для экспорта</h3>", status_code=404)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Отчёт по логам", ln=True, align='C')
    pdf.ln(10)

    for log in logs:
        line = f"{log.timestamp.strftime('%Y-%m-%d %H:%M')} — {log.viewer_telegram_id} — {log.target_username} — {'Просмотрено' if log.status == 'viewed' else 'Не просмотрено'}"
        pdf.cell(200, 10, txt=line, ln=True)

    file_path = os.path.join(EXPORT_FOLDER, "logs_export.pdf")
    pdf.output(file_path)

    return FileResponse(
        file_path,
        filename="logs_export.pdf",
        media_type='application/pdf'
    )

async def get_filtered_logs(telegram_id=None, date=None):
    async with async_session() as session:
        query = select(StoryViewLog)

        if telegram_id and telegram_id.isdigit():
            query = query.where(StoryViewLog.viewer_telegram_id == int(telegram_id))

        if date:
            try:
                dt = datetime.strptime(date, "%Y-%m-%d")
                dt_end = dt.replace(hour=23, minute=59, second=59)
                query = query.where(
                    and_(
                        StoryViewLog.timestamp >= dt,
                        StoryViewLog.timestamp <= dt_end
                    )
                )
            except Exception:
                return []

        query = query.order_by(desc(StoryViewLog.timestamp)).limit(1000)
        result = await session.execute(query)
        return result.scalars().all()
