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
    reels_url = Column(String, nullable=False)
    post_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, default="pending")  # pending / posted
    instagram_login = Column(String, nullable=True)
    instagram_password = Column(String, nullable=True)

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
    subscriber_id = Column(Integer, ForeignKey("subscribers.id"))  # кто запустил просмотр
    target_profile = Column(String, nullable=False)               # чей сторис смотреть
    scheduled_time = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="created")                   # created/in_progress/completed/error
    results = relationship("ViewResult", back_populates="task")

class ViewResult(Base):
    __tablename__ = "view_results"
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("view_tasks.id"))
    account = Column(String, nullable=False)   # аккаунт, с которого смотрели
    success = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    task = relationship("ViewTask", back_populates="results")

class Subscriber(Base):
    __tablename__ = "subscribers"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    instagram_login = Column(String, nullable=False)
    instagram_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
