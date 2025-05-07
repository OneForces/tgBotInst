from sqlalchemy import Column, Integer, String, DateTime, func, BigInteger, Boolean
from db.database import Base
from datetime import datetime


class UserSubmission(Base):
    __tablename__ = "user_submissions"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, nullable=False)
    instagram_link = Column(String, nullable=False)
    telegram_link = Column(String, nullable=False)
    reels_link = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class InstagramAccount(Base):
    __tablename__ = "instagram_accounts"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # в реальности шифруется!
    proxy = Column(String, nullable=True)
    added_at = Column(DateTime(timezone=True), server_default=func.now())

class ReelsTask(Base):
    __tablename__ = "reels_tasks"

    id = Column(Integer, primary_key=True)
    reels_url = Column(String, nullable=False)
    post_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, default="pending")  # pending / posted

class StoryViewLog(Base):
    __tablename__ = "story_view_logs"

    id = Column(Integer, primary_key=True)
    viewer_telegram_id = Column(Integer, nullable=False)
    target_username = Column(String, nullable=False)
    status = Column(String, nullable=False)  # 'viewed' / 'failed'
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class ScheduledPost(Base):
    __tablename__ = "scheduled_posts"

    id = Column(Integer, primary_key=True)
    reels_url = Column(String, nullable=False)
    telegram_id = Column(BigInteger, nullable=False)
    instagram_login = Column(String, nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    is_posted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
