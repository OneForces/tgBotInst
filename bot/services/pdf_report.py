from db.engine import async_session
from db.models import StoryViewLog
from sqlalchemy import select
from datetime import datetime
from fpdf import FPDF
import os

EXPORT_FOLDER = "exports/"
os.makedirs(EXPORT_FOLDER, exist_ok=True)

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Отчёт о просмотрах сторис", ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Страница {self.page_no()}", align="C")

async def export_user_report_pdf(user_id: int) -> str:
    async with async_session() as session:
        result = await session.execute(
            select(StoryViewLog)
            .where(StoryViewLog.viewer_telegram_id == user_id)
            .order_by(StoryViewLog.timestamp.desc())
        )
        logs = result.scalars().all()

    if not logs:
        return None

    username = f"user_{user_id}"
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for log in logs:
        status = "✅ Просмотрено" if log.status == "viewed" else "❌ Не просмотрено"
        line = f"{log.timestamp.strftime('%Y-%m-%d %H:%M')} — {log.target_username} — {status}"
        pdf.cell(0, 10, line, ln=True)

    filename = f"{EXPORT_FOLDER}report_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    return filename
