from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy import BigInteger

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
    appium_url = Column(String, default="http://appium1:4723")

class ReelsTask(Base):
    __tablename__ = "reels_tasks"

    id = Column(Integer, primary_key=True)
    subscriber_id = Column(Integer, ForeignKey("subscribers.id"))
    reels_url = Column(String, nullable=False)
    post_time = Column(DateTime, nullable=False)
    status = Column(String, default="scheduled")

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
    status = Column(String, default="pending")
    instagram_password = Column(String, nullable=False)


class ViewSession(Base):
    __tablename__ = "view_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)  # Telegram ID
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

class ViewTask(Base):
    __tablename__ = "view_tasks"

    id = Column(Integer, primary_key=True)
    subscriber_id = Column(Integer, ForeignKey("subscribers.id"))
    target_profiles = Column(String)
    scheduled_time = Column(DateTime)
    status = Column(String)

    results = relationship("ViewResult", back_populates="view_task")

class ViewResult(Base):
    __tablename__ = "view_results"

    id = Column(Integer, primary_key=True)
    view_task_id = Column(Integer, ForeignKey("view_tasks.id"))
    profile_viewed = Column(String)
    viewer_account = Column(String)
    success = Column(Boolean)
    timestamp = Column(DateTime)

    view_task = relationship("ViewTask", back_populates="results")  # ⬅ вот это

class Subscriber(Base):
    __tablename__ = "subscribers"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    instagram_login = Column(String, nullable=False)
    instagram_password = Column(String, nullable=False)