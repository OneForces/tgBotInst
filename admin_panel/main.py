from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, desc
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from scheduler.cron_jobs import run_story_publisher
from db.database import async_session
from db.models import StoryViewLog
from admin_panel.routes.export import router as export_router


app = FastAPI()
templates = Jinja2Templates(directory="admin_panel/templates")

app.include_router(export_router)
run_story_publisher()

# 🔁 Планировщик запускается при старте приложения
@app.on_event("startup")
async def on_startup():
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(run_story_publisher, "interval", minutes=1)
    scheduler.start()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    async with async_session() as session:
        result = await session.execute(
            select(StoryViewLog).order_by(desc(StoryViewLog.timestamp)).limit(1000)
        )
        logs = result.scalars().all()

    return templates.TemplateResponse("logs.html", {
        "request": request,
        "logs": logs,
        "telegram_id": None,
        "date": None
    })
