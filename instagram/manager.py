from db.models import ViewSession
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
import datetime

async def complete_session(session: AsyncSession, session_id: int):
    await session.execute(
        update(ViewSession)
        .where(ViewSession.id == session_id)
        .values(is_active=False, ended_at=datetime.datetime.utcnow())
    )
    await session.commit()
    print(f"📁 Сессия {session_id} завершена и обновлена.")
