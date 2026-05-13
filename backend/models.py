from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    total_xp = Column(Integer, default=0)
    current_level = Column(Integer, default=1)
    streak_days = Column(Integer, default=0)
    last_active_date = Column(DateTime, default=datetime.utcnow)

    progress = relationship("UserTasksProgress", back_populates="user")


class Level(Base):
    __tablename__ = "levels"

    id = Column(Integer, primary_key=True, index=True)
    order_index = Column(Integer, unique=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)

    tasks = relationship("Task", back_populates="level")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    level_id = Column(Integer, ForeignKey("levels.id"), nullable=False)
    type = Column(String, nullable=False) # 'choice', 'translate', 'scenario'
    question = Column(String, nullable=False)
    correct_answer = Column(String) # nullable for scenario
    image_url = Column(String)
    metadata_json = Column(JSON) # e.g. for choice options

    level = relationship("Level", back_populates="tasks")
    progress = relationship("UserTasksProgress", back_populates="task")


class UserTasksProgress(Base):
    __tablename__ = "user_tasks_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    is_completed = Column(Boolean, default=False)
    attempts_count = Column(Integer, default=0)
    stars_earned = Column(Integer, default=0) # for scenario
    last_attempt_date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="progress")
    task = relationship("Task", back_populates="progress")
