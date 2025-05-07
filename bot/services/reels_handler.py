from db.models import ScheduledPost
from datetime import datetime, timedelta

async def schedule_reels_to_stories(reels_url: str, telegram_id: int, instagram_logins: list[str]):
    from db.database import async_session
    async with async_session() as session:
        now = datetime.utcnow()
        for idx, login in enumerate(instagram_logins):
            post_time = now + timedelta(minutes=idx * 2)
            post = ScheduledPost(
                reels_url=reels_url,
                telegram_id=telegram_id,
                instagram_login=login,
                scheduled_time=post_time
            )
            session.add(post)
        await session.commit()
